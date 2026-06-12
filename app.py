# 匯入 os，用來處理檔案路徑
import os

# 匯入 csv，用來處理欄位數不固定的官方 CSV
import csv

# 匯入 traceback，用來在資料流程失敗時印出完整錯誤
import traceback

# 匯入 pandas，用來讀取與分析 CSV 資料
import pandas as pd

# 匯入 Flask 相關功能
from flask import Flask, render_template, request

# 匯入設定檔
from config import (
    ANALYZED_DATA_PATH,
    PROCESSED_DATA_DIR,
    SAMPLE_DATA_PATH,
    STANDARD_COLUMNS,
    CATEGORY_RULES
)

# 匯入資料下載函式
from collectors.gov_open_data_fetcher import download_all_sources


# 建立 Flask app
app = Flask(__name__)


# 確保處理後資料資料夾存在
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


# -----------------------------
# 資料讀取與欄位處理
# -----------------------------

# 讀取欄位數可能不固定的 CSV
def read_messy_csv(file_path, encoding):
    with open(file_path, "r", encoding=encoding, errors="replace", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if not rows:
        return pd.DataFrame()

    # 勞動部 CSV 前面可能有標題列或說明列，不一定第一列就是表頭
    header_keywords = [
        "縣市",
        "單位",
        "公告日期",
        "處分日期",
        "事業單位",
        "名稱",
        "違法",
        "違反",
        "法規",
        "罰鍰",
        "備註"
    ]

    header_index = 0

    # 找出最像表頭的那一列
    for index, row in enumerate(rows[:20]):
        joined = " ".join(str(cell).strip() for cell in row)
        hit_count = sum(1 for keyword in header_keywords if keyword in joined)

        if hit_count >= 3:
            header_index = index
            break

    header = [str(col).strip() for col in rows[header_index]]

    # 如果表頭有空欄位，補上欄位名稱，避免 Pandas 出錯
    fixed_header = []
    seen = {}

    for index, col in enumerate(header):
        if not col:
            col = f"未命名欄位{index + 1}"

        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 1

        fixed_header.append(col)

    header = fixed_header
    header_len = len(header)

    fixed_rows = []

    for row in rows[header_index + 1:]:
        if not row or all(str(cell).strip() == "" for cell in row):
            continue

        # 如果資料欄位比表頭多，把多出來的欄位合併到最後一欄
        # 勞動部資料的違規內容或備註有時會包含逗號，容易造成欄位數增加
        if len(row) > header_len:
            row = row[:header_len - 1] + [",".join(row[header_len - 1:])]

        # 如果資料欄位比表頭少，補空字串
        if len(row) < header_len:
            row = row + [""] * (header_len - len(row))

        fixed_rows.append(row)

    df = pd.DataFrame(fixed_rows, columns=header)

    print(f"成功修復讀取 CSV：{file_path}")
    print(f"偵測表頭：{list(df.columns)}")
    print(f"原始資料筆數：{len(df)}")

    return df


# 讀取 CSV / Excel / ODS 檔案
def read_data_file(file_path):
    lower_path = file_path.lower()

    if lower_path.endswith(".csv"):
        last_error = None

        for encoding in ["utf-8-sig", "utf-8", "cp950", "big5"]:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"使用 Pandas 成功讀取 CSV：{file_path}")
                print(f"欄位：{list(df.columns)}")
                return df

            except Exception as error:
                last_error = error

                try:
                    return read_messy_csv(file_path, encoding)
                except Exception:
                    pass

        raise last_error

    if lower_path.endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)

    if lower_path.endswith(".ods"):
        return pd.read_excel(file_path, engine="odf")

    raise ValueError(f"不支援的資料格式：{file_path}")


