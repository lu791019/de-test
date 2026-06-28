# TibaMe 雲端資料工程師 — 課程教材

> EP01-04 教學用 repo（Season 0）

## 課程文件

| 文件 | 內容 | 適用 |
|------|------|------|
| [操作手冊](操作手冊_EP01-04_完整路線.md) | EP01-04 從零到 Docker 完整路線（WSL → VS Code → Git → Python → uv → Docker → Compose）| 學生跟著做 |
| [Docker 安裝教學手冊](Docker安裝教學手冊.md) | Docker Engine 安裝（WSL + Mac）、systemd、FAQ 26 題、課前預載清單 | 安裝 Docker 時看 |
| [Docker 實作操作手冊](Docker實作操作手冊.md) | Docker 基本操作 → Dockerfile → Compose（ep03-04 + de-project-course）→ DockerHub → Portainer | Docker 實作時看 |

## 課程進度對應

| EP | 主題 | 用到的資料夾 |
|----|------|-------------|
| EP01 | WSL + VS Code + Git | 根目錄 |
| EP02 | Python 環境（uv）+ Module/Package | `ep02/` |
| EP03 | Docker 安裝 + Dockerfile | `ep03-04/` |
| EP04 | Docker Compose | `ep03-04/` + [de-project-course](https://github.com/lu791019/de-project-course) |

## 快速開始

### 1. 環境準備（EP01）

```bash
# WSL Ubuntu Terminal
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y
```

### 2. Clone 本 repo

```bash
cd ~
mkdir de-01-projects && cd de-01-projects
git clone https://github.com/lu791019/de-test.git
cd de-test
```

### 3. 測試 Python 環境

```bash
# 方法一：venv + pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 test.py
deactivate

# 方法二：uv（課程推薦）
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env
cd ep02
uv sync
uv run python test.py
```

### 4. 安裝 Docker（EP03）

```bash
# Docker Engine（不用 Docker Desktop）
# 完整步驟見 Docker安裝教學手冊.md，以下是精簡版：

sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo service docker start
sudo usermod -aG docker $USER
# PowerShell: wsl --shutdown → 重開 Ubuntu

docker run hello-world    # 看到 Hello from Docker! = 成功
```

### 5. Docker Compose（EP04）

```bash
cd ~/de-01-projects/de-test/ep03-04
docker compose up -d        # 起 4 個 infra 服務
docker compose ps           # 確認全部 Up
docker compose down -v      # 停止 + 清資料
```

## 專案結構

```
de-test/
├── README.md                          ← 你在這裡
├── 操作手冊_EP01-04_完整路線.md
├── Docker安裝教學手冊.md
├── Docker實作操作手冊.md
├── ep01/                              ← EP01 原始檔案
├── ep02/                              ← EP02 + crawlers package + uv
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── ptt_crawler.py
│   │   ├── finmind.py
│   │   └── hahow_crawler.py
│   ├── pyproject.toml
│   └── uv.lock
├── ep03-04/                           ← EP03-04 + Dockerfile + Compose
│   ├── Dockerfile
│   ├── docker-compose.yml             ← 4 服務 infra
│   ├── crawlers/
│   ├── pyproject.toml
│   └── uv.lock
├── ptt_crawler.py                     ← 根目錄爬蟲（EP01 用）
├── hahow_crawler.py
├── finmind.py
├── test.py
└── requirements.txt
```

## 相關 Repo

| Repo | 用途 |
|------|------|
| [de-test](https://github.com/lu791019/de-test)（本 repo）| EP01-04 教學 |
| [de-project-course](https://github.com/lu791019/de-project-course) | EP04+ 完整爬蟲系統（6 服務 + worker/producer）|
| [de-project](https://github.com/DataEngCamp/de-project) | 原版真實專案 |
