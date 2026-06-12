# 匯入 re，用來拆分公司名稱與負責人
import re

# 匯入 pandas，用來處理缺失值
import pandas as pd

# 匯入系統標準欄位
from config import STANDARD_COLUMNS

# 匯入違規分類函式
from analysis.classifier import classify_violation


# 清理文字欄位
def clean_text(value):
    # 如果是缺失值，回傳空字串
    if pd.isna(value):
        return ""

    # 轉成字串並移除換行與前後空白
    return str(value).replace("\r", " ").replace("\n", " ").strip()


# 清理金額欄位
def clean_penalty_amount(value):
    # 如果是缺失值，回傳 0
    if pd.isna(value):
        return 0

    # 轉成文字
    text = str(value)

    # 移除常見金額文字與符號
    text = text.replace(",", "")
    text = text.replace("元", "")
    text = text.replace("新臺幣", "")
    text = text.replace("新台幣", "")
    text = text.strip()

    # 只保留數字
    digits = "".join(ch for ch in text if ch.isdigit())

    # 如果沒有數字，回傳 0
    if not digits:
        return 0

    # 回傳整數金額
    return int(digits)


# 清理日期欄位
def clean_date(value):
    # 如果是缺失值，回傳空字串
    if pd.isna(value):
        return ""

    # 保留原本民國年格式，只清理空白
    return str(value).strip()


# 拆分事業單位名稱與負責人
def split_company_and_person(company_value, person_value):
    # 清理公司名稱
    company_text = clean_text(company_value)

    # 清理負責人欄位
    person_text = clean_text(person_value)

    # 支援半形與全形括號，例如 公司名稱(負責人) 或 公司名稱（負責人）
    match = re.match(r"^(.*?)\s*[\(（](.*?)[\)）]\s*$", company_text)

    # 如果符合括號格式，就拆成公司名稱與負責人
    if match:
        company_name = match.group(1).strip()
        responsible_person = match.group(2).strip()
        return company_name, responsible_person

    # 不符合格式就保留原內容
    return company_text, person_text


# 清理與分類資料
def clean_and_classify(df):
    # 如果是空資料，回傳標準空表
    if df.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    # 複製資料，避免修改原始資料
    df = df.copy()

    # 補齊標準欄位
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # 需要清理的文字欄位
    text_columns = [
        "source_name",
        "city",
        "authority",
        "company_name",
        "responsible_person",
        "announce_date",
        "penalty_date",
        "violated_law",
        "violation_content",
        "note",
    ]

    # 逐一清理文字欄位
    for col in text_columns:
        df[col] = df[col].apply(clean_text)

    # 拆分公司名稱與負責人
    split_results = df.apply(
        lambda row: split_company_and_person(row["company_name"], row["responsible_person"]),
        axis=1,
    )

    # 回填公司名稱
    df["company_name"] = [item[0] for item in split_results]

    # 回填負責人
    df["responsible_person"] = [item[1] for item in split_results]

    # 清理公告日期
    df["announce_date"] = df["announce_date"].apply(clean_date)

    # 清理處分日期
    df["penalty_date"] = df["penalty_date"].apply(clean_date)

    # 清理處分金額
    df["penalty_amount"] = df["penalty_amount"].apply(clean_penalty_amount)

    # 移除沒有公司名稱的資料
    df = df[df["company_name"].astype(str).str.strip() != ""].copy()

    # 加上違規分類
    df["violation_category"] = df.apply(classify_violation, axis=1)

    # 去除重複資料
    df = df.drop_duplicates(
        subset=["company_name", "penalty_date", "violated_law", "violation_content"],
        keep="first",
    )

    # 回傳標準欄位
    return df[STANDARD_COLUMNS]