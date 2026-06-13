#ifndef SEARCH_INDEX_H
#define SEARCH_INDEX_H

// 引入 Record 結構
#include "Record.h"

// 引入 string
#include <string>

// 引入 vector
#include <vector>

// 引入 unordered_map，用來建立公司名稱索引
#include <unordered_map>

// SearchIndex 負責建立公司名稱查詢索引
class SearchIndex {
public:
    // build 負責用所有 Record 建立索引
    void build(const std::vector<Record>& records);

    // searchExact 負責精確查詢公司名稱
    std::vector<Record> searchExact(const std::vector<Record>& records, const std::string& companyName) const;

    // searchKeyword 負責用關鍵字搜尋公司名稱
    std::vector<Record> searchKeyword(const std::vector<Record>& records, const std::string& keyword) const;

    // countIndexedCompanies 回傳索引中的公司數量
    int countIndexedCompanies() const;

private:
    // companyIndex 使用公司名稱對應到 records 裡的 index 陣列
    std::unordered_map<std::string, std::vector<int>> companyIndex;
};

#endif