# 匯入 os，用來處理檔案路徑
import os

# 匯入 re，用來從 HTML 中抓取 csrf token
import re

# 匯入 zipfile，用來解壓縮勞動部下載的 zip
import zipfile

# 匯入 requests，用來連線勞動部網站
import requests

# 匯入設定檔路徑
from config import DOWNLOADED_RAW_DIR


# 勞動部違反勞動法令事業單位查詢系統首頁
MOL_HOME_URL = "https://announcement.mol.gov.tw/"

# 勞動部下載端點
MOL_DOWNLOAD_URL = "https://announcement.mol.gov.tw/Download/"


# 六都代碼
# 先抓六都，資料量夠大，也比較適合作品展示
MOL_CITY_CODES = {
    "臺北市": "63",
    "新北市": "65",
    "桃園市": "68",
    "臺中市": "66",
    "臺南市": "67",
    "高雄市": "64",
}


# 建立瀏覽器 headers
def build_headers():
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


# 從首頁 HTML 抓取 csrf token
def fetch_csrf_token(session):
    response = session.get(
        MOL_HOME_URL,
        headers=build_headers(),
        timeout=30
    )

    response.raise_for_status()

    html = response.text

    # 第一種常見格式：name 在前、value 在後
    match = re.search(
        r'name="_csrf_token"\s+value="([^"]+)"',
        html
    )

    # 第二種常見格式：value 在前、name 在後
    if not match:
        match = re.search(
            r'value="([^"]+)"\s+name="_csrf_token"',
            html
        )

    # 第三種較寬鬆抓法
    if not match:
        match = re.search(
            r'_csrf_token[^>]+value="([^"]+)"',
            html
        )

    if not match:
        raise ValueError("找不到 _csrf_token，可能是勞動部網站表單格式改變。")

    return match.group(1)


# 建立勞動部下載表單
def build_download_form(csrf_token, city_code):
    # 這些欄位是根據你從 Network 複製出來的 cURL 整理
    # requests 的 files 寫法可以送 multipart/form-data
    return {
        "_csrf_token": (None, csrf_token),
        "CITYNO": (None, city_code),
        "UNITNAME": (None, ""),
        "DOCstartDate": (None, ""),
        "DOCEndDate": (None, ""),
        "REGNUMBER": (None, ""),
        "REGNO": (None, ""),
        # 你抓到 CSV 下載時是 downloadType=3
        "downloadType": (None, "3"),
        "sortName3": (None, ""),
        "sortName1": (None, ""),
        "sortName2": (None, ""),
        "Page3": (None, "1"),
        "Page1": (None, "1"),
        "Page2": (None, "1"),
    }


# 解壓縮 zip 並回傳資料檔路徑
def extract_zip_file(zip_path, extract_dir):
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(extract_dir)

    data_files = []

    for root, dirs, files in os.walk(extract_dir):
        for filename in files:
            lower_name = filename.lower()

            if lower_name.endswith((".csv", ".xlsx", ".xls", ".ods")):
                data_files.append(os.path.join(root, filename))

    if not data_files:
        raise FileNotFoundError("zip 解壓縮後找不到 CSV / Excel / ODS 檔案。")

    return data_files[0]


# 下載單一縣市資料
def download_single_city(city_name, city_code):
    # 每個縣市都建立自己的 session，避免 token 一次性失效
    session = requests.Session()

    # 抓新的 csrf token
    csrf_token = fetch_csrf_token(session)

    # 建立下載表單
    form_data = build_download_form(csrf_token, city_code)

    # 送出 POST 下載 zip
    response = session.post(
        MOL_DOWNLOAD_URL,
        headers=build_headers(),
        files=form_data,
        timeout=120
    )

    response.raise_for_status()

    content_type = response.headers.get("content-type", "")

    if "zip" not in content_type.lower():
        raise ValueError(
            f"{city_name} 回傳不是 zip，content-type={content_type}，可能是下載參數或權限問題。"
        )

    # 儲存 zip
    zip_path = os.path.join(DOWNLOADED_RAW_DIR, f"mol_{city_name}.zip")

    with open(zip_path, "wb") as file:
        file.write(response.content)

    # 解壓縮 zip
    extract_dir = os.path.join(DOWNLOADED_RAW_DIR, f"mol_{city_name}")
    data_file_path = extract_zip_file(zip_path, extract_dir)

    return {
        "source_name": f"勞動部動態下載資料－{city_name}",
        "file_path": data_file_path
    }


# 啟動時自動下載勞動部資料
def download_mol_dynamic_data():
    downloaded_files = []

    for city_name, city_code in MOL_CITY_CODES.items():
        try:
            result = download_single_city(city_name, city_code)
            downloaded_files.append(result)
            print(f"成功下載勞動部資料：{city_name}")

        except Exception as error:
            print(f"下載勞動部資料失敗：{city_name}，錯誤：{error}")

    if not downloaded_files:
        raise RuntimeError("勞動部動態下載全部失敗。")

    return downloaded_files