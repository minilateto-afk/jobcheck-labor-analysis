# 匯入 os，用來檢查檔案是否存在
import os

# 匯入 traceback，用來顯示完整錯誤
import traceback

# 匯入 pandas，用來處理資料
import pandas as pd

# 匯入設定
from config import ANALYZED_DATA_PATH, SAMPLE_DATA_PATH, STANDARD_COLUMNS

# 匯入資料來源取得函式
from collectors.gov_open_data_fetcher import download_all_sources

# 匯入資料讀取函式
from analysis.data_loader import read_data_file

# 匯入欄位標準化函式
from analysis.normalizer import normalize_columns

# 匯入資料清理函式
from analysis.cleaner import clean_and_classify


# 執行完整資料流程
def run_data_pipeline():
    # 印出流程開始
    print("開始執行資料流程...", flush=True)

    # 取得資料來源
    source_files = download_all_sources()

    # 儲存標準化後的 DataFrame
    normalized_list = []

    # 逐一處理資料來源
    for source in source_files:
        # 取得資料來源名稱
        source_name = source.get("source_name", "未知資料來源")

        # 取得檔案路徑
        file_path = source.get("file_path", "")

        try:
            # 印出讀取狀態
            print(f"讀取資料來源：{source_name}，路徑：{file_path}", flush=True)

            # 讀取原始資料
            raw_df = read_data_file(file_path)

            # 將欄位轉成系統標準欄位
            normalized_df = normalize_columns(raw_df, source_name)

            # 加入列表
            normalized_list.append(normalized_df)

        except Exception as error:
            # 單一資料來源失敗不讓整個流程中斷
            print(f"讀取或標準化資料失敗：{source_name}，錯誤：{error}", flush=True)

    # 如果沒有任何官方資料成功讀取，改用範例資料
    if not normalized_list:
        print("沒有任何官方資料成功讀取，改用範例資料。", flush=True)

        # 讀取範例資料
        raw_df = read_data_file(SAMPLE_DATA_PATH)

        # 標準化範例資料
        normalized_df = normalize_columns(raw_df, "內建範例資料")

        # 加入列表
        normalized_list.append(normalized_df)

    # 合併所有標準化資料
    combined_df = pd.concat(normalized_list, ignore_index=True)

    # 清理與分類
    final_df = clean_and_classify(combined_df)

    # 輸出分析後 CSV
    final_df.to_csv(ANALYZED_DATA_PATH, index=False, encoding="utf-8-sig")

    # 印出完成訊息
    print(f"資料流程完成，共 {len(final_df)} 筆資料。", flush=True)

    # 回傳整理後資料
    return final_df


# 安全載入分析後資料
def load_analyzed_data():
    # 如果分析後 CSV 存在，就讀取
    if os.path.exists(ANALYZED_DATA_PATH):
        try:
            # 讀取 CSV
            df = pd.read_csv(ANALYZED_DATA_PATH, encoding="utf-8-sig")

            # 補齊標準欄位
            for col in STANDARD_COLUMNS:
                if col not in df.columns:
                    df[col] = ""

            # 將金額欄位轉成數字
            df["penalty_amount"] = (
                pd.to_numeric(df["penalty_amount"], errors="coerce")
                .fillna(0)
                .astype(int)
            )

            # 回傳標準欄位
            return df[STANDARD_COLUMNS]

        except Exception as error:
            # 讀取失敗時印出錯誤
            print(f"讀取 analyzed_labor_violations.csv 失敗：{error}", flush=True)

    # 若不存在或失敗，回傳空表
    return pd.DataFrame(columns=STANDARD_COLUMNS)


# 啟動時準備資料
def startup_prepare_data():
    try:
        # 每次啟動都嘗試下載與更新資料
        return run_data_pipeline()

    except Exception as error:
        # 若資料流程失敗，不讓網站掛掉
        print("啟動時資料流程失敗，改用既有資料或範例資料。", flush=True)
        print(f"錯誤：{error}", flush=True)
        traceback.print_exc()

        # 先嘗試使用既有分析資料
        existing_df = load_analyzed_data()

        # 如果既有資料非空，直接使用
        if not existing_df.empty:
            return existing_df

        # 最後才使用範例資料
        raw_df = read_data_file(SAMPLE_DATA_PATH)
        normalized_df = normalize_columns(raw_df, "內建範例資料")
        final_df = clean_and_classify(normalized_df)
        final_df.to_csv(ANALYZED_DATA_PATH, index=False, encoding="utf-8-sig")
        return final_df


# 將 value_counts 轉成模板需要的格式
def series_to_items(series):
    # 空資料回傳空列表
    if series is None or series.empty:
        return []

    # 取得最大值，用來計算長條百分比
    max_value = int(series.max()) if int(series.max()) > 0 else 1

    # 儲存轉換後資料
    items = []

    # 逐一轉換
    for name, value in series.items():
        # 轉成 int
        value = int(value)

        # 計算長條百分比
        percent = round((value / max_value) * 100, 2)

        # 加入結果
        items.append({
            "name": str(name) if str(name).strip() else "未標示",
            "value": value,
            "percent": percent,
        })

    # 回傳列表
    return items


# 取得摘要卡資料
def get_summary_cards(df):
    # 空資料摘要
    if df.empty:
        return {
            "total_records": 0,
            "total_companies": 0,
            "total_cities": 0,
            "repeated_companies": 0,
            "total_penalty": 0,
            "top_category": "無資料",
            "latest_date": "無資料",
        }

    # 補齊欄位
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # 計算事業單位數
    company_count = int(
        df["company_name"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )

    # 計算縣市數
    city_count = int(
        df["city"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )

    # 計算重複出現事業單位數
    company_counts = df["company_name"].dropna().astype(str).str.strip().value_counts()
    repeated_companies = int((company_counts >= 2).sum())

    # 找出最多的違規類型
    category_counts = df["violation_category"].dropna().astype(str).str.strip().value_counts()
    top_category = category_counts.index[0] if not category_counts.empty else "無資料"

    # 找出最近公告日期
    dates = df["announce_date"].dropna().astype(str).str.strip()
    dates = dates[dates != ""]
    latest_date = str(dates.max()) if not dates.empty else "無資料"

    # 計算總處分金額
    total_penalty = int(pd.to_numeric(df["penalty_amount"], errors="coerce").fillna(0).sum())

    # 回傳摘要資料
    return {
        "total_records": int(len(df)),
        "total_companies": company_count,
        "total_cities": city_count,
        "repeated_companies": repeated_companies,
        "total_penalty": total_penalty,
        "top_category": top_category,
        "latest_date": latest_date,
    }


# 取得 Dashboard 資料
def get_dashboard_data(df):
    # 空資料回傳空結構
    if df.empty:
        return {
            "summary": get_summary_cards(df),
            "category_items": [],
            "city_items": [],
            "top_company_items": [],
            "source_items": [],
        }

    # 補齊欄位
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # 回傳 Dashboard 所需資料
    return {
        "summary": get_summary_cards(df),
        "category_items": series_to_items(
            df["violation_category"].fillna("未分類").value_counts().head(10)
        ),
        "city_items": series_to_items(
            df["city"].fillna("未標示").value_counts().head(10)
        ),
        "top_company_items": series_to_items(
            df["company_name"].fillna("未標示").value_counts().head(10)
        ),
        "source_items": series_to_items(
            df["source_name"].fillna("未標示").value_counts().head(10)
        ),
    }