// 引入 C++ Core 各模組
#include "CSVReader.h"
#include "SearchIndex.h"
#include "Statistics.h"
#include "Ranking.h"

// 引入 iostream，用來輸入輸出
#include <iostream>

// 引入 iomanip，用來格式化輸出
#include <iomanip>

// 引入 filesystem，用來檢查資料檔案是否存在
#include <filesystem>

// 使用 std 命名空間
using namespace std;

// namespace fs 讓 filesystem 使用更簡潔
namespace fs = std::filesystem;

// findDatasetPath 負責尋找 C++ 使用的 CSV 資料路徑
string findDatasetPath() {
    // 如果從 cpp_core/ 資料夾執行，使用這個相對路徑
    string pathFromCppCore = "../data/cpp/labor_records_cpp.csv";

    // 如果從專案根目錄執行，使用這個相對路徑
    string pathFromRoot = "data/cpp/labor_records_cpp.csv";

    // 檢查 cpp_core 執行路徑
    if (fs::exists(pathFromCppCore)) {
        return pathFromCppCore;
    }

    // 檢查根目錄執行路徑
    if (fs::exists(pathFromRoot)) {
        return pathFromRoot;
    }

    // 如果都找不到，回傳預設路徑
    return pathFromCppCore;
}

// printRecord 負責印出單筆公開紀錄
void printRecord(const Record& record, int index) {
    // 印出序號
    cout << "[" << index << "] ";

    // 印出公司名稱與縣市
    cout << record.companyName << "｜" << record.city << endl;

    // 印出公告日期與處分日期
    cout << "    公告日期：" << record.announceDate << "｜處分日期：" << record.penaltyDate << endl;

    // 印出違反法規
    cout << "    違反法規：" << record.violatedLaw << endl;

    // 印出違規分類
    cout << "    違規分類：" << record.violationCategory << endl;

    // 印出處分金額
    cout << "    處分金額：" << record.penaltyAmount << " 元" << endl;
}

// printRecords 負責印出多筆查詢結果
void printRecords(const vector<Record>& records) {
    // 如果查無資料，顯示提示
    if (records.empty()) {
        cout << "查無符合資料。" << endl;
        return;
    }

    // 顯示查詢結果總數
    cout << "共找到 " << records.size() << " 筆公開紀錄。" << endl;

    // 最多只顯示前 20 筆，避免終端機太長
    int limit = min(static_cast<int>(records.size()), 20);

    // 逐筆印出資料
    for (int i = 0; i < limit; i++) {
        printRecord(records[i], i + 1);
    }

    // 如果資料超過 20 筆，提示只顯示部分資料
    if (static_cast<int>(records.size()) > limit) {
        cout << "僅顯示前 " << limit << " 筆，其餘資料省略。" << endl;
    }
}

// printCompanySummaries 負責印出公司排序結果
void printCompanySummaries(const vector<CompanySummary>& summaries) {
    // 如果沒有資料，顯示提示
    if (summaries.empty()) {
        cout << "目前沒有可排序資料。" << endl;
        return;
    }

    // 印出表頭
    cout << left << setw(6) << "排名"
         << setw(36) << "公司名稱"
         << setw(12) << "紀錄筆數"
         << setw(16) << "累計金額"
         << "最近公告日期" << endl;

    // 印出分隔線
    cout << string(90, '-') << endl;

    // 逐筆印出公司摘要
    for (int i = 0; i < static_cast<int>(summaries.size()); i++) {
        cout << left << setw(6) << (i + 1)
             << setw(36) << summaries[i].companyName.substr(0, 34)
             << setw(12) << summaries[i].recordCount
             << setw(16) << summaries[i].totalPenaltyAmount
             << summaries[i].latestAnnounceDate << endl;
    }
}

// printCountPairs 負責印出統計結果
void printCountPairs(const vector<pair<string, int>>& pairs, int limit) {
    // 如果沒有統計資料，顯示提示
    if (pairs.empty()) {
        cout << "目前沒有統計資料。" << endl;
        return;
    }

    // 限制顯示筆數
    int showCount = min(static_cast<int>(pairs.size()), limit);

    // 印出統計結果
    for (int i = 0; i < showCount; i++) {
        cout << "[" << (i + 1) << "] " << pairs[i].first << "："
             << pairs[i].second << " 筆" << endl;
    }
}

