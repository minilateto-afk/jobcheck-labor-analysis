# JobCheck 公開違反勞動法令資料查詢與分析系統

本專案以政府公開之違反勞動法令資料為基礎，建立一套可查詢、可篩選、可統計與可視覺化的資料分析系統。系統目的不是評斷企業好壞，也不是建立黑名單，而是將分散的公開資料整理成較容易閱讀的資訊，作為求職者查閱公開紀錄時的輔助參考。

---

## 一、專案特色

本專案分為兩個主要部分：

1. Python Flask Web System
   負責公開資料整理、公司查詢、公開紀錄列表、統計圖表與網頁介面。

2. C++ Core Module
   使用同一份公開資料，以 C++ 獨立實作資料檢索、統計與排序功能，展示資料結構與演算法能力。

此專題不是單純的網頁作品，而是結合：

* 政府公開資料處理
* Python Flask 網頁系統
* Pandas 資料清理
* Docker 部署
* C++ 資料結構與演算法實作
* 查詢、統計、排序與視覺化

---

## 二、系統架構

專案依照資料處理流程與功能責任進行模組化設計：

```
jobcheck-labor-analysis/
├── app.py                         # Flask 主程式，負責網站路由與頁面資料
├── config.py                      # 專案設定檔，集中管理資料路徑與系統設定
├── analysis/                      # Python 資料清理、標準化、搜尋與分析模組
├── collectors/                    # 政府公開資料下載與蒐集模組
├── data/
│   ├── raw/                       # 原始資料或範例資料
│   ├── processed/                 # Python 清理後的完整分析資料
│   └── cpp/                       # 給 C++ Core 使用的精簡資料
├── scripts/
│   └── export_cpp_dataset.py      # 將 Python 處理後資料匯出成 C++ 可讀 CSV
├── cpp_core/                      # C++ 資料結構與演算法核心模組
├── templates/                     # Flask HTML 頁面
├── static/                        # CSS、圖片與前端靜態資源
├── Dockerfile                     # Docker 建置設定
├── docker-compose.yml             # Docker Compose 啟動設定
└── README.md                      # 專案說明文件
```

---

## 三、Python Flask Web System

Python Flask 系統負責建立使用者可操作的網頁介面，將公開違反勞動法令資料整理成可查詢、可篩選與可視覺化的資訊。

主要功能包含：

* 公司名稱或關鍵字查詢
* 公開違反勞動法令紀錄列表
* 縣市、違規類型與事業單位統計
* 趨勢儀表板與資料視覺化
* 公開紀錄觀察標籤
* 資料處理流程說明
* Docker 化部署

使用技術：

* Python
* Flask
* Pandas
* HTML
* CSS
* Docker
* GitHub

---

## 四、C++ Core Module

C++ Core 使用 Python 清理後的同一份公開資料，獨立實作資料檢索、統計與排序功能。此模組不是取代 Python Flask 網站，而是補足資料結構與演算法能力。

C++ Core 展示的能力包含：

| 功能           | 使用技術           | 能力展示          |
| ------------ | -------------- | ------------- |
| 儲存所有紀錄       | vector<Record> | C++ 資料建模      |
| 公司名稱快速查詢     | unordered_map  | Hash Table 索引 |
| 公開紀錄排序       | sort           | 排序演算法         |
| 累計裁罰金額 Top-K | priority_queue | Heap / Top-K  |
| 法條與縣市統計      | map            | Key-value 統計  |
| 複雜度分析        | Big-O          | 資料結構與演算法分析    |

C++ Core 成功讀取 70,030 筆公開紀錄，並建立 31,881 個事業單位索引，使用 unordered_map 支援公司名稱查詢，並以 sort、priority_queue 與 map 完成公開紀錄排序與法條統計。

---

## 五、資料流程

本專案的資料處理流程如下：

```
政府公開資料
    ↓
collectors/ 下載資料
    ↓
analysis/ 清理、標準化、分類
    ↓
data/processed/analyzed_labor_violations.csv
    ↓
scripts/export_cpp_dataset.py 匯出精簡資料
    ↓
data/cpp/labor_records_cpp.csv
    ↓
cpp_core/ 使用 C++ 做查詢、統計與排序
```

Python 負責資料清理、欄位標準化與網頁呈現；C++ 則使用清理後資料進行資料結構與演算法實作。

---

## 六、如何啟動 Python Flask 系統

請先確認 Docker Desktop 已啟動，並在專案根目錄執行：

```
docker compose up --build
```

如果電腦使用舊版 Docker Compose，可改用：

```
docker-compose up --build
```

啟動後，在瀏覽器開啟：

```
http://localhost:5000
```

若 5000 port 被占用，可以先關閉舊容器：

```
docker compose down
```

再重新啟動：

```
docker compose up --build
```

---

## 七、如何匯出 C++ 使用資料

C++ Core 使用的是 Python 清理後的精簡資料，因此需要先執行匯出腳本。

請在專案根目錄執行：

```
python3 scripts/export_cpp_dataset.py
```

成功後會產生：

