#ifndef RECORD_H
#define RECORD_H

// 引入 string，讓 Record 可以儲存中文文字與日期字串
#include <string>

// 使用 std 命名空間中的 string，避免每次都寫 std::string
using std::string;

// Record 代表公開資料中的一筆裁罰紀錄
struct Record {
    // 事業單位名稱，用來做公司查詢與統計
    string companyName;

    // 縣市或主管機關，用來做地區統計
    string city;

    // 公告日期，用字串保存，避免民國年格式轉換太複雜
    string announceDate;

    // 處分日期，用字串保存
    string penaltyDate;

    // 違反法規條款，例如勞動基準法第24條
    string violatedLaw;

    // Python 分類後的違規類型，例如工時問題、薪資／加班費問題
    string violationCategory;

    // 處分金額，轉成 int 方便排序與加總
    int penaltyAmount;
};

#endif