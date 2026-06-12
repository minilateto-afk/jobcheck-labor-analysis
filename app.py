# 匯入 Flask 相關功能
from flask import Flask, render_template, request

# 匯入分析後資料路徑
from config import ANALYZED_DATA_PATH

# 匯入資料分析函式
from analysis.analyzer import (
    startup_prepare_data,
    load_analyzed_data,
    get_summary_cards,
    get_dashboard_data,
)

# 匯入搜尋與標籤函式
from analysis.searcher import (
    search_company_records,
    get_company_summary,
    attach_observation_labels,
)


# 建立 Flask app
app = Flask(__name__)


# ================================
# 啟動時自動準備資料
# ================================

# 啟動 Flask 前，先自動下載與整理資料
startup_prepare_data()


# ================================
# Flask Routes
# ================================

# 首頁
@app.route("/")
def index():
    # 載入分析後資料
    df = load_analyzed_data()

    # 取得首頁摘要卡片
    summary = get_summary_cards(df)

    # 取得簡要 dashboard 資料
    dashboard_data = get_dashboard_data(df)

    # 回傳首頁模板
    return render_template(
        "index.html",
        summary=summary,
        category_items=dashboard_data["category_items"],
        city_items=dashboard_data["city_items"],
    )


# 公司查詢頁
@app.route("/search", methods=["GET", "POST"])
def search():
    # 取得搜尋關鍵字
    keyword = request.values.get("keyword", "").strip()

    # 載入分析後資料
    df = load_analyzed_data()

    # 搜尋公司公開紀錄
    result_df = search_company_records(df, keyword)

    # 取得搜尋摘要
    company_summary = get_company_summary(result_df, keyword)

    # 最多顯示前 100 筆，避免頁面太長
    records = result_df.head(100).to_dict(orient="records")

    # 回傳搜尋頁模板
    return render_template(
        "search.html",
        keyword=keyword,
        records=records,
        company_summary=company_summary,
    )


# 趨勢儀表板頁
@app.route("/dashboard")
def dashboard():
    # 載入分析後資料
    df = load_analyzed_data()

    # 取得 dashboard 資料
    dashboard_data = get_dashboard_data(df)

    # 回傳 dashboard 模板
    return render_template(
        "dashboard.html",
        summary=dashboard_data["summary"],
        category_items=dashboard_data["category_items"],
        city_items=dashboard_data["city_items"],
        top_company_items=dashboard_data["top_company_items"],
        source_items=dashboard_data["source_items"],
    )


# 公開紀錄列表頁
@app.route("/records")
def records():
    # 載入分析後資料
    df = load_analyzed_data()

    # 替公開紀錄加上觀察標籤
    labeled_df = attach_observation_labels(df, df)

    # 只顯示前 200 筆
    record_list = labeled_df.head(200).to_dict(orient="records")

    # 回傳公開紀錄頁
    return render_template(
        "records.html",
        records=record_list,
    )


# 資料處理說明頁
@app.route("/about")
def about():
    # 載入分析後資料
    df = load_analyzed_data()

    # 取得摘要資料
    summary = get_summary_cards(df)

    # 回傳說明頁
    return render_template(
        "about.html",
        summary=summary,
    )


# 健康檢查 API
@app.route("/health")
def health():
    # 載入分析後資料
    df = load_analyzed_data()

    # 回傳 JSON 狀態
    return {
        "status": "ok",
        "records": int(len(df)),
        "data_path": ANALYZED_DATA_PATH,
    }


# ================================
# 主程式入口
# ================================

# 啟動 Flask
if __name__ == "__main__":
    # 關閉 use_reloader，避免 debug 模式讓資料流程執行兩次
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,
    )