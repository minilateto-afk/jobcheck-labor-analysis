# 匯入 pandas，用來建立空 DataFrame
import pandas as pd

# 匯入標準欄位
from config import STANDARD_COLUMNS


# 依照公開紀錄筆數取得觀察標籤
def get_observation_info(record_count):
    # 0 筆：查無紀錄
    if record_count <= 0:
        return {
            "label": "查無紀錄",
            "class_name": "label-blue",
            "description": "目前匯入資料中未查到相關公開紀錄。",
        }

    # 1 筆：單筆紀錄
    if record_count == 1:
        return {
            "label": "單筆紀錄",
            "class_name": "label-green",
            "description": "查到少量公開紀錄，建議閱讀違反法規與公告日期。",
        }

    # 2 到 4 筆：多筆紀錄
    if record_count <= 4:
        return {
            "label": "多筆紀錄",
            "class_name": "label-yellow",
            "description": "同一事業單位出現多筆公開紀錄，建議比對日期與類型。",
        }

    # 5 筆以上：重複出現
    return {
        "label": "重複出現",
        "class_name": "label-orange",
        "description": "同一事業單位多次出現在公開資料中，求職前可特別留意紀錄內容。",
    }


# 替資料加上觀察標籤欄位
def attach_observation_labels(result_df, full_df):
    # 如果結果資料是空的，直接回傳
    if result_df.empty:
        return result_df

    # 複製資料，避免改到原始 DataFrame
    result_df = result_df.copy()

    # 依全資料計算每間公司的公開紀錄筆數
    company_counts = (
        full_df["company_name"]
        .dropna()
        .astype(str)
        .str.strip()
        .value_counts()
        .to_dict()
    )

    # 建立每一筆資料的觀察筆數
    result_df["company_record_count"] = result_df["company_name"].astype(str).str.strip().map(company_counts).fillna(0).astype(int)

    # 建立觀察標籤
    result_df["observation_label"] = result_df["company_record_count"].apply(
        lambda count: get_observation_info(count)["label"]
    )

    # 建立觀察標籤 CSS class
    result_df["observation_class"] = result_df["company_record_count"].apply(
        lambda count: get_observation_info(count)["class_name"]
    )

    # 回傳加上標籤後的資料
    return result_df


# 搜尋公司公開紀錄
def search_company_records(df, keyword):
    # 如果資料空或關鍵字空，回傳空表
    if df.empty or not keyword:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    # 清理關鍵字
    keyword = str(keyword).strip()

    # 如果關鍵字清理後仍是空的，回傳空表
    if not keyword:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    # 補齊標準欄位
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # 使用 regex=False，避免公司名稱裡有括號等符號造成搜尋錯誤
    result_df = df[
        df["company_name"]
        .astype(str)
        .str.contains(keyword, case=False, na=False, regex=False)
    ].copy()

    # 加上公開紀錄觀察標籤
    result_df = attach_observation_labels(result_df, df)

    # 依公告日期排序，讓較新的紀錄在前
    if "announce_date" in result_df.columns:
        result_df = result_df.sort_values(by="announce_date", ascending=False)

    # 回傳搜尋結果
    return result_df


# 取得公司搜尋摘要
def get_company_summary(result_df, keyword):
    # 沒有搜尋結果時
    if result_df.empty:
        observation = get_observation_info(0)

        return {
            "keyword": keyword,
            "found": False,
            "total_records": 0,
            "categories": [],
            "latest_date": "無資料",
            "total_penalty": 0,
            "main_category": "無資料",
            "observation_label": observation["label"],
            "observation_class": observation["class_name"],
            "observation_description": observation["description"],
        }

    # 取得違規分類列表
    categories = result_df["violation_category"].dropna().astype(str).str.strip()

    # 計算分類次數
    category_counts = categories.value_counts()

    # 取得分類名稱列表
    category_list = category_counts.index.tolist()

    # 取得最近公告日期
    dates = result_df["announce_date"].dropna().astype(str).str.strip()
    dates = dates[dates != ""]
    latest_date = str(dates.max()) if not dates.empty else "無資料"

    # 計算總處分金額
    total_penalty = int(result_df["penalty_amount"].fillna(0).sum())

    # 依查詢結果筆數取得觀察標籤
    observation = get_observation_info(len(result_df))

    # 回傳摘要
    return {
        "keyword": keyword,
        "found": True,
        "total_records": int(len(result_df)),
        "categories": category_list,
        "latest_date": latest_date,
        "total_penalty": total_penalty,
        "main_category": category_list[0] if category_list else "無資料",
        "observation_label": observation["label"],
        "observation_class": observation["class_name"],
        "observation_description": observation["description"],
    }