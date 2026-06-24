# Data Engineering Camp - Python 爬蟲練習

本專案包含 PTT、Hahow、FinMind 等網站的 Python 爬蟲範例。

## 環境需求

- Python 3.10+

## 方法一：venv + pip（基礎）

```bash
# 建立虛擬環境
python3 -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 安裝套件
pip install -r requirements.txt

# 測試執行
python3 test.py

# 離開虛擬環境
deactivate
```

## 方法二：uv（進階）

[uv](https://docs.astral.sh/uv/) 是更快速的 Python 套件管理工具。

```bash
# 安裝 uv（如果還沒裝）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 用 uv 建立虛擬環境並安裝套件
uv venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
uv pip install -r requirements.txt

# 測試執行
python3 test.py

# 離開虛擬環境
deactivate
```

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `ptt_crawler.py` | PTT 看板爬蟲 |
| `ptt.ipynb` | PTT 爬蟲 Notebook 版 |
| `hahow_crawler.py` | Hahow 課程爬蟲 |
| `finmind.py` | FinMind 股票資料查詢 |
| `test.py` | requests 基本測試 |
| `test.ipynb` | 測試用 Notebook |
| `tqdm_test.py` | tqdm 進度條範例 |
