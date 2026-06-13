# JobCheck 公開違反勞動法令資料查詢與分析系統

<!-- 說明專案定位，避免被理解成黑名單或主觀風險評分 -->
本專案以政府公開之違反勞動法令資料為基礎，建立一套可查詢、可篩選、可統計與可視覺化的資料分析系統。系統目的不是評斷企業好壞，也不是建立黑名單，而是將分散的公開資料整理成較容易閱讀的資訊，作為求職者查閱公開紀錄時的輔助參考。

---

## 專案特色

<!-- 說明這個作品不是只有網頁，而是包含資料處理、系統開發與 C++ 資料結構 -->
本專案分為兩個主要部分：

1. **Python Flask Web System**  
   負責公開資料整理、公司查詢、公開紀錄列表、統計圖表與網頁介面。

2. **C++ Core Module**  
   使用同一份公開資料，以 C++ 獨立實作資料檢索、統計與排序功能，展示資料結構與演算法能力。

---

## 系統架構

<!-- 用資料夾結構說明每個區塊的責任 -->
```text
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