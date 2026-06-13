// 引入 Ranking 宣告
#include "Ranking.h"

// 引入 unordered_map，用公司名稱彙整資料
#include <unordered_map>

// 引入 algorithm，用於 sort 排序
#include <algorithm>

// 引入 queue，用於 priority_queue
#include <queue>

// 引入 cctype，用於判斷數字
#include <cctype>

// 使用 std 命名空間
using namespace std;

vector<CompanySummary> Ranking::summarizeCompanies(const vector<Record>& records) const {
    // 建立公司名稱到摘要的對照表
    unordered_map<string, CompanySummary> summaryMap;

    // 逐筆整理 Record
    for (const Record& record : records) {
        // 如果公司名稱為空，跳過
        if (record.companyName.empty()) {
            continue;
        }

        // 如果公司第一次出現，就建立初始摘要
        if (summaryMap.find(record.companyName) == summaryMap.end()) {
            CompanySummary summary;
            summary.companyName = record.companyName;
            summary.recordCount = 0;
            summary.totalPenaltyAmount = 0;
            summary.latestAnnounceDate = "";
            summaryMap[record.companyName] = summary;
        }

        // 取得公司摘要
        CompanySummary& summary = summaryMap[record.companyName];

        // 累加公開紀錄筆數
        summary.recordCount++;

        // 累加處分金額
        summary.totalPenaltyAmount += record.penaltyAmount;

        // 將日期轉成可比較的 key
        string currentDateKey = normalizeDateKey(record.announceDate);
        string latestDateKey = normalizeDateKey(summary.latestAnnounceDate);

        // 如果目前紀錄日期比較新，就更新最近公告日期
        if (currentDateKey > latestDateKey) {
            summary.latestAnnounceDate = record.announceDate;
        }
    }

    // 將 unordered_map 轉成 vector
    vector<CompanySummary> summaries;

    // 逐一加入結果陣列
    for (const auto& pair : summaryMap) {
        summaries.push_back(pair.second);
    }

    // 回傳公司摘要
    return summaries;
}

vector<CompanySummary> Ranking::topByRecordCount(const vector<Record>& records, int k) const {
    // 先整理公司層級摘要
    vector<CompanySummary> summaries = summarizeCompanies(records);

    // 依公開紀錄筆數由大到小排序
    sort(summaries.begin(), summaries.end(), [](const CompanySummary& a, const CompanySummary& b) {
        // 如果筆數不同，筆數多的排前面
        if (a.recordCount != b.recordCount) {
            return a.recordCount > b.recordCount;
        }

        // 如果筆數相同，累計金額高的排前面
        if (a.totalPenaltyAmount != b.totalPenaltyAmount) {
            return a.totalPenaltyAmount > b.totalPenaltyAmount;
        }

        // 如果還是相同，依公司名稱排序
        return a.companyName < b.companyName;
    });

    // 如果資料筆數超過 k，就只保留前 k 筆
    if (static_cast<int>(summaries.size()) > k) {
        summaries.resize(k);
    }

    // 回傳 Top-K 結果
    return summaries;
}

vector<CompanySummary> Ranking::topByPenaltyAmount(const vector<Record>& records, int k) const {
    // 先整理公司層級摘要
    vector<CompanySummary> summaries = summarizeCompanies(records);

    // 建立 priority_queue 的比較規則，金額越高優先度越高
    auto compare = [](const CompanySummary& a, const CompanySummary& b) {
        // priority_queue 預設會把「比較結果為 false」的放前面
        return a.totalPenaltyAmount < b.totalPenaltyAmount;
    };

    // 建立 priority_queue，用來展示 Heap / Top-K 概念
    priority_queue<CompanySummary, vector<CompanySummary>, decltype(compare)> heap(compare);

    // 將所有公司摘要放入 heap
    for (const CompanySummary& summary : summaries) {
        heap.push(summary);
    }

    // 取出前 k 名
    vector<CompanySummary> result;

    // 只要 heap 不空且還沒取滿 k 筆，就持續取出
    while (!heap.empty() && static_cast<int>(result.size()) < k) {
        result.push_back(heap.top());
        heap.pop();
    }

    // 回傳 Top-K 結果
    return result;
}

string Ranking::normalizeDateKey(const string& dateText) const {
    // 建立只保留數字的字串
    string digits;

    // 逐字元檢查日期字串
    for (char c : dateText) {
        // 如果是數字，就加入 digits
        if (isdigit(static_cast<unsigned char>(c))) {
            digits += c;
        }
    }

    // 如果沒有日期，就回傳空字串
    if (digits.empty()) {
        return "";
    }

    // 回傳數字字串，用於簡單比較
    return digits;
}