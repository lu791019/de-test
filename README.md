# TibaMe 雲端資料工程師 — 課程教材

> 帶狀課 21 集教學用 repo

## 學習路線

### Season 0：基礎建置（EP01-04）

| EP | 主題 | 資料夾 | 操作手冊 |
|----|------|--------|---------|
| EP01 | WSL + VS Code + Git | [ep01/](ep01/) | [環境建置](操作手冊_環境建置.md) |
| EP02 | Git + GitHub + uv + Module/Package | [ep02/](ep02/) | [環境建置](操作手冊_環境建置.md) · [Git 協作](Git_GitHub開發協作手冊.md) |
| EP03 | Docker 安裝 + Dockerfile | [ep03-04/](ep03-04/) | [Docker 安裝](Docker安裝教學手冊.md) · [Docker 操作](Docker_Compose開發操作手冊.md) |
| EP04 | Docker Compose + 完整系統 | [ep03-04/](ep03-04/) | [Docker 實作](Docker實作操作手冊.md) |

### Season 1+：爬蟲系統（EP05 開始）

| Repo | 主題 | 
|------|------|
| [stock-crawler](https://github.com/lu791019/stock-crawler-de-course-materials) | FinMind MVP 股價爬蟲（漸進式教學設計，中文註解） | 
| [hahow-crawler](https://github.com/lu791019/hahow-crawler-de-course-materials) | Hahow 課程爬蟲（Airflow + BigQuery 完整 pipeline） | 

> 課堂會擇一來教學和實作

## 操作手冊

| 手冊 | 內容 | 什麼時候看 |
|------|------|-----------|
| [操作手冊](操作手冊_環境建置.md) | WSL → VS Code → Git → uv → Module/Package | EP01-02 跟著做 |
| [Docker 安裝手冊](Docker安裝教學手冊.md) | Docker Engine 安裝 + FAQ 26 題 + 課前預載 | 安裝 Docker 時 |
| [Docker 操作手冊](Docker_Compose開發操作手冊.md) | Daemon + Nginx 部署 + Port + Restart + Compose | Docker 日常操作 |
| [Docker 實作手冊](Docker實作手冊.md) | Dockerfile → Compose 多服務 → DockerHub → Portainer | Docker 實作課 |
| [Git 協作手冊](Git_GitHub開發協作手冊.md) | Git 基礎 + VS Code GUI + Branch + PR + 團隊協作 | Git 協作流程 |

## 快速開始

### 1. 環境準備（EP01）

WSL → VS Code → Git : [操作手冊](操作手冊_環境建置.md) 
Git 基礎 + VS Code GUI + Branch + PR + 團隊協作 & Git 協作流程 : [Git 協作手冊](Git_GitHub開發協作手冊.md) 


### 2. Clone 本 repo

```bash
cd ~
mkdir de-project && cd de-project
git clone https://github.com/lu791019/de-course.git
cd de-course
```

### 3. Python 環境（EP02）

 uv → Module/Package : [操作手冊](操作手冊_環境建置.md) 
 
```bash
# 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 跑爬蟲測試
cd ep02
uv sync
uv run python ptt_crawler.py
```

### 4. Docker（EP03-04）

```bash
# 安裝 Docker Engine（完整步驟見 Docker安裝教學手冊.md）
# 安裝完成後：
cd ~/de-01-projects/de-course/ep03-04
docker compose up -d        # 起 4 個 infra 服務
docker compose ps           # 確認全部 running
docker compose down         # 停止
```
1. 安裝 Docker - Docker Engine 安裝 + FAQ 26 題 + 課前預載： [Docker 安裝手冊](Docker安裝教學手冊.md) 
2. Docker 日常操作 - Docker Daemon + Nginx 部署 + Port 說明 + Docker Compose ：  [Docker 操作手冊](Docker_Compose開發操作手冊.md)
3. Docker 實作練習 - Dockerfile → Compose 多服務 → DockerHub → Portainer：[Docker 實作手冊](Docker實作手冊.md) 


## 專案結構

```
de-course/
├── README.md                          ← 你在這裡
├── 操作手冊_環境建置.md
├── Docker安裝教學手冊.md
├── Docker實作操作手冊.md
├── Docker_Compose開發操作手冊.md
├── Git_GitHub開發協作手冊.md
├── ep01/                              ← EP01：環境建置
├── ep02/                              ← EP02：uv + Module/Package
│   ├── crawlers/                      ← Python Package
│   ├── pyproject.toml
│   └── uv.lock
└── ep03-04/                           ← EP03-04：Docker
    ├── Dockerfile
    ├── docker-compose.yml             
    ├── crawlers/
    ├── pyproject.toml
    └── uv.lock
```
