# 匯入 os，用來處理檔案與資料夾路徑
import os

# 匯入 re，用來從 HTML 中抓取 csrf token
import re

# 匯入 time，用來在連續請求間稍微暫停
import time

# 匯入 shutil，用來清理資料夾
import shutil

# 匯入 zipfile，用來解壓縮勞動部下載的 zip
import zipfile

# 匯入 requests，用來連線勞動部網站
import requests

# 匯入下載資料夾與縣市代碼設定
from config import DOWNLOADED_RAW_DIR, MOL_CITY_CODES


# 勞動部違反勞動法令事業單位查詢系統首頁
MOL_HOME_URL = "https://announcement.mol.gov.tw/"

# 勞動部下載資料的 POST 端點
MOL_DOWNLOAD_URL = "https://announcement.mol.gov.tw/Download/"


# 建立請求標頭，讓 requests 看起來像一般瀏覽器
def build_headers():
    # 回傳瀏覽器常見 headers
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://announcement.mol.gov.tw",
        "Referer": "https://announcement.mol.gov.tw/",
    }


# 重設資料夾，避免舊檔案混入本次下載結果
def reset_folder(folder_path):
    # 如果資料夾已存在，就先刪除
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    # 重新建立空資料夾
    os.makedirs(folder_path, exist_ok=True)


# 從勞動部首頁 HTML 抓取 _csrf_token
def fetch_csrf_token(session):
    # 先進入首頁，取得 session cookie 與表單 HTML
    response = session.get(
        MOL_HOME_URL,
        headers=build_headers(),
        timeout=30,
    )

    # 若 HTTP 狀態碼錯誤，直接丟出例外
    response.raise_for_status()

    # 取得 HTML 內容
    html = response.text

    # 可能出現的 csrf token 格式
    patterns = [
        r'name="_csrf_token"\s+value="([^"]+)"',
        r'value="([^"]+)"\s+name="_csrf_token"',
        r'_csrf_token[^>]+value="([^"]+)"',
    ]

    # 逐一用正規表示式抓 token
    for pattern in patterns:
        match = re.search(pattern, html)

        # 如果抓到 token，就回傳
        if match:
            return match.group(1)

    # 如果全部抓不到，代表網站表單可能改版
    raise ValueError("找不到 _csrf_token，可能是勞動部網站表單格式改變。")


# 建立勞動部下載表單
def build_download_form(csrf_token, city_code):
    # 這些欄位是根據瀏覽器 Network 中 /Download/ 的 Payload 整理
    # requests 使用 files=(None, value) 可以送出 multipart/form-data
    return {
        "_csrf_token": (None, csrf_token),
        "CITYNO": (None, city_code),
        "UNITNAME": (None, ""),
        "DOCstartDate": (None, ""),
        "DOCEndDate": (None, ""),
        "REGNUMBER": (None, ""),
        "REGNO": (None, ""),
        "downloadType": (None, "3"),
        "sortName3": (None, ""),
        "sortName1": (None, ""),
        "sortName2": (None, ""),
        "Page3": (None, "1"),
        "Page1": (None, "1"),
        "Page2": (None, "1"),
    }


# 解壓縮 zip，回傳其中所有 CSV / Excel / ODS 資料檔案
def extract_zip_files(zip_path, extract_dir):
    # 清空並建立解壓縮資料夾
    reset_folder(extract_dir)

    # 解壓縮 zip
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(extract_dir)

    # 儲存找到的資料檔案
    data_files = []

    # 走訪解壓縮資料夾
    for root, dirs, files in os.walk(extract_dir):
        for filename in files:
            # 轉小寫方便判斷副檔名
            lower_name = filename.lower()

            # 只保留可讀資料檔
            if lower_name.endswith((".csv", ".xlsx", ".xls", ".ods")):
                data_files.append(os.path.join(root, filename))

    # 如果沒有找到資料檔，丟出錯誤
    if not data_files:
        raise FileNotFoundError("zip 解壓縮後找不到 CSV / Excel / ODS 檔案。")

    # 回傳資料檔列表
    return data_files


# 下載單一縣市資料
def download_single_city(city_name, city_code):
    # 每個縣市使用獨立 session，避免 token 或 cookie 互相干擾
    session = requests.Session()

    # 取得新的 csrf token
    csrf_token = fetch_csrf_token(session)

    # 建立下載表單
    form_data = build_download_form(csrf_token, city_code)

    # 送出 POST 請求下載 zip
    response = session.post(
        MOL_DOWNLOAD_URL,
        headers=build_headers(),
        files=form_data,
        timeout=120,
    )

    # 如果 HTTP 狀態碼錯誤，丟出例外
    response.raise_for_status()

    # 取得回傳內容類型
    content_type = response.headers.get("content-type", "")

    # 如果不是 zip，通常代表網站回傳錯誤頁或權限頁
    if "zip" not in content_type.lower():
        raise ValueError(
            f"{city_name} 回傳不是 zip，content-type={content_type}，可能是下載參數或權限問題。"
        )

    # 建立 zip 儲存路徑
    zip_path = os.path.join(DOWNLOADED_RAW_DIR, f"mol_{city_name}.zip")

    # 將 zip 寫入檔案
    with open(zip_path, "wb") as file:
        file.write(response.content)

    # 建立解壓縮資料夾
    extract_dir = os.path.join(DOWNLOADED_RAW_DIR, f"mol_{city_name}")

    # 解壓縮並取得資料檔案
    data_file_paths = extract_zip_files(zip_path, extract_dir)

    # 儲存結果
    results = []

    # 每個資料檔都建立一個資料來源紀錄
    for file_path in data_file_paths:
        results.append({
            "source_name": f"勞動部動態下載資料－{city_name}",
            "file_path": file_path,
        })

    # 回傳該縣市所有資料檔
    return results


# 動態下載勞動部資料
def download_mol_dynamic_data():
    # 儲存所有成功下載的資料檔
    downloaded_files = []

    # 逐一下載設定中的縣市
    for city_name, city_code in MOL_CITY_CODES.items():
        try:
            # 下載單一縣市資料
            city_results = download_single_city(city_name, city_code)

            # 加入成功結果
            downloaded_files.extend(city_results)

            # 印出成功訊息
            print(f"成功下載勞動部資料：{city_name}", flush=True)

            # 暫停一下，避免連續請求太快
            time.sleep(0.8)

        except Exception as error:
            # 單一縣市失敗不讓整個系統停止
            print(f"下載勞動部資料失敗：{city_name}，錯誤：{error}", flush=True)

    # 如果完全沒有成功下載，就丟錯讓外層使用備援資料
    if not downloaded_files:
        raise RuntimeError("勞動部動態下載全部失敗。")

    # 回傳成功下載的資料檔
    return downloaded_files