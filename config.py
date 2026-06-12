# 匯入 os，用來建立跨平台路徑
import os


# 專案根目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 原始資料資料夾
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# 處理後資料資料夾
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# 內建範例資料路徑
SAMPLE_DATA_PATH = os.path.join(RAW_DATA_DIR, "sample_labor_violations.csv")

# 手動下載的勞動部 CSV 資料路徑
MOL_LOCAL_DATA_PATH = os.path.join(RAW_DATA_DIR, "mol_labor_violations.csv")

# 政府資料下載後暫存資料夾
DOWNLOADED_RAW_DIR = os.path.join(RAW_DATA_DIR, "downloaded")

# 分析後輸出的統一 CSV
ANALYZED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "analyzed_labor_violations.csv")


# 建立必要資料夾，避免第一次執行找不到路徑
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(DOWNLOADED_RAW_DIR, exist_ok=True)


# 政府公開資料來源清單
# 你之後可以把政府資料開放平台的 CSV / XLSX / ODS 下載連結放進來
# 第一版先留空，系統會自動使用 sample_labor_violations.csv
DATA_SOURCES = [
    # 範例格式：
    # {
    #     "name": "臺北市違反勞動法令資料",
    #     "url": "https://example.gov.tw/labor.csv"
    # },
    # {
    #     "name": "嘉義市違反勞動基準法業者名單",
    #     "url": "https://example.gov.tw/chiayi.csv"
    # },
]

# 是否啟用勞動部動態下載
# True：網站啟動時自動下載勞動部資料
# False：不自動下載，改用本地 CSV 或範例資料
USE_MOL_DYNAMIC_FETCH = True

# 系統統一欄位名稱
STANDARD_COLUMNS = [
    "source_name",
    "city",
    "authority",
    "company_name",
    "responsible_person",
    "announce_date",
    "penalty_date",
    "violated_law",
    "violation_content",
    "penalty_amount",
    "note",
    "violation_category",
]


# 違規類型分類規則
# 這裡使用規則式關鍵字分類，避免誇大成 AI 判斷
CATEGORY_RULES = {
    "工時問題": [
        "延長工時",
        "工時",
        "出勤紀錄",
        "正常工時",
        "休息時間",
        "超時工作",
        "工作時間",
    ],
    "薪資／加班費問題": [
        "工資",
        "加班費",
        "未全額給付",
        "工資清冊",
        "最低工資",
        "延長工作時間工資",
        "薪資",
    ],
    "休假問題": [
        "例假",
        "休息日",
        "特別休假",
        "國定假日",
        "未給假",
        "假日",
    ],
    "勞退／保險問題": [
        "勞工退休金",
        "提繳",
        "退休金",
        "就業保險",
        "勞保",
    ],
    "職業安全問題": [
        "職業安全",
        "職業安全衛生",
        "職災",
        "安全衛生",
        "防護",
        "危害",
    ],
    "職場平等問題": [
        "性別平等",
        "就業歧視",
        "育嬰留職停薪",
        "性騷擾",
        "平等",
    ],
}