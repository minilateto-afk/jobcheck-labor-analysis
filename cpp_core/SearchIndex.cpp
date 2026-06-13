// 引入 SearchIndex 宣告
#include "SearchIndex.h"

// 使用 std 命名空間，讓程式碼更簡潔
using namespace std;

void SearchIndex::build(const vector<Record>& records) {
    // 清空舊索引，避免重複 build 時資料重複
    companyIndex.clear();

    // 逐筆資料建立公司名稱索引
    for (int i = 0; i < static_cast<int>(records.size()); i++) {
        // 取得公司名稱
        string companyName = records[i].companyName;

        // 如果公司名稱為空，跳過
        if (companyName.empty()) {
            continue;
        }

        // 將這筆資料的 index 加入該公司名稱底下
        companyIndex[companyName].push_back(i);
    }
}

vector<Record> SearchIndex::searchExact(const vector<Record>& records, const string& companyName) const {
    // 建立查詢結果
    vector<Record> results;

    // 在 unordered_map 中查詢公司名稱
    auto it = companyIndex.find(companyName);

    // 如果找不到公司名稱，回傳空結果
    if (it == companyIndex.end()) {
        return results;
    }

    // 根據 index 取出對應的 Record
    for (int recordIndex : it->second) {
        // 確認 index 在合法範圍內
        if (recordIndex >= 0 && recordIndex < static_cast<int>(records.size())) {
            results.push_back(records[recordIndex]);
        }
    }

    // 回傳查詢結果
    return results;
}

vector<Record> SearchIndex::searchKeyword(const vector<Record>& records, const string& keyword) const {
    // 建立查詢結果
    vector<Record> results;

    // 如果關鍵字是空的，直接回傳空結果
    if (keyword.empty()) {
        return results;
    }

    // 逐一檢查索引中的公司名稱是否包含關鍵字
    for (const auto& pair : companyIndex) {
        // 取得公司名稱
        const string& companyName = pair.first;

        // 如果公司名稱包含關鍵字
        if (companyName.find(keyword) != string::npos) {
            // 取出該公司的所有紀錄
            for (int recordIndex : pair.second) {
                // 確認 index 在合法範圍內
                if (recordIndex >= 0 && recordIndex < static_cast<int>(records.size())) {
                    results.push_back(records[recordIndex]);
                }
            }
        }
    }

    // 回傳查詢結果
    return results;
}

int SearchIndex::countIndexedCompanies() const {
    // 回傳 unordered_map 裡不同公司名稱的數量
    return static_cast<int>(companyIndex.size());
}