# 從不同來源欄位名稱轉成系統統一欄位
def normalize_columns(df, source_name):
    normalized_df = pd.DataFrame()

    df.columns = [str(col).strip() for col in df.columns]

    # 用「包含關鍵字」的方式找欄位，避免官方欄位名稱多空白、換行或括號時對不到
    def find_column(candidates):
        # 先完全比對
        for candidate in candidates:
            for col in df.columns:
                if candidate == col:
                    return col

        # 再用包含比對
        for candidate in candidates:
            for col in df.columns:
                if candidate in col:
                    return col

        return None

    column_candidates = {
        "city": ["縣市", "縣市/單位別", "地方主管機關", "主管機關", "單位別", "縣市別"],
        "authority": ["主管機關", "縣市/單位別", "單位別", "處分機關"],
        "company_name": ["事業單位名稱", "事業單位", "公司名稱", "單位名稱", "雇主名稱", "受處分事業單位", "名稱"],
        "responsible_person": ["負責人", "代表人", "事業主"],
        "announce_date": ["公告日期", "公布日期", "公告年月日"],
        "penalty_date": ["處分日期", "裁處日期", "處分年月日"],
        "violated_law": ["違法法規法條", "違反法規法條", "違反法令", "違反條文", "法規法條", "違反法規"],
        "violation_content": ["法條敘述", "違反法規內容", "違法事實", "違規內容", "違反內容", "違法內容"],
        "penalty_amount": ["罰鍰金額", "處分金額", "罰鍰", "罰鍰金額或滯納金", "罰鍰金額(元)"],
        "note": ["備註", "備註說明", "說明", "其他"]
    }

    normalized_df["source_name"] = [source_name] * len(df)

    for standard_col, candidates in column_candidates.items():
        matched_col = find_column(candidates)

        if matched_col:
            normalized_df[standard_col] = df[matched_col]
            print(f"{source_name} 欄位對應：{standard_col} <- {matched_col}")
        else:
            normalized_df[standard_col] = ""
            print(f"{source_name} 找不到欄位：{standard_col}")

    for col in STANDARD_COLUMNS:
        if col not in normalized_df.columns:
            normalized_df[col] = ""

    return normalized_df[STANDARD_COLUMNS]


# 清理文字欄位
def clean_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip().replace("\n", " ").replace("\r", " ")


# 清理金額欄位
def clean_penalty_amount(value):
    if pd.isna(value):
        return 0

    text = str(value)
    text = text.replace(",", "")
    text = text.replace("元", "")
    text = text.replace("新臺幣", "")
    text = text.replace("新台幣", "")
    text = text.strip()

    # 只保留數字
    digits = "".join(ch for ch in text if ch.isdigit())

    if not digits:
        return 0

    return int(digits)


# 清理日期欄位
def clean_date(value):
    if pd.isna(value):
        return ""

    text = str(value).strip()

    if not text:
        return ""

    # 讓民國年格式先保留原樣，避免亂轉
    return text


# 判斷違規類型
def classify_violation(row):
    # 合併法規與違規內容進行關鍵字判斷
    content = f"{row.get('violated_law', '')} {row.get('violation_content', '')}"

    # 依照規則分類
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in content:
                return category

    return "其他"


