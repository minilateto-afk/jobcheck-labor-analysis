# C++ Core：公開裁罰資料檢索與排序模組

本模組是 JobCheck 公開違反勞動法令資料查詢與分析系統中的 C++ 資料結構與演算法核心。Python Flask 系統負責資料清理、網頁查詢與資料視覺化；C++ Core 則使用同一份清理後資料，獨立實作資料檢索、統計與排序功能，用來展示 C++、資料結構、演算法與時間複雜度分析能力。

---

## 一、模組定位

C++ Core 不是取代 Python Flask 網站，而是作為同一專題中的核心能力補強。

Python Flask Web System 主要負責：

* 資料清理
* 網頁介面
* 公司查詢
* 條件篩選
* 統計圖表
* 使用者操作
* Docker 部署

C++ Core Module 主要負責：

* 使用 C++ 讀取精簡 CSV 資料
* 建立公司名稱索引
* 實作公司查詢
* 統計違反法條、違規分類與縣市分布
* 完成公開紀錄筆數排序
* 完成累計裁罰金額 Top-K 排序
* 整理資料結構與時間複雜度

此模組的重點不是做出漂亮介面，而是證明具備資料結構、演算法與 C++ 基礎實作能力。

---

## 二、使用資料

本模組讀取以下資料：

```
../data/cpp/labor_records_cpp.csv
```

這份資料由專案根目錄的 Python 腳本產生：

```
python3 scripts/export_cpp_dataset.py
```

資料來源流程如下：

```
data/processed/analyzed_labor_violations.csv
    ↓
scripts/export_cpp_dataset.py
    ↓
data/cpp/labor_records_cpp.csv
    ↓
cpp_core/ C++ Core 讀取並進行查詢、統計與排序
```

C++ Core 使用的是 Python 清理後的精簡資料，避免 C++ 直接處理不同縣市原始資料格式差異，讓模組重點放在資料結構與演算法實作。

---

## 三、檔案架構

```
cpp_core/
├── README.md             # C++ Core 說明文件
├── main.cpp              # 主程式與終端機選單
├── Record.h              # 定義單筆公開紀錄資料結構
├── CSVReader.h           # CSVReader 類別宣告
├── CSVReader.cpp         # CSV 讀取與解析實作
├── SearchIndex.h         # SearchIndex 類別宣告
├── SearchIndex.cpp       # unordered_map 公司名稱索引實作
├── Statistics.h          # Statistics 類別宣告
├── Statistics.cpp        # map 統計法條、分類與縣市
├── Ranking.h             # Ranking 類別與 CompanySummary 宣告
├── Ranking.cpp           # sort 與 priority_queue 排序實作
└── Makefile              # 可選，簡化編譯指令
```

---

## 四、各檔案功能說明

### main.cpp

主程式入口，負責：

* 顯示 C++ Core 模組說明
* 讀取資料檔路徑
* 呼叫 CSVReader 載入資料
* 建立 SearchIndex 公司名稱索引
* 顯示終端機功能選單
* 呼叫查詢、統計與排序功能
* 顯示執行結果

此檔案主要負責流程控制，不把所有邏輯塞在一起，讓專案具有模組化設計。

---

### Record.h

定義單筆公開裁罰紀錄的資料結構。

Record 包含：

* companyName：事業單位名稱
* city：縣市或主管機關
* announceDate：公告日期
* penaltyDate：處分日期
* violatedLaw：違反法規條款
* violationCategory：違規分類
* penaltyAmount：處分金額

使用 struct Record 可以將 CSV 中的一列資料轉換成 C++ 可操作的資料物件。

---

### CSVReader.h / CSVReader.cpp

負責讀取 C++ Core 使用的 CSV 資料。

功能包含：

* 開啟 CSV 檔案
* 讀取表頭
* 解析每一列資料
* 處理 UTF-8 BOM
* 處理雙引號與逗號
* 將金額文字轉成整數
* 將資料轉成 vector<Record>

能力展示：

* 檔案讀取
* 字串解析
* vector 資料儲存
* C++ 基礎資料處理

---

### SearchIndex.h / SearchIndex.cpp

負責建立公司名稱查詢索引。

使用資料結構：

* unordered_map<string, vector<int>>

設計邏輯：

* key：公司名稱
* value：該公司在 records 陣列中的資料位置

功能包含：

* 建立公司名稱索引
* 公司名稱精確查詢
* 公司名稱關鍵字搜尋
* 統計已建立索引的公司數量

能力展示：

* Hash Table
* 平均 O(1) 查詢
* 索引設計
* 資料結構應用

---

### Statistics.h / Statistics.cpp

負責統計公開資料中的分類數量。

使用資料結構：

* map<string, int>

功能包含：

* 違反法條統計
* 違規分類統計
* 縣市資料筆數統計
* 統計結果排序

能力展示：

* map key-value 統計
* 分類資料彙整
* 統計結果排序
* 資料分析基礎

---

### Ranking.h / Ranking.cpp

負責公司層級資料彙整與排序。

使用資料結構與演算法：

