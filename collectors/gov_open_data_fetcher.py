# 匯入 os，用來掃描快取檔案
import os

# 匯入 shutil，用來複製手動資料或範例資料
import shutil

# 匯入專案設定
from config import (
    USE_MOL_DYNAMIC_FETCH,
    USE_CACHED_MOL_FILES,
    USE_SAMPLE_FALLBACK,
    DOWNLOADED_RAW_DIR,
    SAMPLE_DATA_PATH,
    MOL_LOCAL_DATA_PATH,
)

# 匯入勞動部動態下載函式
from collectors.mol_dynamic_fetcher import download_mol_dynamic_data


# 判斷檔案是否為可讀取的資料檔
def is_data_file(filename):
    # 轉小寫方便判斷副檔名
    lower_name = filename.lower()

    # 支援 CSV、Excel、ODS
    return lower_name.endswith((".csv", ".xlsx", ".xls", ".ods"))


# 找出上次成功下載的勞動部資料
def find_cached_mol_files():
    # 儲存快取檔案
    cached_files = []

    # 如果資料夾不存在，直接回傳空列表
    if not os.path.exists(DOWNLOADED_RAW_DIR):
        return cached_files

    # 走訪 downloaded 資料夾
    for root, dirs, files in os.walk(DOWNLOADED_RAW_DIR):
        for filename in files:
            # 排除 sample 範例資料
            if "sample" in filename.lower():
                continue

            # 只保留資料檔
            if is_data_file(filename):
                cached_files.append({
                    "source_name": "勞動部快取資料",
                    "file_path": os.path.join(root, filename),
                })

    # 回傳快取檔案列表
    return cached_files


# 取得系統資料來源
def download_all_sources():
    # 第一優先：啟動時動態下載勞動部資料
    if USE_MOL_DYNAMIC_FETCH:
        try:
            # 嘗試從勞動部網站動態下載資料
            mol_files = download_mol_dynamic_data()

            # 如果有成功下載，直接使用本次下載資料
            if mol_files:
                print("本次啟動已成功使用勞動部動態下載資料。", flush=True)
                return mol_files

        except Exception as error:
            # 動態下載失敗後，改用快取或其他備援
            print(f"勞動部動態下載失敗，改用備援資料：{error}", flush=True)

    # 第二優先：使用上次成功下載的勞動部資料
    if USE_CACHED_MOL_FILES:
        # 尋找快取檔
        cached_files = find_cached_mol_files()

        # 如果有快取檔，就回傳
        if cached_files:
            print("本次啟動使用上次成功下載的勞動部快取資料。", flush=True)
            return cached_files

    # 第三優先：使用手動下載的勞動部 CSV
    if os.path.exists(MOL_LOCAL_DATA_PATH):
        # 建立複製後路徑
        output_path = os.path.join(DOWNLOADED_RAW_DIR, "mol_labor_violations.csv")

        # 複製手動下載資料
        shutil.copyfile(MOL_LOCAL_DATA_PATH, output_path)

        # 回傳手動資料來源
        return [{
            "source_name": "勞動部手動下載資料",
            "file_path": output_path,
        }]

    # 第四優先：使用內建範例資料
    if USE_SAMPLE_FALLBACK and os.path.exists(SAMPLE_DATA_PATH):
        # 建立範例資料複製路徑
        output_path = os.path.join(DOWNLOADED_RAW_DIR, "sample_labor_violations.csv")

        # 複製範例資料
        shutil.copyfile(SAMPLE_DATA_PATH, output_path)

        # 印出提醒
        print("警告：目前使用內建範例資料。", flush=True)

        # 回傳範例資料來源
        return [{
            "source_name": "內建範例資料",
            "file_path": output_path,
        }]

    # 如果完全沒有資料來源，丟出錯誤
    raise FileNotFoundError("找不到可使用的資料來源。")