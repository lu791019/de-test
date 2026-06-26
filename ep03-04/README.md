# EP03-04 — Docker 基礎 + Docker Compose 多服務

本資料夾是 EP03-04 教完後的狀態：在 EP02 的基礎上加了 Dockerfile 和 docker-compose.yml。

## 環境需求

### 方法一：Docker Desktop（推薦初學者）

- [下載 Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Windows 用戶：確認 WSL Integration 已開啟

### 方法二：Docker Engine（不用 Desktop）

Docker Engine 可完全取代 Docker Desktop，更輕量。

```bash
# 安裝 Docker Engine（WSL Ubuntu）
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# 修復 iptables（Ubuntu 22.04+ 必要）
sudo update-alternatives --set iptables /usr/sbin/iptables-legacy

# 加入 docker group + 啟動
sudo usermod -aG docker $USER
sudo service docker start

# 驗證
docker --version && docker compose version
```

**自動啟動：** 編輯 `/etc/wsl.conf` 加入 `[boot]\nsystemd=true`，然後 `wsl --shutdown` 重啟，再 `sudo systemctl enable docker`。

**Mac 替代方案：** `brew install colima docker docker-compose && colima start`

## 快速開始

```bash
# 1. Build image
docker build -t test-app .

# 2. 跑 container（互動模式）
docker run -it test-app

# 3. 在 container 裡跑爬蟲
uv run python crawlers/ptt_crawler.py
exit
```

## Dockerfile 解讀

```dockerfile
FROM python:3.13-slim              # 基底 image
RUN apt-get update && ...          # 安裝系統工具
RUN curl ... | sh                  # 安裝 uv
WORKDIR /app                       # 設定工作目錄
COPY pyproject.toml uv.lock ./     # 先複製依賴檔（Docker 快取）
RUN uv sync                        # 安裝套件
COPY crawlers/ ./crawlers/         # 複製 package
COPY *.py ./                       # 複製腳本
CMD ["/bin/bash"]                  # 預設開 bash
```

**為什麼先 COPY 依賴檔再 COPY 程式碼？**

Docker 有快取機制。如果 pyproject.toml 沒變，`RUN uv sync` 那層就不用重跑。只改 code 的話 rebuild 會快很多。

## Docker Compose — 一行啟動所有服務

```bash
# 啟動所有服務（背景）
docker compose up -d

# 查看服務狀態
docker compose ps

# 看特定服務的 log
docker compose logs -f worker

# 只啟動部分服務
docker compose up -d rabbitmq mysql

# 停止所有服務
docker compose down
```

### 服務總覽

| 服務 | Image | Port | 用途 |
|------|-------|------|------|
| RabbitMQ | rabbitmq:3-management | 5672 / 15672 | 訊息佇列（管理介面 localhost:15672） |
| Flower | mher/flower | 5555 | Celery 任務監控（localhost:5555） |
| MySQL | mysql:8.0 | 3306 | 資料庫 |
| phpMyAdmin | phpmyadmin:5.2 | 8000 | 資料庫管理介面（localhost:8000） |

### 預設帳號密碼

| 服務 | 帳號 | 密碼 |
|------|------|------|
| RabbitMQ | worker | worker |
| MySQL | root | 1234 |

## Docker 常用指令

```bash
# Image 操作
docker build -t <name> .          # Build image
docker images                      # 列出所有 image
docker rmi <name>                  # 刪除 image

# Container 操作
docker run -it <name>              # 互動模式跑 container
docker run -p 8000:8000 <name>     # port 映射
docker ps                          # 看正在跑的 container
docker ps -a                       # 看所有 container
docker stop <id>                   # 停止 container
docker rm <id>                     # 刪除 container

# Docker Compose
docker compose up -d               # 背景啟動所有服務
docker compose down                # 停止並移除所有服務
docker compose ps                  # 查看服務狀態
docker compose logs -f <service>   # 看即時 log
docker compose restart <service>   # 重啟特定服務
```

## 常見問題

| 問題 | 解法 |
|------|------|
| `docker: command not found` | 開啟 Docker Desktop，確認 WSL Integration 有開；或用 Docker Engine 直接裝在 WSL（見上方方法二）|
| `Cannot connect to Docker daemon` | Docker Desktop 沒在跑，開啟它等啟動完成；Engine 版用 `sudo service docker start` |
| `port already in use` | `docker ps` 找到佔用的 container → `docker stop` |
| `permission denied` | `sudo usermod -aG docker <username>` → `wsl --shutdown` 重開 |
| build 很慢 | 第一次要下載基底 image，之後有快取會快 |
| `docker compose up` 報 `iptables: No chain/target/match` / `DOCKER-FORWARD` | 多半是中途切過 iptables-legacy 造成不一致。`sudo service docker restart` 即可（新版 Docker 預設別碰 iptables）|
| phpMyAdmin 一直 Restarting，log 顯示 `exec format error` | `phpmyadmin:5.2` 是 amd64-only。**Windows WSL 學生不受影響**；Apple Silicon Mac 把 compose 裡 `phpmyadmin:5.2` 改成 `phpmyadmin:latest`（多架構）|

> 完整 Docker Engine 安裝、systemd、Mac/Colima、架構問題、課前預載清單 → 見課程的 `Docker 安裝教學手冊（Docker_Engine_vs_Desktop.md）`

## 檔案說明

| 檔案 | EP02 就有 | EP03-04 新增 |
|------|-----------|-------------|
| `crawlers/` | ✅ | |
| `pyproject.toml` | ✅ | |
| `uv.lock` | ✅ | |
| `Dockerfile` | | ✅ |
| `docker-compose.yml` | | ✅ |
| `.gitignore` | ✅ | 更新（加了 .env, output/） |

## 整合版 vs 拆開版

本資料夾使用**整合版** docker-compose.yml（所有服務寫在同一個檔案）。

[de-project](https://github.com/DataEngCamp/de-project) 使用**拆開版**（每個服務一個 compose file）。兩種做法的差別：

| | 整合版（本資料夾） | 拆開版（de-project） |
|---|---|---|
| 啟動 | `docker compose up` 一行 | 每個各一行 |
| network | 自動建 | 手動 `docker network create` |
| 適合 | 一鍵部署、教學 | 開發測試、逐步除錯 |
