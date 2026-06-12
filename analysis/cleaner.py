# 匯入 re，用來使用正規表示式
import re

# 匯入 pandas，用來處理日期與空值
import pandas as pd


# 將文字轉成乾淨字串
def clean_text(value):
    # 如果是空值，回傳空字串
    if pd.isna(value):
        return ""

    # 轉成字串
    text = str(value)

    # 去除前後空白
    text = text.strip()

    # 移除連續空白
    text = re.sub(r"\s+", " ", text)

    # 回傳清理後文字
    return text


# 將處分金額轉成數字
def clean_penalty_amount(value):
    # 如果是空值，回傳 0
    if pd.isna(value):
        return 0

    # 轉成字串
    text = str(value)

    # 移除逗號與空白
    text = text.replace(",", "").strip()

    # 使用正規表示式抓數字
    match = re.search(r"\d+", text)

    # 如果找不到數字，回傳 0
    if not match:
        return 0

    # 回傳整數金額
    return int(match.group())


# 將民國年或西元年日期轉成標準日期
def clean_date(value):
    # 如果是空值，回傳空字串
    if pd.isna(value):
        return ""

    # 轉成字串並清理空白
    text = str(value).strip()

    # 如果是空字串，回傳空字串
    if text == "":
        return ""

    # 將常見分隔符號統一成 /
    text = text.replace("-", "/").replace(".", "/").replace("年", "/").replace("月", "/").replace("日", "")

    # 抓出所有數字
    numbers = re.findall(r"\d+", text)

    # 如果完全沒有數字，回傳原文字
    if not numbers:
        return text

    try:
        # 取得年份
        year = int(numbers[0])

        # 如果年份小於 1911，視為民國年，轉成西元年
        if year < 1911:
            year += 1911

        # 取得月份，沒有就補 1
        month = int(numbers[1]) if len(numbers) > 1 else 1

        # 取得日期，沒有就補 1
        day = int(numbers[2]) if len(numbers) > 2 else 1

        # 回傳 YYYY-MM-DD
        return f"{year:04d}-{month:02d}-{day:02d}"

    except Exception:
        # 如果轉換失敗，就回傳原文字
        return text


# 清理勞動違規資料
def clean_labor_data(df):
    # 複製資料，避免直接修改原始 DataFrame
    cleaned_df = df.copy()

    # 需要文字清理的欄位
    text_columns = [
        "source_name",
        "city",
        "authority",
        "company_name",
        "responsible_person",
        "violated_law",
        "violation_content",
        "note",
    ]

    # 逐一清理文字欄位
    for col in text_columns:
        cleaned_df[col] = cleaned_df[col].apply(clean_text)

    # 清理公告日期
    cleaned_df["announce_date"] = cleaned_df["announce_date"].apply(clean_date)

    # 清理處分日期
    cleaned_df["penalty_date"] = cleaned_df["penalty_date"].apply(clean_date)

    # 清理處分金額
    cleaned_df["penalty_amount"] = cleaned_df["penalty_amount"].apply(clean_penalty_amount)

    # 如果 city 是空的，就嘗試用 authority 補上
    cleaned_df["city"] = cleaned_df.apply(
        lambda row: row["authority"] if row["city"] == "" else row["city"],
        axis=1
    )

    # 移除公司名稱空白的資料
    cleaned_df = cleaned_df[cleaned_df["company_name"] != ""]

    # 移除完全重複資料
    cleaned_df = cleaned_df.drop_duplicates()

    # 回傳清理後資料
    return cleaned_df