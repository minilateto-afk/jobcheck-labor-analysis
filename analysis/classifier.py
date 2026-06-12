# 匯入分類規則
from config import CATEGORY_RULES


# 依照關鍵字分類違規類型
def classify_violation(row):
    # 合併違反法規條款與法條敘述
    text = f"{row.get('violated_law', '')} {row.get('violation_content', '')}"

    # 逐一檢查分類規則
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in text:
                return category

    # 沒有命中任何規則時歸類為其他
    return "其他"