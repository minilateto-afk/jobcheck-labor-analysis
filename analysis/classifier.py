# 匯入分類規則
from config import CATEGORY_RULES


# 判斷單筆資料的違規類型
def classify_single_record(row):
    # 合併法條與違規內容，增加分類命中機率
    text = f"{row.get('violated_law', '')} {row.get('violation_content', '')}"

    # 逐一檢查分類規則
    for category, keywords in CATEGORY_RULES.items():
        # 如果任一關鍵字出現在文字中，就回傳該分類
        for keyword in keywords:
            if keyword in text:
                return category

    # 如果都沒有命中，就歸類為其他
    return "其他"


# 對整份資料套用違規分類
def apply_violation_classification(df):
    # 複製資料，避免直接修改原始 DataFrame
    classified_df = df.copy()

    # 套用分類函式
    classified_df["violation_category"] = classified_df.apply(classify_single_record, axis=1)

    # 回傳分類後資料
    return classified_df