# 匯入 pandas，用來讀取 CSV、Excel、ODS
import pandas as pd


# 嘗試用多種中文常見編碼讀取 CSV
def read_csv_with_encoding(file_path):
    # 常見中文資料編碼
    encodings = ["utf-8-sig", "utf-8", "cp950", "big5"]

    # 記錄最後一次錯誤
    last_error = None

    # 逐一嘗試不同編碼
    for encoding in encodings:
        try:
            # 讀取 CSV
            return pd.read_csv(file_path, encoding=encoding)

        except Exception as error:
            # 如果失敗，就記錄錯誤後繼續嘗試下一個編碼
            last_error = error

    # 如果全部失敗，就丟出錯誤
    raise ValueError(f"無法讀取 CSV 檔案：{file_path}，錯誤：{last_error}")


# 依副檔名自動讀取表格資料
def load_table_file(file_path):
    # 將路徑轉成小寫，方便判斷副檔名
    lower_path = file_path.lower()

    # 如果是 CSV，就使用多編碼讀取
    if lower_path.endswith(".csv"):
        return read_csv_with_encoding(file_path)

    # 如果是 Excel，就用 read_excel
    if lower_path.endswith(".xlsx") or lower_path.endswith(".xls"):
        return pd.read_excel(file_path)

    # 如果是 ODS，就用 read_excel 並指定 engine
    if lower_path.endswith(".ods"):
        return pd.read_excel(file_path, engine="odf")

    # 如果格式不支援，就丟出錯誤
    raise ValueError(f"不支援的資料格式：{file_path}")