// printMenu 負責顯示功能選單
void printMenu() {
    // 印出主選單
    cout << endl;
    cout << "=== C++ 公開裁罰資料檢索與排序模組 ===" << endl;
    cout << "1. 公司名稱精確查詢" << endl;
    cout << "2. 公司名稱關鍵字搜尋" << endl;
    cout << "3. 公開紀錄筆數 Top 10" << endl;
    cout << "4. 累計裁罰金額 Top 10" << endl;
    cout << "5. 違反法條統計 Top 10" << endl;
    cout << "6. 違規分類統計" << endl;
    cout << "7. 縣市資料筆數統計" << endl;
    cout << "0. 離開" << endl;
    cout << "請輸入功能編號：";
}

int main() {
    // 顯示程式定位
    cout << "JobCheck C++ Core Module" << endl;
    cout << "本模組使用 C++ 實作資料檢索、統計與排序，展示資料結構與演算法能力。" << endl;

    // 尋找資料檔案路徑
    string datasetPath = findDatasetPath();

    // 建立 CSVReader
    CSVReader reader;

    // 讀取資料
    vector<Record> records = reader.load(datasetPath);

    // 如果資料讀取失敗，提示使用者先執行匯出腳本
    if (records.empty()) {
        cout << "沒有讀取到資料。" << endl;
        cout << "請先在專案根目錄執行：" << endl;
        cout << "python scripts/export_cpp_dataset.py" << endl;
        return 1;
    }

    // 建立公司名稱索引
    SearchIndex searchIndex;
    searchIndex.build(records);

    // 建立統計模組
    Statistics statistics;

    // 建立排序模組
    Ranking ranking;

    // 顯示資料載入結果
    cout << "資料載入成功：" << records.size() << " 筆公開紀錄" << endl;
    cout << "已建立公司索引：" << searchIndex.countIndexedCompanies() << " 個事業單位" << endl;
    cout << "資料來源：" << datasetPath << endl;

    // 主選單迴圈
    while (true) {
        // 顯示選單
        printMenu();

        // 讀取使用者輸入
        string choice;
        getline(cin, choice);

        // 如果選擇 0，就離開程式
        if (choice == "0") {
            cout << "已離開 C++ Core 模組。" << endl;
            break;
        }

        // 公司名稱精確查詢
        if (choice == "1") {
            cout << "請輸入完整公司名稱：";
            string companyName;
            getline(cin, companyName);

            // 使用 unordered_map 查詢
            vector<Record> results = searchIndex.searchExact(records, companyName);

            // 印出結果
            printRecords(results);
        }
        // 公司名稱關鍵字搜尋
        else if (choice == "2") {
            cout << "請輸入公司名稱關鍵字：";
            string keyword;
            getline(cin, keyword);

            // 使用關鍵字搜尋
            vector<Record> results = searchIndex.searchKeyword(records, keyword);

            // 印出結果
            printRecords(results);
        }
        // 公開紀錄筆數 Top 10
        else if (choice == "3") {
            // 使用 sort 取得公開紀錄筆數 Top 10
            vector<CompanySummary> topCompanies = ranking.topByRecordCount(records, 10);

            // 顯示結果
            cout << "公開紀錄筆數 Top 10" << endl;
            printCompanySummaries(topCompanies);
        }
        // 累計裁罰金額 Top 10
        else if (choice == "4") {
            // 使用 priority_queue 取得累計裁罰金額 Top 10
            vector<CompanySummary> topCompanies = ranking.topByPenaltyAmount(records, 10);

            // 顯示結果
            cout << "累計裁罰金額 Top 10" << endl;
            printCompanySummaries(topCompanies);
        }
        // 違反法條統計 Top 10
        else if (choice == "5") {
            // 使用 map 統計法條
            vector<pair<string, int>> lawStats = statistics.countByLaw(records);

            // 顯示前 10 名
            cout << "違反法條統計 Top 10" << endl;
            printCountPairs(lawStats, 10);
        }
        // 違規分類統計
        else if (choice == "6") {
            // 使用 map 統計違規分類
            vector<pair<string, int>> categoryStats = statistics.countByCategory(records);

            // 顯示前 10 名
            cout << "違規分類統計" << endl;
            printCountPairs(categoryStats, 10);
        }
        // 縣市資料筆數統計
        else if (choice == "7") {
            // 使用 map 統計縣市
            vector<pair<string, int>> cityStats = statistics.countByCity(records);

            // 顯示前 20 名
            cout << "縣市資料筆數統計" << endl;
            printCountPairs(cityStats, 20);
        }
        // 其他輸入視為無效
        else {
            cout << "無效的功能編號，請重新輸入。" << endl;
        }
    }

    // 程式正常結束
    return 0;
}