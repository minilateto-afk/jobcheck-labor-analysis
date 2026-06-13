// 引入 Statistics 宣告
#include "Statistics.h"

// 引入 map，用來統計 key-value 次數
#include <map>

// 引入 algorithm，用來排序
#include <algorithm>

// 使用 std 命名空間
using namespace std;

vector<pair<string, int>> Statistics::countByLaw(const vector<Record>& records) const {
    // 建立 map，key 是法規條款，value 是出現次數
    map<string, int> countMap;

    // 逐筆統計違反法規條款
    for (const Record& record : records) {
        // 如果法規欄位為空，就歸類為未分類法條
        string key = record.violatedLaw.empty() ? "未分類法條" : record.violatedLaw;

        // 累加該法條出現次數
        countMap[key]++;
    }

    // 回傳排序後結果
    return sortCountMap(countMap);
}

vector<pair<string, int>> Statistics::countByCategory(const vector<Record>& records) const {
    // 建立 map，key 是違規分類，value 是出現次數
    map<string, int> countMap;

    // 逐筆統計違規分類
    for (const Record& record : records) {
        // 如果分類欄位為空，就歸類為未分類
        string key = record.violationCategory.empty() ? "未分類" : record.violationCategory;

        // 累加該分類出現次數
        countMap[key]++;
    }

    // 回傳排序後結果
    return sortCountMap(countMap);
}

vector<pair<string, int>> Statistics::countByCity(const vector<Record>& records) const {
    // 建立 map，key 是縣市，value 是出現次數
    map<string, int> countMap;

    // 逐筆統計縣市
    for (const Record& record : records) {
        // 如果縣市欄位為空，就歸類為未知縣市
        string key = record.city.empty() ? "未知縣市" : record.city;

        // 累加該縣市出現次數
        countMap[key]++;
    }

    // 回傳排序後結果
    return sortCountMap(countMap);
}

vector<pair<string, int>> Statistics::sortCountMap(const map<string, int>& countMap) const {
    // 將 map 轉成 vector，方便排序
    vector<pair<string, int>> result(countMap.begin(), countMap.end());

    // 依照出現次數由大到小排序
    sort(result.begin(), result.end(), [](const pair<string, int>& a, const pair<string, int>& b) {
        // 如果次數不同，次數多的排前面
        if (a.second != b.second) {
            return a.second > b.second;
        }

        // 如果次數相同，依名稱排序，讓結果穩定
        return a.first < b.first;
    });

    // 回傳排序後結果
    return result;
}