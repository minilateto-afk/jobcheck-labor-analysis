#ifndef RANKING_H
#define RANKING_H

// 引入 Record 結構
#include "Record.h"

// 引入 string
#include <string>

// 引入 vector
#include <vector>

// CompanySummary 代表同一間公司的統計摘要
struct CompanySummary {
    // 公司名稱
    std::string companyName;

    // 公開紀錄筆數
    int recordCount;

    // 累計處分金額
    long long totalPenaltyAmount;

    // 最近一次公告日期，用字串保存
    std::string latestAnnounceDate;
};

// Ranking 負責處理公司公開紀錄排序
class Ranking {
public:
    // summarizeCompanies 將多筆 Record 彙整成公司層級摘要
    std::vector<CompanySummary> summarizeCompanies(const std::vector<Record>& records) const;

    // topByRecordCount 依公開紀錄筆數排序，取前 k 名
    std::vector<CompanySummary> topByRecordCount(const std::vector<Record>& records, int k) const;

    // topByPenaltyAmount 使用 priority_queue 依累計處分金額取前 k 名
    std::vector<CompanySummary> topByPenaltyAmount(const std::vector<Record>& records, int k) const;

private:
    // normalizeDateKey 將日期字串轉成方便比較的數字字串
    std::string normalizeDateKey(const std::string& dateText) const;
};

#endif