* unordered_map：彙整同一公司資料
* sort：公開紀錄筆數排序
* priority_queue：累計裁罰金額 Top-K
* CompanySummary：公司摘要資料結構

功能包含：

* 彙整公司公開紀錄筆數
* 加總公司累計裁罰金額
* 找出公開紀錄筆數 Top 10
* 找出累計裁罰金額 Top 10
* 記錄最近公告日期

能力展示：

* 排序演算法
* Heap / Top-K
* 公司層級資料彙整
* 自訂資料結構設計

---

## 五、使用資料結構與演算法

| 功能           | 使用技術           | 複雜度概念      | 能力展示          |
| ------------ | -------------- | ---------- | ------------- |
| 儲存所有紀錄       | vector<Record> | O(n)       | C++ 資料建模      |
| 公司名稱查詢       | unordered_map  | 平均 O(1)    | Hash Table 索引 |
| 關鍵字搜尋        | 字串比對           | O(n)       | 基礎搜尋          |
| 法條統計         | map            | O(n log m) | Key-value 統計  |
| 公開紀錄筆數排序     | sort           | O(n log n) | 排序演算法         |
| 累計裁罰金額 Top-K | priority_queue | O(n log n) | Heap / Top-K  |
| 公司資料彙整       | unordered_map  | 平均 O(n)    | 分組統計          |

---

## 六、功能選單

執行 C++ Core 後，會顯示以下選單：

```
=== C++ 公開裁罰資料檢索與排序模組 ===
1. 公司名稱精確查詢
2. 公司名稱關鍵字搜尋
3. 公開紀錄筆數 Top 10
4. 累計裁罰金額 Top 10
5. 違反法條統計 Top 10
6. 違規分類統計
7. 縣市資料筆數統計
0. 離開
```

---

## 七、編譯方式

請先確認已在專案根目錄執行資料匯出：

```
python3 scripts/export_cpp_dataset.py
```

接著進入 C++ Core 資料夾：

```
cd cpp_core
```

使用 g++ 編譯：

```
g++ -std=c++17 main.cpp CSVReader.cpp SearchIndex.cpp Statistics.cpp Ranking.cpp -o jobcheck_cpp
```

如果有加入 Makefile，也可以使用：

```
make
```

---

## 八、執行方式

編譯完成後執行：

```
./jobcheck_cpp
```

如果是在 Windows 環境，可以執行：

```
jobcheck_cpp.exe
```

成功執行後會顯示：

```
JobCheck C++ Core Module
本模組使用 C++ 實作資料檢索、統計與排序，展示資料結構與演算法能力。
資料載入成功：70030 筆公開紀錄
已建立公司索引：31881 個事業單位
資料來源：../data/cpp/labor_records_cpp.csv
```

---

## 九、測試建議

建議依序測試以下功能：

1. 輸入 3
   測試公開紀錄筆數 Top 10，確認 sort 排序功能正常。

2. 輸入 4
   測試累計裁罰金額 Top 10，確認 priority_queue 功能正常。

3. 輸入 5
   測試違反法條統計 Top 10，確認 map 統計功能正常。

4. 輸入 2
   測試公司名稱關鍵字搜尋，例如輸入「科技」或「股份有限公司」。

5. 輸入 1
   使用完整公司名稱測試精確查詢。

---

## 十、執行成果

目前 C++ Core 已成功完成：

* 讀取 70,030 筆公開紀錄
* 建立 31,881 個事業單位索引
* 支援公司名稱精確查詢
* 支援公司名稱關鍵字搜尋
* 支援公開紀錄筆數 Top 10 排序
* 支援累計裁罰金額 Top 10 排序
* 支援違反法條統計
* 支援違規分類統計
* 支援縣市資料筆數統計

---

## 十一、作品集說明文字

本模組以 C++ 實作公開裁罰資料檢索與排序核心，使用 unordered_map 建立公司名稱索引，將公司查詢由逐筆搜尋優化為平均 O(1)；使用 map 統計違反法規條款、違規分類與縣市資料筆數；使用 sort 與 priority_queue 完成公開紀錄筆數與累計裁罰金額 Top-K 排序，展示資料結構、演算法與系統效能設計能力。

---

## 十二、專案限制

本模組目前仍有以下限制：

* 公司名稱精確查詢需要輸入完整名稱。
* 關鍵字搜尋仍採線性搜尋，未實作 Trie 或更進階的字串索引。
* 日期目前以字串方式保存，未完整轉換成日期物件。
* C++ Core 目前不直接連接 Flask 網站，而是作為獨立終端機模組執行。
* 本模組僅整理公開資料，不對企業現況做主觀評價。

---

## 十三、後續改進方向

後續可改進方向包含：

* 加入 Trie 或更進階的公司名稱搜尋索引
* 加入線性搜尋與 unordered_map 查詢時間比較
* 加入查詢結果匯出 CSV
* 加入公告日期區間篩選
* 加入更完整的單元測試
* 將效能測試結果整理成表格
* 將 C++ Core 的輸出結果截圖放入 screenshots 資料夾
