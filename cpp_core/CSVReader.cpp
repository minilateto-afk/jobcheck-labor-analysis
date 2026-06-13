// 引入 CSVReader 宣告
#include "CSVReader.h"

// 引入檔案輸入功能
#include <fstream>

// 引入字串串流，用於處理欄位內容
#include <sstream>

// 引入 unordered_map，用來建立欄位名稱到欄位位置的對照
#include <unordered_map>

// 引入 cctype，用於判斷空白與數字
#include <cctype>

// 引入 iostream，用來輸出錯誤訊息
#include <iostream>

// 使用 std 命名空間，讓程式碼更簡潔
using namespace std;

vector<Record> CSVReader::load(const string& filePath) {
    // 建立儲存所有資料的 vector
    vector<Record> records;

    // 開啟 CSV 檔案
    ifstream file(filePath);

    // 如果檔案無法開啟，輸出錯誤並回傳空 vector
    if (!file.is_open()) {
        cerr << "無法開啟 CSV 檔案：" << filePath << endl;
        return records;
    }

    // 讀取第一行表頭
    string headerLine;
    if (!getline(file, headerLine)) {
        cerr << "CSV 檔案是空的：" << filePath << endl;
        return records;
    }

    // 解析表頭欄位
    vector<string> headers = splitCSVLine(headerLine);

    // 建立欄位名稱到欄位 index 的對照表
    unordered_map<string, int> columnIndex;

    // 逐一記錄每個欄位的位置
    for (int i = 0; i < static_cast<int>(headers.size()); i++) {
        // 移除 BOM 與空白，避免欄位名稱不一致
        string cleanHeader = removeBom(trim(headers[i]));

        // 將欄位名稱對應到 index
        columnIndex[cleanHeader] = i;
    }

    // 定義一個安全取得欄位的 lambda，避免欄位不存在時程式崩潰
    auto getValue = [&](const vector<string>& row, const string& columnName) -> string {
        // 如果欄位不存在，回傳空字串
        if (columnIndex.find(columnName) == columnIndex.end()) {
            return "";
        }

        // 取得欄位位置
        int index = columnIndex[columnName];

        // 如果該列欄位不足，回傳空字串
        if (index < 0 || index >= static_cast<int>(row.size())) {
            return "";
        }

        // 回傳清理後的欄位內容
        return trim(row[index]);
    };

    // 逐行讀取資料
    string line;
    while (getline(file, line)) {
        // 如果整行是空的，就跳過
        if (trim(line).empty()) {
            continue;
        }

        // 解析一行 CSV
        vector<string> row = splitCSVLine(line);

        // 建立一筆 Record
        Record record;

        // 讀取公司名稱
        record.companyName = getValue(row, "company_name");

        // 如果公司名稱是空的，就跳過這筆資料
        if (record.companyName.empty()) {
            continue;
        }

        // 讀取縣市
        record.city = getValue(row, "city");

        // 讀取公告日期
        record.announceDate = getValue(row, "announce_date");

        // 讀取處分日期
        record.penaltyDate = getValue(row, "penalty_date");

        // 讀取違反法規
        record.violatedLaw = getValue(row, "violated_law");

        // 讀取違規分類
        record.violationCategory = getValue(row, "violation_category");

        // 讀取並轉換處分金額
        record.penaltyAmount = toInt(getValue(row, "penalty_amount"));

        // 將資料加入 records
        records.push_back(record);
    }

    // 回傳讀取完成的資料
    return records;
}

vector<string> CSVReader::splitCSVLine(const string& line) {
    // 建立欄位陣列
    vector<string> fields;

    // 建立目前欄位內容
    string current;

    // 記錄目前是否在雙引號內
    bool inQuotes = false;

    // 逐字元解析 CSV
    for (size_t i = 0; i < line.size(); i++) {
        // 取得目前字元
        char c = line[i];

        // 如果遇到雙引號，切換 inQuotes 狀態
        if (c == '"') {
            // 如果是連續兩個雙引號，代表欄位中的一個雙引號
            if (inQuotes && i + 1 < line.size() && line[i + 1] == '"') {
                current += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        }
        // 如果遇到逗號且不在雙引號內，代表欄位結束
        else if (c == ',' && !inQuotes) {
            fields.push_back(current);
            current.clear();
        }
        // 其他字元直接加入目前欄位
        else {
            current += c;
        }
    }

    // 加入最後一個欄位
    fields.push_back(current);

    // 回傳欄位陣列
    return fields;
}

string CSVReader::trim(const string& text) {
    // 找到第一個不是空白的位置
    size_t start = 0;

    // 從前面移除空白
    while (start < text.size() && isspace(static_cast<unsigned char>(text[start]))) {
        start++;
    }

    // 找到最後一個不是空白的位置
    size_t end = text.size();

    // 從後面移除空白
    while (end > start && isspace(static_cast<unsigned char>(text[end - 1]))) {
        end--;
    }

    // 回傳去除前後空白後的字串
    return text.substr(start, end - start);
}

string CSVReader::removeBom(const string& text) {
    // UTF-8 BOM 的三個 byte 是 EF BB BF
    if (text.size() >= 3 &&
        static_cast<unsigned char>(text[0]) == 0xEF &&
        static_cast<unsigned char>(text[1]) == 0xBB &&
        static_cast<unsigned char>(text[2]) == 0xBF) {
        return text.substr(3);
    }

    // 如果沒有 BOM，直接回傳原字串
    return text;
}

int CSVReader::toInt(const string& text) {
    // 建立只保留數字的字串
    string digits;

    // 逐字元檢查
    for (char c : text) {
        // 如果是數字，就加入 digits
        if (isdigit(static_cast<unsigned char>(c))) {
            digits += c;
        }
    }

    // 如果沒有任何數字，回傳 0
    if (digits.empty()) {
        return 0;
    }

    // 將數字字串轉成整數
    return stoi(digits);
}