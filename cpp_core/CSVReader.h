#ifndef CSV_READER_H
#define CSV_READER_H

// 引入 Record 結構，讓 CSVReader 可以回傳 Record 資料
#include "Record.h"

// 引入 string，用來表示檔案路徑
#include <string>

// 引入 vector，用來儲存多筆 Record
#include <vector>

// CSVReader 負責讀取 C++ Core 使用的精簡 CSV
class CSVReader {
public:
    // load 函式讀取 CSV 檔案，並回傳 Record 陣列
    std::vector<Record> load(const std::string& filePath);

private:
    // splitCSVLine 負責解析一行 CSV，支援雙引號包住的逗號
    std::vector<std::string> splitCSVLine(const std::string& line);

    // trim 負責清除字串前後空白
    std::string trim(const std::string& text);

    // removeBom 負責移除 UTF-8 BOM，避免第一個欄位名稱讀錯
    std::string removeBom(const std::string& text);

    // toInt 負責將金額文字轉成整數
    int toInt(const std::string& text);
};

#endif