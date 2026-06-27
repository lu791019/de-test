# Docker 實作操作手冊（EP03–04）

> 對象：已照《Docker 安裝教學手冊》裝好 Docker 的學員
> 涵蓋：Docker 基本操作 → Dockerfile 實作 → 真實專案 → Docker Compose（整合版 + 分開版）→ DockerHub → Portainer
> 所有指令都在 Docker 29.6.1 / Compose v5.2.0 / Ubuntu 22.04 實測通過
> 最後更新：2026-06-27

---

## 使用前提

```bash
# 確認 Docker 可用（不用 sudo）
docker --version          # Docker version 29.x.x
docker compose version    # Docker Compose version v2+（v5.2.0）
docker run hello-world    # 看到 Hello from Docker!
```

如果 `docker ps` 要加 `sudo` 才能跑 → 你還沒設好 docker 群組，回去看《Docker 安裝教學手冊》Step 7。

> 📁 **重要**：所有實作都在 WSL 原生路徑（`~/`）下做，**不要在 `/mnt/c/`**（會慢 3-5 倍且檔案監聽失效）。

---

## 目錄

- [第一部分：Docker 基本操作](#第一部分docker-基本操作)
- [第二部分：Dockerfile 實作（FastAPI 範例）](#第二部分dockerfile-實作fastapi-範例)
- [第三部分：de-test 真實專案 Dockerfile](#第三部分de-test-真實專案-dockerfile)
- [第四部分：Docker Compose 整合版](#第四部分docker-compose-整合版)
- [第五部分：Docker Compose 分開版（de-project）](#第五部分docker-compose-分開版de-project)
- [第六部分：DockerHub 分享 image](#第六部分dockerhub-分享-image)
- [第七部分：Portainer 圖形化管理](#第七部分portainer-圖形化管理)
- [附錄：清理與還原](#附錄清理與還原)

---

## 第一部分：Docker 基本操作

先用官方 `hello-world` 熟悉 image / container 的關係。

### Step 1：跑第一個 container

```bash
docker run hello-world
```

✅ **預期**：

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

這行指令背後做了 4 件事：
1. 本機沒有 `hello-world` image → 自動從 DockerHub 下載
2. 用這個 image 建立一個 container
3. container 執行印出訊息
4. 執行完畢，container 停止

### Step 2：看 image 和 container

```bash
# 看本機所有 image
docker images
# 預期：看到 hello-world

# 看「正在執行」的 container
docker ps
# 預期：空的（hello-world 跑完就停了）

# 看「所有」container（含已停止）
docker ps -a
# 預期：看到 hello-world，STATUS 是 Exited
```

💡 **重點觀念**：
- `docker ps` 只顯示執行中的 → hello-world 看不到
- `docker ps -a` 加 `-a`（all）才看得到停止的

### Step 3：管理 container 生命週期

```bash
# 跑一個會持續執行的 container（Ubuntu 互動 shell）
docker run -it ubuntu bash
# 進到 container 裡，提示符變成 root@xxxx:/#
# 試試：
ls /
cat /etc/os-release
exit                     # 離開，container 停止

# 看剛才的 container
docker ps -a

# 刪除停止的 container
docker rm <container_id 或 name>

# 刪除 image
docker rmi hello-world
```

### Step 4：常用指令速查

```bash
docker run -d <image>           # 背景執行（detached）
docker run -p 8080:80 <image>   # port 映射（主機 8080 → 容器 80）
docker run --name myapp <image> # 命名 container
docker logs <id>                # 看 container log
docker exec -it <id> bash       # 進入正在跑的 container
docker stop <id>                # 停止
docker start <id>               # 重新啟動
docker rm <id>                  # 刪除 container
docker rmi <image>              # 刪除 image
docker system prune             # 清理未使用資源
```

---

## 第二部分：Dockerfile 實作（FastAPI 範例）

從零寫一個 Dockerfile，把一個 FastAPI 小程式打包成 image。

### 情境

你寫好一個 API，想讓別人「不用裝任何東西、一行指令就能跑」。

### Step 1：建立專案資料夾

```bash
cd ~
mkdir fastapi-demo && cd fastapi-demo
```

### Step 2：寫 main.py

```bash
cat > main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello Docker + FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
EOF
```

> 用 VS Code 的話直接新建 `main.py` 貼上即可。

### Step 3：寫 requirements.txt

```bash
cat > requirements.txt << 'EOF'
fastapi
uvicorn[standard]
EOF
```

### Step 4：寫 Dockerfile

```bash
cat > Dockerfile << 'EOF'
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

**逐行解讀**：

| 指令 | 作用 |
|------|------|
| `FROM python:3.13-slim` | 基底 image（精簡版 Python）|
| `WORKDIR /app` | 設定容器內工作目錄 |
| `COPY requirements.txt .` | 先複製依賴清單（為了快取）|
| `RUN pip install ...` | 安裝套件 |
| `COPY . .` | 複製程式碼進去 |
| `EXPOSE 8000` | 宣告容器用 8000 port |
| `CMD [...]` | 容器啟動時執行的指令 |

💡 **為什麼先 COPY requirements 再 COPY 程式碼？**
Docker 有層快取。只要 `requirements.txt` 沒變，`pip install` 那層就不用重跑。只改程式碼的話 rebuild 會非常快。

### Step 5：Build image

```bash
docker build -t fastapi-demo .
```

✅ **預期**：最後看到

```
naming to docker.io/library/fastapi-demo:latest done
```

```bash
# 確認 image 建好
docker images | grep fastapi-demo
```

### Step 6：Run container

```bash
docker run -d --name fastapi-demo -p 8000:8000 fastapi-demo
```

- `-d`：背景執行
- `--name`：命名
- `-p 8000:8000`：主機 8000 → 容器 8000

✅ **驗證**（實測通過）：

```bash
curl http://localhost:8000/
# {"message":"Hello Docker + FastAPI!"}

curl http://localhost:8000/items/42
# {"item_id":42}
```

### Step 7：看 Swagger UI

開瀏覽器 → `http://localhost:8000/docs`
✅ 會看到 FastAPI 自動產生的互動式 API 文件（HTTP 200）。

### Step 8：停止與清理

```bash
docker stop fastapi-demo
docker rm fastapi-demo
```

---

## 第三部分：de-test 真實專案 Dockerfile

用課程的 de-test repo（ep03-04）打包真實的爬蟲專案。這個 Dockerfile 用 **uv** 管理環境。

### Step 1：進入專案

```bash
cd ~/de-01-projects/de-test/ep03-04
ls
# 看到 Dockerfile、docker-compose.yml、crawlers/、pyproject.toml、uv.lock...
```

### Step 2：看 Dockerfile

```bash
cat Dockerfile
```

```dockerfile
FROM python:3.13-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
# 安裝 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh
WORKDIR /app
# 先複製依賴檔（快取）
COPY pyproject.toml uv.lock ./
RUN uv sync
# 複製程式碼
COPY crawlers/ ./crawlers/
COPY *.py ./
ENV TZ=Asia/Taipei
CMD ["/bin/bash"]
```

**和 FastAPI 版的差異**：

| | fastapi-demo | de-test |
|---|---|---|
| 套件管理 | pip + requirements.txt | uv + pyproject.toml/uv.lock |
| 基底 | python:3.13-slim | python:3.13-slim |
| 啟動 | 跑 uvicorn server | 開 bash（互動用）|

### Step 3：Build

```bash
docker build -t test-app .
```

✅ **預期**：image 約 438MB（實測），最後 `naming to ... test-app:latest done`

```bash
docker images | grep test-app
```

### Step 4：Run + 進入容器

```bash
docker run -it test-app
# 進到容器的 bash，提示符變 root@xxxx:/app#
```

### Step 5：在容器裡跑爬蟲

```bash
# （在容器內）
uv run python crawlers/ptt_crawler.py
# 會實際去爬 PTT，印出文章資料
```

✅ 看到爬蟲輸出 = 整個環境（Python + uv + 套件 + 程式碼）都被正確打包進 image 了。

### Step 6：離開容器

```bash
exit
# 容器停止，但 image 還在
docker ps -a    # 看到剛才的 test-app container（Exited）
```

---

## 第四部分：Docker Compose 整合版

一個 `docker-compose.yml` 一次啟動多個服務。de-test 的 ep03-04 用**整合版**（所有服務寫在同一個檔案）。

### 情境

你的資料工程系統需要 4 個服務同時跑：訊息佇列、監控、資料庫、資料庫管理介面。手動 `docker run` 4 次太麻煩 → 用 Compose 一行搞定。

### Step 1：看 docker-compose.yml

```bash
cd ~/de-01-projects/de-test/ep03-04
cat docker-compose.yml
```

四個服務：

| 服務 | Image | Port | 用途 |
|------|-------|------|------|
| rabbitmq | rabbitmq:3-management | 5672 / 15672 | 訊息佇列（管理介面 15672）|
| flower | mher/flower | 5555 | Celery 任務監控 |
| mysql | mysql:8.0 | 3306 | 資料庫 |
| phpmyadmin | phpmyadmin:5.2 | 8000 | 資料庫管理介面 |

> ⚠️ **Apple Silicon Mac 老師**：`phpmyadmin:5.2` 只有 amd64，arm64 會 `exec format error`。本機把該行改成 `phpmyadmin:latest`。學生 Windows WSL 不受影響。

### Step 2：一行啟動所有服務

```bash
docker compose up -d
```

- `up`：啟動
- `-d`：背景執行

✅ **預期**（實測）：

```
Container rabbitmq   Started
Container mysql      Started
Container flower     Started
Container phpmyadmin Started
```

> 第一次會 pull mysql:8.0 等 image（約 1.5-2GB），需要時間。建議課前先 `docker compose pull`。

### Step 3：查看服務狀態

```bash
docker compose ps
```

✅ 四個服務 STATUS 都是 `Up`。

### Step 4：打開各服務的 web 介面（實測都 HTTP 200）

| 服務 | 網址 | 帳密 |
|------|------|------|
| RabbitMQ 管理 | http://localhost:15672 | worker / worker |
| Flower 監控 | http://localhost:5555 | （無）|
| phpMyAdmin | http://localhost:8000 | root / 1234 |

### Step 5：看 log

```bash
docker compose logs -f rabbitmq   # 看單一服務
docker compose logs -f            # 看全部
# Ctrl+C 離開（不會停止服務）
```

### Step 6：停止所有服務

```bash
docker compose down
# 停止並移除所有 container + network

docker compose down -v
# 連 volume（資料庫資料）也一起刪
```

---

## 第五部分：Docker Compose 分開版（de-project）

de-project 用**分開版** —— 每個服務一個 compose file，一次加一個。適合逐步除錯、彈性組合。

### Step 1：取得 de-project

```bash
cd ~/de-01-projects
git clone https://github.com/DataEngCamp/de-project.git
cd de-project
ls docker-compose-*.yml
# docker-compose-broker.yml  -mysql.yml  -worker.yml  -producer.yml
```

### Step 2：建立共用 network（關鍵！）

分開版的服務分散在不同 compose file，要靠一個**共用網路**互通。所有 compose file 都設了 `my_network: external: true`，所以要先手動建：

```bash
docker network create my_network
```

✅ **驗證**：

```bash
docker network ls | grep my_network
```

> ⚠️ 不先建這個網路，`docker compose -f ... up` 會報 `network my_network declared as external, but could not be found`。

### Step 3：第一個服務 — RabbitMQ + Flower（broker）

```bash
docker compose -f docker-compose-broker.yml up -d
```

✅ **驗證**（實測 HTTP 200）：
- RabbitMQ 管理：http://localhost:15672 （worker / worker）
- Flower 監控：http://localhost:5555

### Step 4：第二個服務 — MySQL + phpMyAdmin

```bash
docker compose -f docker-compose-mysql.yml up -d
```

✅ **驗證**：
- phpMyAdmin：http://localhost:8000
- 也可從另一容器測 MySQL 連線（實測 `mysqld is alive`）：
  ```bash
  docker run --rm --network my_network mysql:8.0 \
    mysqladmin ping -h mysql -uroot -p1234
  ```

### Step 5：第三個服務 — Worker

```bash
docker compose -f docker-compose-worker.yml up -d
docker compose -f docker-compose-worker.yml logs -f
```

> Worker 用的是 DockerHub 上預先 build 好的 image `enzochang/data_ingestion:latest`，第一次會自動 pull。

### Step 6：發送任務 — Producer

```bash
docker compose -f docker-compose-producer.yml up
# producer 跑完就結束（送出爬蟲任務）
```

### Step 7：在 Flower 看任務執行

回到 http://localhost:5555 → Tasks 頁籤，看 Worker 接到任務並執行。

### Step 8：停止所有服務

```bash
docker compose -f docker-compose-broker.yml -f docker-compose-mysql.yml \
  -f docker-compose-worker.yml down
docker network rm my_network
```

### 整合版 vs 分開版

| | 整合版（ep03-04）| 分開版（de-project）|
|---|---|---|
| 啟動 | `docker compose up` 一行 | 每個服務各一行 |
| network | 自動建 | 手動 `docker network create` |
| 適合 | 一鍵部署、教學 | 逐步除錯、彈性組合 |

---

## 第六部分：DockerHub 分享 image

把你 build 好的 image push 上 DockerHub，別人 pull 就能用。

> DockerHub = 「image 版的 GitHub」。GitHub 管程式碼，DockerHub 管 Docker image。

### Step 1：註冊 + 登入

```bash
# 先到 https://hub.docker.com 註冊帳號（記住 username）
docker login
# 輸入 DockerHub 帳號密碼
```

✅ **預期**：`Login Succeeded`

### Step 2：給 image 加 tag

DockerHub 的 image 命名規則是 `username/image:tag`：

```bash
docker tag test-app <你的username>/test-app:latest
docker images | grep test-app   # 確認多了一個 username/test-app
```

### Step 3：Push 上 DockerHub

```bash
docker push <你的username>/test-app:latest
```

✅ 到 https://hub.docker.com → Repositories，看到 `test-app`。

### Step 4：pull 下來測試（驗證 push 成功）

```bash
# 模擬另一台電腦：先刪本地 image
docker rmi <你的username>/test-app:latest

# 從 DockerHub 拉下來
docker pull <你的username>/test-app:latest

# 跑起來確認
docker run -it <你的username>/test-app:latest
```

✅ 能跑 = push 成功！別人只要 `docker pull` 就能用你的環境，不用自己 build。

---

## 第七部分：Portainer 圖形化管理

Docker 指令太多記不住？Portainer 是 Docker 的網頁圖形管理介面（取代 Docker Desktop 的 GUI）。

### Step 1：安裝 Portainer（一行）

```bash
docker volume create portainer_data

docker run -d -p 9000:9000 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

**參數說明**：
- `-p 9000:9000`：網頁介面 port
- `-v /var/run/docker.sock`：讓 Portainer 能控制 Docker
- `--restart=always`：開機自動啟動

✅ **驗證**（實測）：

```bash
docker ps --filter name=portainer
# STATUS: Up
curl -o /dev/null -w "%{http_code}\n" http://localhost:9000
# 200
```

### Step 2：設定 admin 密碼

開瀏覽器 → http://localhost:9000 → 第一次會要求設定管理員帳密（密碼至少 12 碼）。

### Step 3：用 Portainer 看所有 container

1. 選 `local` 環境
2. 左側選 `Containers`
3. 看到所有 container，可以直接點按鈕 start / stop / logs / console，不用打指令

### Step 4：移除 Portainer（若不需要）

```bash
docker rm -f portainer
docker volume rm portainer_data
```

---

## 附錄：清理與還原

### 清理單一實作

```bash
docker compose down -v          # 停 compose 服務 + 刪 volume
docker rm -f <container>         # 刪 container
docker rmi <image>              # 刪 image
```

### 全部清乾淨（謹慎）

```bash
docker ps -aq | xargs -r docker rm -f     # 刪所有 container
docker system prune -a --volumes          # 刪所有未使用 image/network/volume
```

### 常見實作排錯

| 問題 | 解法 |
|------|------|
| `docker compose up` 報 `DOCKER-FORWARD` / `No chain/target/match` | `sudo service docker restart` 後重試（見《Docker 安裝教學手冊》Q14.5）|
| `network my_network not found` | 分開版要先 `docker network create my_network` |
| `port already in use` | `docker ps` 找佔用的 → `docker stop`，或改 compose 的 port |
| phpMyAdmin 一直 Restarting（Apple Silicon）| `phpmyadmin:5.2` → `phpmyadmin:latest` |
| build 很慢 | 第一次要下載基底 image，之後有快取會快 |
| 容器內檔案改了主機看不到 | 用 volume 掛載：`-v $(pwd):/app` |

---

## 實作檢核表（課堂帶學生跑）

- [ ] `docker run hello-world` 成功
- [ ] 看懂 `docker ps` vs `docker ps -a`
- [ ] FastAPI demo：build → run → 瀏覽器看到 /docs
- [ ] de-test：build test-app → 容器內跑爬蟲
- [ ] Compose 整合版：`docker compose up -d` → 4 服務 web 介面都開得起來
- [ ] Compose 分開版：建 network → broker → mysql → worker → producer
- [ ] DockerHub：login → tag → push → pull 測試
- [ ] Portainer：安裝 → 網頁看 container
