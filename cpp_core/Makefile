# 設定 C++ 編譯器
CXX = g++

# 設定 C++ 版本與警告提示
CXXFLAGS = -std=c++17 -Wall -Wextra

# 設定輸出執行檔名稱
TARGET = jobcheck_cpp

# 設定需要編譯的原始碼檔案
SOURCES = main.cpp CSVReader.cpp SearchIndex.cpp Statistics.cpp Ranking.cpp

# 預設指令：編譯專案
all:
	$(CXX) $(CXXFLAGS) $(SOURCES) -o $(TARGET)

# 清除編譯後的執行檔
clean:
	rm -f $(TARGET)