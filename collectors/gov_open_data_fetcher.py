# 匯入 os，用來處理檔案路徑
import os

# 匯入 shutil，用來複製資料
import shutil

# 匯入 requests，用來下載政府公開資料
import requests

# 匯入設定檔中的資料來源與路徑
from config import (
    DATA_SOURCES,
    DOWNLOADED_RAW_DIR,
    SAMPLE_DATA_PATH,
    MOL_LOCAL_DATA_PATH,
    USE_MOL_DYNAMIC_FETCH
)

# 匯入勞動部動態下載函式
from collectors.mol_dynamic_fetcher import download_mol_dynamic_data


# 依照 URL 推測副檔名
def guess_extension(url):
    lower_url = url.lower()

    if ".xlsx" in lower_url:
        return ".xlsx"

    if ".xls" in lower_url:
        return ".xls"

    if ".ods" in lower_url:
        return ".ods"

    return ".csv"


# 取得上一次成功下載的勞動部官方資料
def find_cached_mol_files():
    cached_files = []

    if not os.path.exists(DOWNLOADED_RAW_DIR):
        return cached_files

    for root, dirs, files in os.walk(DOWNLOADED_RAW_DIR):
        for filename in files:
            lower_name = filename.lower()

            if lower_name.endswith((".csv", ".xlsx", ".xls", ".ods")):
                # 排除範例資料
                if "sample" in lower_name:
                    continue

                file_path = os.path.join(root, filename)

                cached_files.append({
                    "source_name": "勞動部上次成功下載資料",
                    "file_path": file_path
                })

    return cached_files


# 下載單一政府資料檔案
def download_single_source(source, index):
    source_name = source.get("name", f"資料來源_{index}")
    url = source.get("url", "")

    if not url:
        return None

    extension = guess_extension(url)
    output_path = os.path.join(DOWNLOADED_RAW_DIR, f"source_{index}{extension}")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)

    return {
        "source_name": source_name,
        "file_path": output_path
    }


# 取得所有資料來源
def download_all_sources():
    # 第一優先：網站啟動時自動下載勞動部資料
    if USE_MOL_DYNAMIC_FETCH:
        try:
            mol_files = download_mol_dynamic_data()

            if mol_files:
                print("本次啟動已成功使用勞動部動態下載資料。")
                return mol_files

        except Exception as error:
            print(f"勞動部動態下載失敗，嘗試改用上次成功下載的官方資料：{error}")

    # 第二優先：使用上一次成功下載的勞動部官方資料
    cached_mol_files = find_cached_mol_files()

    if cached_mol_files:
        print("本次啟動使用上一次成功下載的勞動部官方資料。")
        return cached_mol_files

    # 第三優先：使用手動下載的勞動部 CSV
    if os.path.exists(MOL_LOCAL_DATA_PATH):
        mol_output_path = os.path.join(DOWNLOADED_RAW_DIR, "mol_labor_violations.csv")
        shutil.copyfile(MOL_LOCAL_DATA_PATH, mol_output_path)

        return [
            {
                "source_name": "勞動部手動下載 CSV",
                "file_path": mol_output_path
            }
        ]

    # 第四優先：如果 config.py 有設定 DATA_SOURCES，就下載政府資料
    downloaded_files = []

    if DATA_SOURCES:
        for index, source in enumerate(DATA_SOURCES, start=1):
            try:
                result = download_single_source(source, index)

                if result:
                    downloaded_files.append(result)

            except Exception as error:
                print(f"資料來源下載失敗：{source.get('name')}，錯誤：{error}")

        if downloaded_files:
            return downloaded_files

    # 第五優先：真的沒有官方資料時，才使用範例資料
    fallback_path = os.path.join(DOWNLOADED_RAW_DIR, "sample_labor_violations.csv")
    shutil.copyfile(SAMPLE_DATA_PATH, fallback_path)

    print("警告：目前沒有成功取得官方資料，暫時使用內建範例資料。")

    return [
        {
            "source_name": "內建範例資料",
            "file_path": fallback_path
        }
    ]