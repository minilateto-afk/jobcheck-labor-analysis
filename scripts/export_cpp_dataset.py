# 匯入 pathlib，用來處理跨系統檔案路徑
from pathlib import Path

# 匯入 re，用來清理金額字串中的非數字內容
import re

# 匯入 pandas，用來讀取與輸出 CSV
import pandas as pd


# 設定專案根目錄，parents[1] 代表 scripts/ 的上一層，也就是專案根目錄
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 設定 Python 已清理完成的資料來源
INPUT_CSV = PROJECT_ROOT / "data" / "processed" / "analyzed_labor_violations.csv"

# 設定 C++ Core 要使用的輸出資料夾
OUTPUT_DIR = PROJECT_ROOT / "data" / "cpp"

# 設定 C++ Core 要讀取的精簡 CSV 檔案
OUTPUT_CSV = OUTPUT_DIR / "labor_records_cpp.csv"


def normalize_text(value: object) -> str:
    # 將空值轉成空字串，避免輸出 nan
    if pd.isna(value):
        return ""

    # 將資料轉成字串
    text = str(value)

    # 移除前後空白
    text = text.strip()

    # 將換行與 tab 轉成空白，避免 C++ 讀取 CSV 時格式混亂
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # 回傳清理後文字
    return text


def normalize_money(value: object) -> int:
    # 如果是空值，金額視為 0
    if pd.isna(value):
        return 0

    # 將資料轉成字串
    text = str(value)

    # 移除逗號，例如 60,000 變成 60000
    text = text.replace(",", "")

    # 只保留數字，避免出現「新臺幣60000元」造成 C++ 解析失敗
    digits = re.sub(r"[^0-9]", "", text)

    # 如果沒有任何數字，回傳 0
    if digits == "":
        return 0

    # 將數字字串轉成整數
    return int(digits)


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    # 定義 C++ Core 需要的欄位
    required_columns = [
        "company_name",
        "city",
        "announce_date",
        "penalty_date",
        "violated_law",
        "violation_category",
        "penalty_amount",
    ]

    # 檢查每個必要欄位是否存在
    for column in required_columns:
        # 如果原始資料沒有這個欄位，就建立空欄位，避免程式直接錯誤
        if column not in df.columns:
            df[column] = ""

    # 只保留 C++ Core 需要的欄位，讓 C++ 讀取時更簡單
    return df[required_columns].copy()


def export_cpp_dataset() -> None:
    # 檢查 Python 已處理資料是否存在
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"找不到輸入資料：{INPUT_CSV}")

    # 建立 data/cpp 資料夾，如果已存在就不會報錯
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 讀取 Python 已整理完成的資料
    df = pd.read_csv(INPUT_CSV)

    # 只保留 C++ Core 需要的欄位
    cpp_df = ensure_columns(df)

    # 清理公司名稱
    cpp_df["company_name"] = cpp_df["company_name"].apply(normalize_text)

    # 清理縣市欄位
    cpp_df["city"] = cpp_df["city"].apply(normalize_text)

    # 清理公告日期
    cpp_df["announce_date"] = cpp_df["announce_date"].apply(normalize_text)

    # 清理處分日期
    cpp_df["penalty_date"] = cpp_df["penalty_date"].apply(normalize_text)

    # 清理違反法規欄位
    cpp_df["violated_law"] = cpp_df["violated_law"].apply(normalize_text)

    # 清理違規分類欄位
    cpp_df["violation_category"] = cpp_df["violation_category"].apply(normalize_text)

    # 將處分金額轉成整數，方便 C++ 排序與統計
    cpp_df["penalty_amount"] = cpp_df["penalty_amount"].apply(normalize_money)

    # 移除公司名稱空白的資料，避免查詢時出現空名稱
    cpp_df = cpp_df[cpp_df["company_name"] != ""]

    # 依公司名稱、公告日期、法規與金額去重，降低重複公告造成的干擾
    cpp_df = cpp_df.drop_duplicates(
        subset=["company_name", "announce_date", "violated_law", "penalty_amount"]
    )

    # 輸出成 UTF-8 with BOM，方便 Excel 開啟，也讓 C++ 可以正常讀取中文
    cpp_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    # 印出輸出結果，方便確認
    print("C++ Core 資料匯出完成")
    print(f"輸入資料：{INPUT_CSV}")
    print(f"輸出資料：{OUTPUT_CSV}")
    print(f"輸出筆數：{len(cpp_df)}")


# 如果直接執行這個檔案，就匯出 C++ 資料
if __name__ == "__main__":
    export_cpp_dataset()