# 清理與分類資料
def clean_and_classify(df):
    # 如果資料是空的，回傳標準欄位空表
    if df.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    # 清理文字欄位
    text_columns = [
        "source_name",
        "city",
        "authority",
        "company_name",
        "responsible_person",
        "violated_law",
        "violation_content",
        "note"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    # 清理日期
    df["announce_date"] = df["announce_date"].apply(clean_date)
    df["penalty_date"] = df["penalty_date"].apply(clean_date)

    # 清理金額
    df["penalty_amount"] = df["penalty_amount"].apply(clean_penalty_amount)

    # 移除沒有公司名稱的資料
    df = df[df["company_name"].astype(str).str.strip() != ""]

    # 加上違規分類
    df["violation_category"] = df.apply(classify_violation, axis=1)

    # 去除重複資料
    df = df.drop_duplicates(
        subset=["company_name", "penalty_date", "violated_law", "violation_content"],
        keep="first"
    )

    # 補齊標準欄位
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df[STANDARD_COLUMNS]


# -----------------------------
# 啟動時資料流程
# -----------------------------

# 執行資料流程
def run_data_pipeline():
    print("開始執行資料流程...")

    # 下載或取得資料來源
    source_files = download_all_sources()

    # 收集所有標準化後的資料
    normalized_list = []

    for source in source_files:
        source_name = source.get("source_name", "未知資料來源")
        file_path = source.get("file_path", "")

        try:
            print(f"讀取資料來源：{source_name}，路徑：{file_path}")

            raw_df = read_data_file(file_path)
            normalized_df = normalize_columns(raw_df, source_name)
            normalized_list.append(normalized_df)

        except Exception as error:
            print(f"讀取或標準化資料失敗：{source_name}，錯誤：{error}")

    # 如果沒有任何資料成功讀取，就嘗試讀範例資料
    if not normalized_list:
        print("沒有任何官方資料成功讀取，改用範例資料。")
        raw_df = read_data_file(SAMPLE_DATA_PATH)
        normalized_df = normalize_columns(raw_df, "內建範例資料")
        normalized_list.append(normalized_df)

    # 合併資料
    combined_df = pd.concat(normalized_list, ignore_index=True)

    # 清理與分類
    final_df = clean_and_classify(combined_df)

    # 輸出處理後資料
    final_df.to_csv(ANALYZED_DATA_PATH, index=False, encoding="utf-8-sig")

    print(f"資料流程完成，共 {len(final_df)} 筆資料。")

    return final_df


# 安全載入資料
def load_analyzed_data():
    # 如果分析後資料存在，就直接讀取
    if os.path.exists(ANALYZED_DATA_PATH):
        try:
            return pd.read_csv(ANALYZED_DATA_PATH, encoding="utf-8-sig")
        except Exception:
            pass

    # 如果沒有，就回傳空表
    return pd.DataFrame(columns=STANDARD_COLUMNS)


# 啟動時執行資料流程，但失敗也不讓網站掛掉
def startup_prepare_data():
    try:
        # 每次啟動都嘗試更新資料
        return run_data_pipeline()

    except Exception as error:
        print("啟動時資料流程失敗，但網站會繼續啟動。")
        print(f"錯誤：{error}")
        traceback.print_exc()

        # 嘗試使用已經存在的分析結果
        existing_df = load_analyzed_data()

        if not existing_df.empty:
            print("改用既有 analyzed_labor_violations.csv。")
            return existing_df

        # 最後才使用範例資料
        try:
            print("改用內建範例資料。")
            raw_df = read_data_file(SAMPLE_DATA_PATH)
            normalized_df = normalize_columns(raw_df, "內建範例資料")
            final_df = clean_and_classify(normalized_df)
            final_df.to_csv(ANALYZED_DATA_PATH, index=False, encoding="utf-8-sig")
            return final_df

        except Exception as fallback_error:
            print(f"範例資料也讀取失敗：{fallback_error}")
            return pd.DataFrame(columns=STANDARD_COLUMNS)


# 啟動時先準備資料
startup_prepare_data()


# -----------------------------
# 統計資料產生
# -----------------------------

# 取得首頁摘要
def get_summary_cards(df):
    # 空資料時也要回傳所有模板會用到的欄位，避免 Undefined 錯誤
    empty_summary = {
        "total_records": 0,
        "record_count": 0,
        "total_companies": 0,
        "company_count": 0,
        "total_cities": 0,
        "city_count": 0,
        "total_authorities": 0,
        "authority_count": 0,
        "total_penalty": 0,
        "penalty_total": 0,
        "top_category": "無資料",
        "repeated_companies": 0,
        "repeat_company_count": 0,
        "latest_date": "無資料",
        "data_source": "無資料"
    }

    if df.empty:
        return empty_summary

    # 避免欄位缺失造成模板錯誤
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # 事業單位數
    company_count = int(df["company_name"].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())

    # 縣市 / 主管機關數
    city_count = int(df["city"].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())

    # 重複出現事業單位：同一公司出現 2 次以上
    company_counts = df["company_name"].dropna().astype(str).str.strip().value_counts()
    repeated_companies = int((company_counts >= 2).sum())

    # 違規類型
    category_counts = df["violation_category"].dropna().astype(str).str.strip().value_counts()
    top_category = category_counts.index[0] if not category_counts.empty else "無資料"

    # 最近公告日期
    latest_date = "無資料"
    if "announce_date" in df.columns:
        non_empty_dates = df["announce_date"].dropna().astype(str).str.strip()
        non_empty_dates = non_empty_dates[non_empty_dates != ""]
        if not non_empty_dates.empty:
            latest_date = str(non_empty_dates.max())

    # 資料來源
    data_source = "勞動部動態下載資料"
    if "source_name" in df.columns:
        source_counts = df["source_name"].dropna().astype(str).str.strip().value_counts()
        if not source_counts.empty:
            data_source = source_counts.index[0]

    total_penalty = int(df["penalty_amount"].fillna(0).sum()) if "penalty_amount" in df.columns else 0

    return {
        "total_records": int(len(df)),
        "record_count": int(len(df)),
        "total_companies": company_count,
        "company_count": company_count,
        "total_cities": city_count,
        "city_count": city_count,
        "total_authorities": city_count,
        "authority_count": city_count,
        "total_penalty": total_penalty,
        "penalty_total": total_penalty,
        "top_category": top_category,
        "repeated_companies": repeated_companies,
        "repeat_company_count": repeated_companies,
        "latest_date": latest_date,
        "data_source": data_source
    }



# -----------------------------
# Dashboard 統計輔助函式
# -----------------------------

# 將 value_counts 轉成模板好用的格式
def series_to_items(series):
    items = []

    if series is None or series.empty:
        return items

    max_value = int(series.max()) if int(series.max()) > 0 else 1

    for name, value in series.items():
        value = int(value)
        percent = round((value / max_value) * 100, 2)

        items.append({
            "name": str(name) if str(name).strip() else "未標示",
            "value": value,
            "percent": percent
        })

    return items


# 取得 Dashboard 資料
def get_dashboard_data(df):
    if df.empty:
        return {
            "summary": get_summary_cards(df),
            "category_items": [],
            "city_items": [],
            "top_company_items": [],
            "source_items": []
        }

    # 補齊欄位，避免資料欄位缺失造成錯誤
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return {
        "summary": get_summary_cards(df),
        "category_items": series_to_items(df["violation_category"].fillna("未分類").value_counts().head(10)),
        "city_items": series_to_items(df["city"].fillna("未標示").value_counts().head(10)),
        "top_company_items": series_to_items(df["company_name"].fillna("未標示").value_counts().head(10)),
        "source_items": series_to_items(df["source_name"].fillna("未標示").value_counts().head(10))
    }




# -----------------------------
# 公司查詢輔助函式
# -----------------------------

# 搜尋公司公開紀錄
def search_company_records(keyword):
    df = load_analyzed_data()

    if df.empty or not keyword:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    keyword = str(keyword).strip()

    if not keyword:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    # 確保欄位存在
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # 以事業單位名稱進行模糊查詢
    result_df = df[
        df["company_name"].astype(str).str.contains(keyword, case=False, na=False)
    ].copy()

    # 依公告日期或處分日期排序，讓較新的資料在前面
    if "announce_date" in result_df.columns:
        result_df = result_df.sort_values(by="announce_date", ascending=False)

    return result_df


# 產生公司查詢摘要
def get_company_summary(result_df, keyword):
    if result_df.empty:
        return {
            "keyword": keyword,
            "found": False,
            "total_records": 0,
            "categories": [],
            "latest_date": "無資料",
            "total_penalty": 0,
            "main_category": "無資料"
        }

    categories = (
        result_df["violation_category"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    category_counts = categories.value_counts()
    category_list = category_counts.index.tolist()

    latest_date = "無資料"
    if "announce_date" in result_df.columns:
        dates = result_df["announce_date"].dropna().astype(str).str.strip()
        dates = dates[dates != ""]
        if not dates.empty:
            latest_date = str(dates.max())

    total_penalty = 0
    if "penalty_amount" in result_df.columns:
        total_penalty = int(result_df["penalty_amount"].fillna(0).sum())

    return {
        "keyword": keyword,
        "found": True,
        "total_records": int(len(result_df)),
        "categories": category_list,
        "latest_date": latest_date,
        "total_penalty": total_penalty,
        "main_category": category_list[0] if category_list else "無資料"
    }


# -----------------------------
# Flask Routes
# -----------------------------

# 首頁
@app.route("/")
def index():
    df = load_analyzed_data()
    summary = get_summary_cards(df)
    dashboard_data = get_dashboard_data(df)

    return render_template(
        "index.html",
        summary=summary,
        dashboard_data=dashboard_data,
        category_items=dashboard_data.get("category_items", []),
        city_items=dashboard_data.get("city_items", []),
        top_company_items=dashboard_data.get("top_company_items", []),
        source_items=dashboard_data.get("source_items", [])
    )


# 搜尋頁
@app.route("/search", methods=["GET", "POST"])
def search():
    keyword = request.values.get("keyword", "").strip()

    result_df = search_company_records(keyword)

    records = result_df.head(100).to_dict(orient="records")

    company_summary = get_company_summary(result_df, keyword)

    return render_template(
        "search.html",
        keyword=keyword,
        records=records,
        results=records,
        company_summary=company_summary,
        summary_card=company_summary
    )


# Dashboard 頁
@app.route("/dashboard")
def dashboard():
    df = load_analyzed_data()
    dashboard_data = get_dashboard_data(df)

    return render_template(
        "dashboard.html",
        dashboard_data=dashboard_data,
        summary=dashboard_data.get("summary", {}),
        category_items=dashboard_data.get("category_items", []),
        city_items=dashboard_data.get("city_items", []),
        top_company_items=dashboard_data.get("top_company_items", []),
        source_items=dashboard_data.get("source_items", [])
    )


# 全部紀錄頁
@app.route("/records")
def records():
    df = load_analyzed_data()

    record_list = df.head(200).to_dict(orient="records")

    return render_template(
        "records.html",
        records=record_list
    )


# 資料處理說明頁
@app.route("/about")
def about():
    df = load_analyzed_data()
    summary = get_summary_cards(df)

    return render_template(
        "about.html",
        summary=summary
    )


# 健康檢查頁
@app.route("/health")
def health():
    df = load_analyzed_data()

    return {
        "status": "ok",
        "records": int(len(df)),
        "data_path": ANALYZED_DATA_PATH
    }


# 主程式入口
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
