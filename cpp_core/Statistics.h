#ifndef STATISTICS_H
#define STATISTICS_H

// 引入 Record 結構
#include "Record.h"

// 引入 string
#include <string>

// 引入 vector
#include <vector>

// 引入 pair
#include <utility>

// 引入 map，因為 private 函式會使用 std::map
#include <map>

// Statistics 負責統計公開資料中的分類數量
class Statistics {
public:
    // countByLaw 統計違反法規條款出現次數
    std::vector<std::pair<std::string, int>> countByLaw(const std::vector<Record>& records) const;

    // countByCategory 統計違規分類出現次數
    std::vector<std::pair<std::string, int>> countByCategory(const std::vector<Record>& records) const;

    // countByCity 統計縣市資料筆數
    std::vector<std::pair<std::string, int>> countByCity(const std::vector<Record>& records) const;

private:
    // sortCountMap 將統計結果依次數由大到小排序
    std::vector<std::pair<std::string, int>> sortCountMap(const std::map<std::string, int>& countMap) const;
};

#endif