```
data/cpp/labor_records_cpp.csv
```

執行成功時，終端機會顯示類似：

```
C++ Core 資料匯出完成
輸入資料：data/processed/analyzed_labor_violations.csv
輸出資料：data/cpp/labor_records_cpp.csv
輸出筆數：70030
```

---

## 八、如何編譯與執行 C++ Core

請先進入 C++ Core 資料夾：

```
cd cpp_core
```

使用 g++ 編譯：

```
g++ -std=c++17 main.cpp CSVReader.cpp SearchIndex.cpp Statistics.cpp Ranking.cpp -o jobcheck_cpp
```

執行 C++ Core：

```
./jobcheck_cpp
```

成功後會顯示功能選單：

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

## 九、C++ Core 功能說明

### 1. 公司名稱精確查詢

使用 unordered_map 建立公司名稱索引，讓使用者輸入完整公司名稱後，可以快速查詢該事業單位的公開裁罰紀錄。

能力展示：

* Hash Table 索引
* 平均 O(1) 查詢
* vector<Record> 資料儲存
* C++ 字串處理

---

### 2. 公司名稱關鍵字搜尋

使用字串比對搜尋公司名稱中包含特定關鍵字的紀錄，適合在不知道完整公司名稱時查找資料。

能力展示：

* 字串搜尋
* vector 資料遍歷
* 查詢結果整理

---

### 3. 公開紀錄筆數 Top 10

將同一事業單位的公開紀錄彙整後，依照公開紀錄筆數排序，顯示筆數較多的前 10 個事業單位。

能力展示：

* 公司層級資料彙整
* sort 排序
* 自訂比較函式
* O(n log n) 排序概念

---

### 4. 累計裁罰金額 Top 10

將同一事業單位的裁罰金額加總後，使用 priority_queue 取得累計裁罰金額前 10 名。

能力展示：

* priority_queue
* Heap / Top-K
* 公司摘要資料結構
* 累計金額統計

---

### 5. 違反法條統計 Top 10

使用 map 統計違反法規條款出現次數，並依次數排序顯示前 10 名。

能力展示：

* map
* Key-value 統計
* 分類統計
* 資料彙整

---

### 6. 違規分類統計

使用 Python 清理後的分類欄位，統計不同違規類型的資料筆數。

能力展示：

* Python 與 C++ 資料流程銜接
* map 統計
* 分類資料分析

---

### 7. 縣市資料筆數統計

統計不同縣市或主管機關的公開資料筆數，觀察資料來源分布。

能力展示：

* map 統計
* 地區資料分布
* 公開資料整理

---

## 十、專案定位

本專題除以 Python Flask 建立公開資料查詢與視覺化系統外，另以 C++ 獨立實作資料檢索與排序模組。C++ 模組使用 unordered_map 建立公司名稱索引、map 統計違反法規條款分布、sort 與 priority_queue 進行公開紀錄排序，並整理各功能時間複雜度，以展示資料結構、演算法與系統效能設計能力。

此設計讓專案同時展現：

* Python 資料處理能力
* Flask 網頁系統開發能力
* Docker 部署能力
* C++ 程式設計能力
* 資料結構與演算法能力
* 公開資料應用能力

---

## 十一、資料倫理與系統限制

本系統僅整理政府公開資料，不對企業現況進行主觀評價。

系統限制如下：

* 本系統僅整理已公開公告之資料。
* 未出現在資料中的公司，不代表一定沒有勞動爭議。
* 公開裁罰紀錄僅代表過去公告資料，不代表企業目前狀況。
* 系統不使用黑名單、風險分數或主觀評價。
* 不同縣市公開資料格式可能不同，因此需要進行欄位標準化與缺值處理。
* 部分縣市可能因外部網站連線狀態或格式差異，導致資料匯入不完整。
* 後續可擴充公告日期篩選、公司名稱模糊比對、資料更新時間顯示與更細緻的分類規則。

---

## 十二、作品集說明文字

在作品集中，本專題可整理為以下說明：

本專題以政府公開違反勞動法令資料為基礎，建立公開紀錄查詢與分析系統。Python Flask 網頁系統負責資料查詢、篩選、統計圖表與使用者介面；另新增 C++ Core 模組，使用同一份清理後資料實作資料檢索、統計與排序。C++ 模組以 unordered_map 建立公司名稱索引、以 map 統計違反法條與縣市分布，並透過 sort 與 priority_queue 完成公開紀錄 Top-K 排序，補足資料結構與演算法能力。系統不建立黑名單或主觀風險分數，而是以中性方式整理公開資料，作為求職者查閱公開紀錄時的輔助參考。

---

## 十三、後續改進方向

後續可改進方向包含：

* 增加公告日期區間篩選
* 增加公司名稱模糊比對
* 增加資料更新時間顯示
* 增加更多縣市資料格式相容處理
* 將 C++ Core 的效能測試結果整理成表格
* 比較線性搜尋與 unordered_map 查詢速度差異
* 將查詢結果匯出成 CSV
* 加入更完整的測試資料與 README 截圖
