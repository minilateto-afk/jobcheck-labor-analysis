# 匯入 os，用來建立跨平台路徑
import os


# ================================
# 專案路徑設定
# ================================

# 專案根目錄，也就是目前 config.py 所在的資料夾
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 原始資料資料夾，放 sample 或手動下載的 CSV
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# 勞動部動態下載後的資料資料夾
DOWNLOADED_RAW_DIR = os.path.join(RAW_DATA_DIR, "downloaded")

# 處理後資料資料夾
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# 範例資料路徑，只有在官方資料抓不到時才使用
SAMPLE_DATA_PATH = os.path.join(RAW_DATA_DIR, "sample_labor_violations.csv")

# 手動下載的勞動部 CSV 備援路徑
MOL_LOCAL_DATA_PATH = os.path.join(RAW_DATA_DIR, "mol_labor_violations.csv")

# 系統分析後輸出的統一 CSV
ANALYZED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "analyzed_labor_violations.csv")


# ================================
# 啟動資料設定
# ================================

# 是否在網站啟動時自動嘗試下載勞動部資料
USE_MOL_DYNAMIC_FETCH = True

# 若動態下載失敗，是否允許使用上次成功下載的勞動部資料
USE_CACHED_MOL_FILES = True

# 若官方資料與快取都失敗，是否允許使用範例資料
USE_SAMPLE_FALLBACK = True


# ================================
# 勞動部縣市代碼設定
# ================================

# 這些代碼是勞動部查詢系統 POST 表單中的 CITYNO
# 第一版先抓六都，資料量足夠，也比較適合作品展示
MOL_CITY_CODES = {
    "臺北市": "63",
    "新北市": "65",
    "桃園市": "68",
    "臺中市": "66",
    "臺南市": "67",
    "高雄市": "64",
}


# ================================
# 系統標準欄位
# ================================

# 不同來源的欄位最後都會整理成這些欄位
STANDARD_COLUMNS = [
    "source_name",          # 資料來源名稱
    "city",                 # 縣市或主管機關
    "authority",            # 主管機關
    "company_name",         # 事業單位名稱
    "responsible_person",   # 負責人
    "announce_date",        # 公告日期
    "penalty_date",         # 處分日期
    "violated_law",         # 違反法規條款
    "violation_content",    # 法條敘述或違規內容
    "penalty_amount",       # 處分金額
    "note",                 # 備註
    "violation_category",   # 系統分類後的違規類型
]


# ================================
# 違規類型分類規則
# ================================

# 系統會依照違反法規條款與法條敘述中的關鍵字分類
CATEGORY_RULES = {
    "工時問題": [
        "延長工時",
        "工時",
        "工作時間",
        "出勤紀錄",
        "休息時間",
        "超時",
        "第30條",
        "第32條",
        "第36條",
    ],
    "薪資／加班費問題": [
        "工資",
        "加班費",
        "延長工作時間工資",
        "未全額給付",
        "最低工資",
        "薪資",
        "第22條",
        "第24條",
    ],
    "休假問題": [
        "例假",
        "休息日",
        "特別休假",
        "國定假日",
        "未給假",
        "休假",
        "第38條",
        "第39條",
    ],
    "職業安全問題": [
        "職業安全",
        "職業安全衛生",
        "安全衛生",
        "職災",
        "防護",
        "危害",
        "職安",
    ],
    "勞退／保險問題": [
        "勞工退休金",
        "退休金",
        "提繳",
        "勞保",
        "就業保險",
    ],
    "職場平等問題": [
        "性別平等",
        "就業歧視",
        "育嬰留職停薪",
        "性騷擾",
        "平等",
    ],
}


# ================================
# 建立必要資料夾
# ================================

# 建立原始資料資料夾
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# 建立動態下載資料資料夾
os.makedirs(DOWNLOADED_RAW_DIR, exist_ok=True)

# 建立處理後資料資料夾
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)