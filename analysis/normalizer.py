# 匯入 pandas，用來整理 DataFrame
import pandas as pd

# 匯入系統統一欄位
from config import STANDARD_COLUMNS


# 從多個可能欄位名稱中找到實際存在的欄位
def find_column(df, possible_names):
    # 逐一檢查可能欄位名稱
    for name in possible_names:
        # 如果欄位存在，就回傳該欄位名稱
        if name in df.columns:
            return name

    # 如果都找不到，就回傳 None
    return None


# 從原始資料中安全取得欄位
def get_series_or_empty(df, column_name):
    # 如果欄位名稱存在，就回傳該欄位
    if column_name is not None and column_name in df.columns:
        return df[column_name]

    # 如果欄位不存在，就回傳空字串 Series
    return pd.Series([""] * len(df))


# 將不同縣市資料欄位統一成系統欄位
def normalize_labor_data(raw_df, source_name):
    # 複製原始資料，避免直接修改
    df = raw_df.copy()

    # 去除欄位名稱前後空白
    df.columns = [str(col).strip() for col in df.columns]

    # 建立欄位對應表
    column_map = {
        "city": [
            "縣市",
            "主管機關",
            "公告機關",
            "處分機關",
            "發布機關",
        ],
        "authority": [
            "主管機關",
            "公告機關",
            "處分機關",
            "發布機關",
        ],
        "company_name": [
            "事業單位名稱",
            "事業單位或事業主名稱",
            "事業單位名稱或負責人",
            "公司名稱",
            "名稱",
            "受處分事業單位",
        ],
        "responsible_person": [
            "負責人",
            "負責人姓名",
            "代表人",
            "事業主姓名",
        ],
        "announce_date": [
            "公告日期",
            "公布日期",
            "發布日期",
            "公告年月",
        ],
        "penalty_date": [
            "處分日期",
            "裁處日期",
            "裁罰日期",
            "處分年月日",
        ],
        "violated_law": [
            "違反法規法條",
            "違反法令條款",
            "違反條文",
            "違法法規法條",
            "法條",
            "違反法規",
        ],
        "violation_content": [
            "違反法規內容",
            "違規內容",
            "違反事實",
            "違法事實",
            "違反事項",
            "違法內容",
        ],
        "penalty_amount": [
            "處分金額",
            "裁罰金額",
            "罰鍰金額",
            "罰鍰金額或滯納金",
            "罰鍰",
        ],
        "note": [
            "備註",
            "說明",
            "備考",
        ],
    }

    # 建立標準化後的 DataFrame
    normalized_df = pd.DataFrame()

    # 加入資料來源名稱
    normalized_df["source_name"] = source_name

    # 逐一建立標準欄位
    for standard_col, possible_names in column_map.items():
        # 找出實際欄位名稱
        actual_col = find_column(df, possible_names)

        # 取得欄位資料或空值
        normalized_df[standard_col] = get_series_or_empty(df, actual_col)

    # 先建立空的違規分類欄位，後續由 classifier 補上
    normalized_df["violation_category"] = ""

    # 確保所有標準欄位都存在
    for col in STANDARD_COLUMNS:
        if col not in normalized_df.columns:
            normalized_df[col] = ""

    # 只保留標準欄位
    normalized_df = normalized_df[STANDARD_COLUMNS]

    # 回傳標準化後資料
    return normalized_df