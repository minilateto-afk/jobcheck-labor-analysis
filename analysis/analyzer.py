# 匯入 pandas
import pandas as pd


# 讀取分析後資料
def load_analyzed_data(file_path):
    # 讀取 CSV
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 處分金額轉成數字，避免讀取後變字串
    df["penalty_amount"] = pd.to_numeric(df["penalty_amount"], errors="coerce").fillna(0).astype(int)

    # 日期欄位轉成字串，避免模板顯示 NaN
    df["announce_date"] = df["announce_date"].fillna("").astype(str)
    df["penalty_date"] = df["penalty_date"].fillna("").astype(str)

    # 回傳資料
    return df


# 產生 Dashboard 統計摘要
def generate_summary(df):
    # 計算總筆數
    total_records = len(df)

    # 計算事業單位數
    company_count = df["company_name"].nunique()

    # 計算縣市或主管機關數
    city_count = df["city"].nunique()

    # 計算總處分金額
    total_penalty = int(df["penalty_amount"].sum())

    # 計算最高處分金額
    max_penalty = int(df["penalty_amount"].max()) if total_records > 0 else 0

    # 計算重複出現事業單位數
    company_record_counts = df["company_name"].value_counts()
    repeated_company_count = int((company_record_counts > 1).sum())

    # 找出最常見違規類型
    if total_records > 0:
        main_category = df["violation_category"].mode().iloc[0]
    else:
        main_category = "無資料"

    # 回傳統計摘要
    return {
        "total_records": total_records,
        "company_count": company_count,
        "city_count": city_count,
        "total_penalty": total_penalty,
        "max_penalty": max_penalty,
        "repeated_company_count": repeated_company_count,
        "main_category": main_category,
    }


# 將 Series 統計轉成模板容易使用的格式
def series_to_items(series, limit=10):
    # 取前幾名並轉成字典列表
    return [
        {
            "label": str(index),
            "value": int(value)
        }
        for index, value in series.head(limit).items()
    ]


# 產生圖表用統計資料
def generate_dashboard_data(df):
    # 依縣市統計筆數
    city_counts = series_to_items(df["city"].value_counts(), limit=10)

    # 依違規類型統計筆數
    category_counts = series_to_items(df["violation_category"].value_counts(), limit=10)

    # 依事業單位統計重複出現次數
    company_counts = series_to_items(df["company_name"].value_counts(), limit=10)

    # 建立年份欄位
    year_series = df["announce_date"].astype(str).str.slice(0, 4)

    # 只保留看起來像西元年的資料
    year_series = year_series[year_series.str.match(r"^\d{4}$", na=False)]

    # 依年份統計筆數
    year_counts = series_to_items(year_series.value_counts().sort_index(), limit=20)

    # 建立處分金額區間
    amount_bins = pd.cut(
        df["penalty_amount"],
        bins=[-1, 0, 20000, 50000, 100000, 300000, 100000000],
        labels=["0", "1-2萬", "2-5萬", "5-10萬", "10-30萬", "30萬以上"]
    )

    # 統計金額區間
    amount_counts = series_to_items(amount_bins.value_counts().sort_index(), limit=10)

    # 回傳 Dashboard 資料
    return {
        "city_counts": city_counts,
        "category_counts": category_counts,
        "company_counts": company_counts,
        "year_counts": year_counts,
        "amount_counts": amount_counts,
    }


# 取得最近幾筆紀錄
def get_recent_records(df, limit=30):
    # 依公告日期排序
    sorted_df = df.sort_values(by="announce_date", ascending=False)

    # 回傳前幾筆 dict
    return sorted_df.head(limit).to_dict(orient="records")