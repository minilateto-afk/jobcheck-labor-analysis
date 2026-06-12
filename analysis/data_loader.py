# 匯入 csv，用來修復欄位數不固定的官方 CSV
import csv

# 匯入 pandas，用來處理表格資料
import pandas as pd


# 判斷某一列是否像表頭
def looks_like_header(row):
    # 勞動部資料表頭常見關鍵字
    keywords = [
        "縣市",
        "單位",
        "公告日期",
        "處分日期",
        "事業單位",
        "名稱",
        "違反",
        "法規",
        "法條",
        "罰鍰",
        "備註",
    ]

    # 把整列合併成一段文字
    joined = " ".join(str(cell).strip() for cell in row)

    # 計算命中幾個關鍵字
    hit_count = sum(1 for keyword in keywords if keyword in joined)

    # 命中 3 個以上就視為表頭
    return hit_count >= 3


# 讀取欄位數可能不固定的 CSV
def read_messy_csv(file_path, encoding):
    # 讀取 CSV 原始列
    with open(file_path, "r", encoding=encoding, errors="replace", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)

    # 空檔案回傳空表
    if not rows:
        return pd.DataFrame()

    # 預設第一列是表頭
    header_index = 0

    # 在前 20 列中尋找最像表頭的那一列
    for index, row in enumerate(rows[:20]):
        if looks_like_header(row):
            header_index = index
            break

    # 取得表頭列
    header = [str(col).strip() for col in rows[header_index]]

    # 修正空欄位與重複欄位
    fixed_header = []
    seen = {}

    # 逐一處理欄位名稱
    for index, col in enumerate(header):
        # 如果欄位名稱為空，給它一個預設名稱
        if not col:
            col = f"未命名欄位{index + 1}"

        # 如果欄位名稱重複，加上編號
        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 1

        # 加入修正後欄位名稱
        fixed_header.append(col)

    # 更新表頭
    header = fixed_header

    # 表頭欄位數
    header_len = len(header)

    # 儲存修正後資料列
    fixed_rows = []

    # 從表頭下一列開始讀取資料
    for row in rows[header_index + 1:]:
        # 跳過完全空白列
        if not row or all(str(cell).strip() == "" for cell in row):
            continue

        # 如果資料欄位比表頭多，把多出來的欄位合併到最後一欄
        if len(row) > header_len:
            row = row[:header_len - 1] + [",".join(row[header_len - 1:])]

        # 如果資料欄位比表頭少，補空字串
        if len(row) < header_len:
            row = row + [""] * (header_len - len(row))

        # 加入修正後資料
        fixed_rows.append(row)

    # 建立 DataFrame
    df = pd.DataFrame(fixed_rows, columns=header)

    # 印出讀取狀態
    print(f"成功修復讀取 CSV：{file_path}", flush=True)
    print(f"偵測表頭：{list(df.columns)}", flush=True)
    print(f"原始資料筆數：{len(df)}", flush=True)

    # 回傳 DataFrame
    return df


# 讀取 CSV / Excel / ODS 檔案
def read_data_file(file_path):
    # 轉小寫方便判斷副檔名
    lower_path = file_path.lower()

    # 如果是 CSV
    if lower_path.endswith(".csv"):
        # 儲存最後錯誤
        last_error = None

        # 嘗試常見中文編碼
        for encoding in ["utf-8-sig", "utf-8", "cp950", "big5"]:
            try:
                # 優先使用修復讀取，避免官方 CSV 表頭不在第一列或欄位數不固定
                return read_messy_csv(file_path, encoding)

            except Exception as error:
                # 記錄錯誤
                last_error = error

        # 如果所有編碼都失敗，丟出最後錯誤
        raise last_error

    # 如果是 Excel
    if lower_path.endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)

    # 如果是 ODS
    if lower_path.endswith(".ods"):
        return pd.read_excel(file_path, engine="odf")

    # 不支援的格式直接報錯
    raise ValueError(f"不支援的資料格式：{file_path}")