# 匯入 pandas
import pandas as pd


# 進行公司名稱搜尋
def search_company(df, keyword):
    # 如果關鍵字是空的，就回傳空 DataFrame
    if keyword is None or keyword.strip() == "":
        return df.iloc[0:0]

    # 清理關鍵字
    keyword = keyword.strip()

    # 建立搜尋條件：公司名稱包含關鍵字
    mask = df["company_name"].str.contains(keyword, case=False, na=False)

    # 回傳搜尋結果
    return df[mask].copy()


# 建立查詢摘要卡資料
def build_company_summary(search_results, keyword):
    # 如果沒有搜尋結果，回傳無紀錄摘要
    if len(search_results) == 0:
        return {
            "keyword": keyword,
            "has_records": False,
            "record_count": 0,
            "company_count": 0,
            "latest_date": "無公開紀錄",
            "main_category": "無公開紀錄",
            "total_penalty": 0,
            "max_penalty": 0,
            "message": "目前未在系統資料中查到相關公開違規紀錄。"
        }

    # 計算公開紀錄筆數
    record_count = len(search_results)

    # 計算涉及公司數
    company_count = search_results["company_name"].nunique()

    # 找出最新公告日期
    latest_date = search_results["announce_date"].max()

    # 找出最常見違規類型
    main_category = search_results["violation_category"].mode().iloc[0]

    # 計算累計處分金額
    total_penalty = int(search_results["penalty_amount"].sum())

    # 計算最高處分金額
    max_penalty = int(search_results["penalty_amount"].max())

    # 回傳摘要字典
    return {
        "keyword": keyword,
        "has_records": True,
        "record_count": record_count,
        "company_count": company_count,
        "latest_date": latest_date,
        "main_category": main_category,
        "total_penalty": total_penalty,
        "max_penalty": max_penalty,
        "message": "查詢結果僅依政府公開資料整理，作為求職前了解公開紀錄之參考。"
    }