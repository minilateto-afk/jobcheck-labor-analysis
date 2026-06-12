# 匯入 pandas，用來建立 DataFrame
import pandas as pd

# 匯入系統標準欄位
from config import STANDARD_COLUMNS


# 找出最符合的欄位名稱
def find_column(df_columns, candidates):
    # 第一輪：完全比對
    for candidate in candidates:
        for col in df_columns:
            if candidate == col:
                return col

    # 第二輪：包含比對
    for candidate in candidates:
        for col in df_columns:
            if candidate in col:
                return col

    # 找不到就回傳 None
    return None


# 將不同來源欄位轉成系統統一欄位
def normalize_columns(df, source_name):
    # 複製資料，避免直接修改原始 df
    df = df.copy()

    # 清理欄位名稱前後空白
    df.columns = [str(col).strip() for col in df.columns]

    # 建立標準化後 DataFrame
    normalized_df = pd.DataFrame()

    # 欄位候選名稱設定
    column_candidates = {
        "city": [
            "縣市／單位別",
            "縣市/單位別",
            "縣市",
            "縣市別",
            "地方主管機關",
            "主管機關",
            "單位別",
        ],
        "authority": [
            "縣市／單位別",
            "縣市/單位別",
            "主管機關",
            "處分機關",
            "單位別",
        ],
        "company_name": [
            "事業單位名稱",
            "事業單位",
            "公司名稱",
            "單位名稱",
            "雇主名稱",
            "受處分事業單位",
            "自然人姓名",
        ],
        "responsible_person": [
            "負責人",
            "代表人",
            "事業主",
            "事業單位名稱(負責人)",
            "自然人姓名",
        ],
        "announce_date": [
            "公告日期",
            "公布日期",
            "公告年月日",
        ],
        "penalty_date": [
            "處分日期",
            "裁處日期",
            "處分年月日",
        ],
        "violated_law": [
            "違反法規條款",
            "違反法規法條",
            "違法法規法條",
            "違反法令",
            "違反條文",
            "法規法條",
            "違反法規",
        ],
        "violation_content": [
            "法條敘述",
            "違反法規內容",
            "違法事實",
            "違規內容",
            "違反內容",
            "違法內容",
        ],
        "penalty_amount": [
            "處分金額／滯納金",
            "罰鍰金額",
            "處分金額",
            "罰鍰",
            "罰鍰金額或滯納金",
            "罰鍰金額(元)",
        ],
        "note": [
            "備註",
            "備註說明",
            "說明",
            "其他",
        ],
    }

    # 加入資料來源名稱
    normalized_df["source_name"] = [source_name] * len(df)

    # 逐一對應標準欄位
    for standard_col, candidates in column_candidates.items():
        # 找出原始資料中最符合的欄位
        matched_col = find_column(df.columns, candidates)

        # 如果找到欄位，就複製資料
        if matched_col:
            normalized_df[standard_col] = df[matched_col]
        else:
            normalized_df[standard_col] = ""

    # 補齊所有標準欄位
    for col in STANDARD_COLUMNS:
        if col not in normalized_df.columns:
            normalized_df[col] = ""

    # 回傳固定欄位順序
    return normalized_df[STANDARD_COLUMNS]