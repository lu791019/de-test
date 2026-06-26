# Docker 安裝教學手冊（WSL + Mac）

> 適用對象：已安裝 WSL Ubuntu 或使用 macOS 的學員
> 安裝方式：Docker Engine（不需要 Docker Desktop）
> 最後更新：2026-06-26

---

## 目錄

- [什麼是 Docker？什麼是 Docker Engine？](#什麼是-docker什麼是-docker-engine)
- [Docker Engine vs Docker Desktop](#docker-engine-vs-docker-desktop)
- [WSL Ubuntu 安裝 Docker Engine](#wsl-ubuntu-安裝-docker-engine)
- [啟用 systemd（WSL 自動啟動 Docker）](#啟用-systemdwsl-自動啟動-docker)
- [macOS 安裝 Docker（Colima）](#macos-安裝-dockercolima)
- [安裝後驗證清單](#安裝後驗證清單)
- [FAQ：安裝問題](#faq安裝問題)
- [FAQ：啟動與權限問題](#faq啟動與權限問題)
- [FAQ：網路與 Port 問題](#faq網路與-port-問題)
- [FAQ：效能與檔案問題](#faq效能與檔案問題)
- [FAQ：Docker Desktop 相關](#faq-docker-desktop-相關)
- [FAQ：Mac / Colima 問題](#faqmac--colima-問題)
- [指令速查表](#指令速查表)

---

## 什麼是 Docker？什麼是 Docker Engine？

### Docker
Docker 是一個**容器化平台**，讓你把程式碼 + 環境 + 依賴全部打包成一個「容器」，在任何電腦上都能跑出一模一樣的結果。

### Docker Engine
Docker Engine 是 Docker 的核心引擎，由三個元件組成：

```
┌─────────────────────────────────────────┐
│  你打的指令                               │
│  $ docker run hello-world               │
│         ↓                               │
│  docker CLI（命令列工具）                  │
│         ↓                               │
│  REST API（溝通介面）                     │
│         ↓                               │
│  dockerd（daemon，背景常駐程式）           │
│  → 管理 image、container、network、volume │
└─────────────────────────────────────────┘
```

- **開源**（Apache 2.0 授權），完全免費
- 直接裝在 Linux / WSL 上
- 純 CLI，沒有圖形介面
- 業界伺服器上跑的就是 Docker Engine

---

## Docker Engine vs Docker Desktop

### 為什麼我們用 Engine 不用 Desktop？

| | Docker Engine | Docker Desktop |
|---|---|---|
| 安裝方式 | 在 WSL 裡用指令安裝 | 下載 .exe 安裝 |
| 資源佔用 | 輕量（只有 daemon） | 較重（常駐 GUI + VM 管理層） |
| 費用 | 完全免費 | 個人免費，大企業要付費 |
| 效能 | 較快（直接跑在 WSL） | 略慢（多一層管理） |
| GUI | 沒有 → 用 Portainer 替代 | 有內建 Dashboard |
| 學到的技能 | 和業界部署環境一致 | 只在開發機用 |

### 功能比較（重要：功能上完全一樣）

| 功能 | Desktop | Engine |
|------|---------|--------|
| `docker build` | ✅ | ✅ |
| `docker run` | ✅ | ✅ |
| `docker compose` | ✅ | ✅（plugin 形式）|
| `docker push / pull` | ✅ | ✅ |
| BuildKit / buildx | ✅ | ✅ |
| port mapping（`-p 8000:8000`）| ✅ | ✅ |
| volume mount | ✅ | ✅ |

**結論：你在 terminal 打的所有 docker 指令，兩種安裝方式完全一樣。**

Desktop 多的只是 GUI 和一鍵安裝。但 Desktop 常見的痛點：
- 佔 500MB+ 磁碟 + 常駐吃記憶體
- Starting Engine 卡住不動
- WSL Integration 要手動開
- 有些同學的電腦因為防毒軟體擋住而無法使用

---

## WSL Ubuntu 安裝 Docker Engine

### 前提
- 已安裝 WSL + Ubuntu（EP01 已完成）
- 確認 WSL 版本：在 PowerShell 輸入 `wsl -l -v`，VERSION 要是 **2**

### Step 1：移除舊版（確保乾淨安裝）

如果之前裝過任何 Docker 相關套件，先全部移除：

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 \
           podman-docker containerd runc; do
  sudo apt-get remove -y $pkg 2>/dev/null
done
```

✅ **驗證**：沒有錯誤訊息就 OK（如果顯示 "package not found" 也是正常的）

### Step 2：安裝必要工具

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
```

✅ **驗證**：最後一行顯示 `0 newly installed` 或安裝成功

### Step 3：加入 Docker 官方 GPG key

```bash
sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc

sudo chmod a+r /etc/apt/keyrings/docker.asc
```

✅ **驗證**：

```bash
ls -la /etc/apt/keyrings/docker.asc
# 看到檔案存在，大小約 2-3KB
```

### Step 4：加入 Docker 官方 apt repository

```bash
echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

✅ **驗證**：

```bash
cat /etc/apt/sources.list.d/docker.list
# 應該看到一行 deb [arch=amd64 signed-by=...] https://download.docker.com/linux/ubuntu jammy stable
# （jammy = Ubuntu 22.04，noble = Ubuntu 24.04）
```

### Step 5：安裝 Docker Engine + Compose + BuildKit

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

⚠️ **五個套件都要列出！** `docker-compose-plugin` 不是 `docker-ce` 的自動相依，漏掉的話 `docker compose` 指令會找不到。

✅ **驗證**：

```bash
docker --version
# Docker version 27.x.x, build xxxxxxx

docker compose version
# Docker Compose version v2.x.x
```

### Step 6：iptables —— 預設不用碰（重要觀念）

> **過去很多教學叫你一律把 iptables 切成 legacy。實測後確認：新版 Docker（28/29+）+ 新 kernel 用 Ubuntu 預設的 nftables 就能正常跑，不需要切。** iptables-legacy 已從「必做步驟」降級為「遇到網路錯誤時的排錯手段」。

iptables 是 Docker 拿來做容器網路的工具（port 映射、bridge、`docker compose` 服務互連）。Ubuntu 22.04+ 預設用 nftables 後端。

**這一步什麼都不用做** —— 直接進 Step 7。只有在後面 `docker compose up` 報網路錯誤時，才回來看 [FAQ Q10 / Q14.5](#q10iptables-報-rule_append-failed) 的 legacy 排錯。

✅ 實測（Docker 29 / Ubuntu 22.04）：純 nftables 下 `docker run`、`docker build`、`docker network create`、`docker compose up`、`-p` port 映射全部正常。

### Step 7：把用戶加入 docker 群組

不加這步的話，每次都要用 `sudo docker ...`。

```bash
sudo usermod -aG docker $USER
```

⚠️ **加完不會立即生效！** 需要重新登入。最可靠的方式：

```
1. 關閉所有 WSL 視窗
2. 開啟 Windows PowerShell
3. 輸入：wsl --shutdown
4. 等 5 秒
5. 重新打開 Ubuntu terminal
```

✅ **驗證**（重開 WSL 後）：

```bash
groups
# 列出的群組中應該包含 docker

docker ps
# 不加 sudo 也能執行 = 成功
# 如果報 permission denied = 沒有重新登入，再做一次 wsl --shutdown
```

### Step 8：啟動 Docker

```bash
# 全新 WSL 預設用這個（沒有 systemd）
sudo service docker start
```

💡 註：
- 你在 Step 6 已經 `service docker restart` 過了，daemon 通常已經在跑，這步只是確保它啟動。
- 如果之後照「啟用 systemd」那節開了 systemd，改用 `sudo systemctl start docker`。

✅ **驗證**：

```bash
docker run hello-world
```

看到以下訊息 = 安裝完成！

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

---

## 啟用 systemd（WSL 自動啟動 Docker）

### 為什麼要啟用？

沒啟用 systemd 的話，**每次打開 WSL 都要手動打 `sudo service docker start`**。
啟用 systemd 後，Docker 會隨 WSL 開啟自動啟動，就像一般的 Linux 伺服器。

### 前提

- WSL 版本需要 0.67.6 以上（2022 年 9 月後的版本都支援）
- 確認方式：在 PowerShell 輸入 `wsl --version`

### Step 1：編輯 /etc/wsl.conf

```bash
sudo tee /etc/wsl.conf << 'EOF'
[boot]
systemd=true
EOF
```

✅ **驗證**：

```bash
cat /etc/wsl.conf
# 看到：
# [boot]
# systemd=true
```

### Step 2：重啟 WSL

**在 Windows PowerShell 執行**（不是在 Ubuntu 裡）：

```powershell
wsl --shutdown
```

等 5 秒，然後**重新打開 Ubuntu terminal**。

### Step 3：驗證 systemd 已啟用

```bash
systemctl list-unit-files --type=service | head -10
```

✅ 看到服務列表 = systemd 已啟用
❌ 如果報錯 `System has not been booted with systemd as init system` = 沒成功

沒成功的話檢查：
1. `/etc/wsl.conf` 裡面有沒有 `[boot]` 和 `systemd=true`
2. 有沒有在 PowerShell 執行 `wsl --shutdown`（不是在 Ubuntu 裡執行）
3. WSL 版本是否夠新：PowerShell 輸入 `wsl --version`

### Step 4：設定 Docker 開機自動啟動

```bash
sudo systemctl enable docker
sudo systemctl enable containerd
```

✅ **驗證**：

```bash
sudo systemctl status docker
# 看到 Active: active (running) = Docker 正在跑
# 看到 enabled = 下次開 WSL 會自動啟動
```

### Step 5：測試自動啟動

1. 關閉所有 WSL 視窗
2. PowerShell 執行 `wsl --shutdown`
3. 重新打開 Ubuntu terminal
4. 直接輸入 `docker ps`（不需要先 `sudo service docker start`）

✅ 如果直接能用 = 自動啟動設定成功！

---

### Windows 10 的替代方案

⚠️ 如果你的電腦是 **Windows 10**，systemd 可能不穩定。替代方式：

#### 方案 A：wsl.conf boot command（僅 Windows 11）

```bash
sudo tee /etc/wsl.conf << 'EOF'
[boot]
command=service docker start
EOF
```

然後 PowerShell 執行 `wsl --shutdown`，重開 WSL。

⚠️ `[boot] command` **只支援 Windows 11 / Server 2022**，Windows 10 不支援。

#### 方案 B：每次手動啟動

```bash
sudo service docker start
```

每次打開 WSL 執行一次就好，Docker 就會一直跑到你關閉 WSL。

---

## macOS 安裝 Docker（Colima）

### 為什麼 Mac 不能直接裝 Docker Engine？

Docker Engine 需要 Linux kernel 才能跑。macOS 不是 Linux，所以需要一個輕量 VM 來跑 Linux，Docker 就跑在那個 VM 裡面。

- **Docker Desktop** = 用自己的 VM 層（較重）
- **Colima** = 用 Lima VM（較輕）

### Step 1：安裝 Homebrew（如果還沒裝）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2：安裝 Colima + Docker CLI + Compose

```bash
brew install colima docker docker-compose
```

⚠️ 三個都要裝：
- `colima` = VM 管理（提供 Docker daemon）
- `docker` = Docker CLI（打指令用）
- `docker-compose` = Docker Compose v2（plugin 形式）

### Step 3：啟動 Colima

```bash
# Intel Mac
colima start

# Apple Silicon (M1/M2/M3/M4) — 推薦用 virtiofs 提升效能
colima start --vm-type vz --mount-type virtiofs
```

第一次啟動要等 1-2 分鐘（下載 VM image）。

✅ **驗證**：

```bash
colima status
# 看到 colima is running
```

### Step 4：驗證 Docker

```bash
docker --version
docker compose version
docker run hello-world
```

看到 `Hello from Docker!` = 安裝完成！

### Step 5：設定自動啟動（可選）

```bash
brew services start colima
```

⚠️ 如果不設定自動啟動，**每次重開機後都要手動 `colima start`**。

### Step 6：docker compose plugin 設定

如果 `docker compose` 報 `not a docker command`，需要設定 plugin 路徑：

```bash
mkdir -p ~/.docker
echo '{"cliPluginsExtraDirs": ["/opt/homebrew/lib/docker/cli-plugins"]}' > ~/.docker/config.json
```

✅ **驗證**：

```bash
docker compose version
# Docker Compose version v2.x.x
```

---

## 安裝後驗證清單

安裝完成後，逐一執行以下指令，全部通過才算成功：

```bash
# 1. Docker 版本
docker --version
# 預期：Docker version 27.x.x

# 2. Docker Compose 版本
docker compose version
# 預期：Docker Compose version v2.x.x

# 3. 不用 sudo 就能執行
docker ps
# 預期：CONTAINER ID   IMAGE   COMMAND   ...（空的列表）
# 如果報 permission denied → 見 FAQ Q4

# 4. 跑 hello-world
docker run hello-world
# 預期：Hello from Docker!

# 5. 看 image
docker images
# 預期：看到 hello-world 這個 image

# 6. 看 container
docker ps -a
# 預期：看到剛才跑完的 hello-world container（Exited 狀態）

# 7. 清理測試用的 container 和 image
docker rm $(docker ps -aq)
docker rmi hello-world
```

全部通過 → 可以開始上課了！

---

## 課前準備：下載清單與預載（老師必看）

課程過程中會下載不少東西，教室網路若不穩容易卡住。以下整理所有下載項目與課前預載建議。

### 一、會下載的 Docker images

| Image | 用在 | 磁碟佔用 | 下載量（壓縮約略）|
|-------|------|---------|------------------|
| `mysql:8.0` | EP04 | 1.09GB | ~500MB 🔴 最大 |
| `phpmyadmin/phpmyadmin:5.2` | EP04 | 1.09GB | ~250MB |
| `rabbitmq:3-management` | EP04 | 408MB | ~130MB |
| `mher/flower:latest` | EP04 | 141MB | ~50MB |
| `python:3.13-slim` | EP03（Dockerfile 基底）| ~150MB | ~45MB |
| `hello-world` | EP03 | 22KB | 極小 |
| `enzochang/data_ingestion:latest` | EP04 分開版 worker/producer | 依 push 版本 | 視大小 |

> EP03 下載量小（hello-world + python:3.13-slim）。**EP04 才是下載爆發點**（4 個服務約 1.5-2GB），尤其 `mysql:8.0` 最大。

### 二、其他會下載的大檔案

| 操作 | 集數 | 下載量 |
|------|------|--------|
| Docker Engine apt 安裝（docker-ce + containerd）| EP03 | ~400-500MB .deb |
| `uv sync`（pandas / numpy / requests…）| EP02 | ~80-100MB |
| `docker build` 時容器內再跑一次 `uv sync` | EP03 | ~80-100MB（容器內重下）|

### 三、課前預載指令（避免現場網路塞車）

教室網路不穩的話，**課前在 VM 裡先 pull 好**，上課就有快取秒開：

```bash
docker pull mysql:8.0
docker pull phpmyadmin/phpmyadmin:5.2    # 老師 Apple Silicon Mac 改 phpmyadmin:latest（見 Q25）
docker pull rabbitmq:3-management
docker pull mher/flower:latest
docker pull python:3.13-slim
docker pull hello-world
```

### 四、教學節奏建議（demo 完整性 vs 下載時間的折衷）

| 段落 | 建議 |
|------|------|
| EP03 裝 Docker + hello-world + python:3.13-slim | **現場 demo**（小檔，體現完整安裝流程）|
| EP04 的大 image（mysql 等）| **課前預載**（避免下午卡在下載）|

> 折衷原則：上午 EP03 現場示範「從零裝 Docker」展現完整流程；下午 EP04 的大 image 課前先 pull 好，把時間花在講解 compose 而非等下載。

---

## FAQ：安裝問題

### Q1：`sudo apt-get update` 報 GPG error 或 NO_PUBKEY

**原因**：GPG key 沒加成功，或過期了。

**解法**：重做 Step 3：

```bash
sudo rm -f /etc/apt/keyrings/docker.asc
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo apt-get update
```

### Q2：`apt-get install docker-ce` 找不到套件

**原因**：Step 4 的 apt repository 沒加成功。

**檢查**：

```bash
cat /etc/apt/sources.list.d/docker.list
```

應該看到一行包含 `https://download.docker.com/linux/ubuntu`。

如果是空的或不存在 → 重做 Step 4。

如果 `VERSION_CODENAME` 不對（例如顯示空白）→ 手動指定：

```bash
# Ubuntu 22.04
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu jammy stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Ubuntu 24.04
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu noble stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
```

### Q3：安裝卡在 `Setting up docker-ce` 很久

**原因**：Docker daemon 嘗試啟動但因 iptables 問題卡住。

**解法**：等它跑完（可能 1-2 分鐘），然後執行 Step 6（切換 iptables-legacy），再重新啟動 Docker。

### Q4：安裝過程中報 `dpkg was interrupted`

**解法**：

```bash
sudo dpkg --configure -a
sudo apt-get install -f
# 然後重新執行安裝指令
```

### Q5：WSL 版本怎麼確認？

在 **Windows PowerShell** 輸入：

```powershell
wsl --version
```

如果這個指令報錯 → WSL 版本太舊，需要更新：

```powershell
wsl --update
```

### Q6：Ubuntu 版本怎麼確認？

在 WSL Ubuntu 裡輸入：

```bash
cat /etc/os-release | grep VERSION_ID
# VERSION_ID="22.04" 或 "24.04"

lsb_release -cs
# jammy (22.04) 或 noble (24.04)
```

---

## FAQ：啟動與權限問題

### Q7：`docker ps` 報 `Cannot connect to the Docker daemon`

**原因**：Docker daemon 沒有在跑。

**解法**：

```bash
# 方法 1：手動啟動
sudo service docker start

# 方法 2：如果已啟用 systemd
sudo systemctl start docker
```

⚠️ **不要混用**：有啟用 systemd → 用 `systemctl`；沒啟用 → 用 `service`。

### Q8：`docker ps` 報 `permission denied`

**原因**：你的用戶不在 docker 群組。

**檢查**：

```bash
groups
# 列表裡有沒有 docker？
```

**解法**：

```bash
# 如果沒有 docker 群組 → 加入
sudo usermod -aG docker $USER

# 然後重新登入（最可靠）
# 在 PowerShell 執行：
# wsl --shutdown
# 再重新打開 Ubuntu
```

如果 groups 裡已經有 docker 但還是報錯 → 可能是 `~/.docker` 目錄權限問題：

```bash
sudo chown "$USER":"$USER" /home/"$USER"/.docker -R
sudo chmod g+rwx "$HOME/.docker" -R
```

### Q9：`sudo service docker start` 沒反應或報錯

**檢查 Docker daemon log**：

```bash
sudo dockerd --debug 2>&1 | head -50
```

常見原因：
1. **systemd 已啟用但用了 service** → 改用 `sudo systemctl start docker`
2. **iptables 後端不相容**（舊 kernel）→ 見 Q10
3. **Docker 被另一個 process 鎖住** → `sudo kill $(cat /var/run/docker.pid)` 然後重啟

### Q10：iptables 報 `RULE_APPEND failed`（舊 kernel 才會遇到）

> 多數新環境（Docker 28/29+ + 新 kernel）**不會**遇到這題，nftables 預設就能跑。這題是舊 kernel / 舊 Docker 才需要切 legacy。

**完整錯誤訊息**：

```
iptables v1.8.7 (nf_tables): RULE_APPEND failed (No such file or directory)
```

**原因**：那台機器的 kernel 對 nftables 後端支援不完整，Docker 設不了網路規則。

**解法**：切到 legacy 後端，**切完一定要重啟 daemon**：

```bash
sudo update-alternatives --set iptables /usr/sbin/iptables-legacy
sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy

# ⚠️ 切完一定要 restart（全新 WSL 用 service）
sudo service docker restart
# 已啟用 systemd 才改用 sudo systemctl restart docker
```

⚠️ **重要**：不要「裝完先用 nft 跑一陣子、中途才切 legacy」。daemon 用 nft 建好 chain 後你才切 CLI 成 legacy，兩邊會不一致，反而報 `DOCKER-FORWARD` 錯（見 Q14.5）。要切就在裝好後、還沒大量使用前切，並馬上 restart。

**驗證**：

```bash
iptables --version
# 切換後應該看到 (legacy)
docker network create t && docker network rm t   # 能成功 = OK
```

### Q11：systemd 啟用後 `service docker start` 報錯

**原因**：啟用 systemd 後不能用 `service` 指令，要用 `systemctl`。

**解法**：

```bash
sudo systemctl start docker
```

這是 WSL 的已知問題（microsoft/WSL #12307）。

### Q12：`systemctl` 報 `System has not been booted with systemd`

**原因**：systemd 沒有啟用。

**檢查**：

```bash
cat /etc/wsl.conf
```

確認有：
```
[boot]
systemd=true
```

如果有但還是報錯 → 需要在 **PowerShell** 執行 `wsl --shutdown`，然後重新打開 WSL。

---

## FAQ：網路與 Port 問題

### Q13：`docker run -p 8000:8000` 後，瀏覽器打 localhost:8000 沒反應

**檢查步驟**：

```bash
# 1. 確認 container 有在跑
docker ps
# 看 STATUS 是不是 Up，PORTS 有沒有 0.0.0.0:8000->8000/tcp

# 2. 確認服務有在聽
curl http://localhost:8000
# 如果 curl 有回應但瀏覽器沒有 → 可能是 Windows 防火牆

# 3. 確認 container 內部有啟動
docker logs <container_id>
# 看有沒有錯誤訊息
```

**常見原因**：
- Container 裡面的服務 bind 到 `127.0.0.1` 而不是 `0.0.0.0` → 改成 `0.0.0.0`
- Windows 防火牆擋住 → 暫時關閉防火牆測試
- Port 被別的程式佔用 → `docker ps` 或 `netstat -tlnp` 檢查

### Q14：port already in use

```bash
# 找出誰在用這個 port
sudo lsof -i :8000

# 或用 docker 找
docker ps | grep 8000

# 停掉佔用的 container
docker stop <container_id>
```

### Q14.5：`docker compose up` 建立網路報 `DOCKER-FORWARD` / `No chain/target/match`

**完整錯誤訊息**：

```
Failed to Setup IP tables: Unable to enable ACCEPT OUTGOING rule:
iptables: No chain/target/match by that name. (exit status 1)
failed to create network xxx_default
```

**根本原因（實測確認）**：通常是**「中途切 iptables-legacy 造成的不一致」**。Docker daemon 已經用 nftables 建好 chain，你之後才把 iptables CLI 切成 legacy，兩邊對不上 → daemon 要加 `DOCKER-FORWARD` 規則時找不到 chain。`docker run hello-world`（不建網路）和 `docker build` 不受影響，但 `docker compose up` 要建 bridge 網路就炸。

> 💡 **最好的預防：根本不要切 iptables**（見 Step 6）。新版 Docker 用 nftables 預設就能跑。實測 Docker 29 純 nft 下 compose / port 映射全部正常。

**解法**：重啟 Docker daemon 讓 chain 重新一致：

```bash
# 全新 WSL 預設用這個
sudo service docker restart
# （已啟用 systemd 才改用 sudo systemctl restart docker）

# 重啟後重試
docker compose up -d
```

> 如果你之前手賤切了 legacy 又想切回乾淨的 nft 預設：
> ```bash
> sudo update-alternatives --set iptables /usr/sbin/iptables-nft
> sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-nft
> sudo service docker restart
> ```

**驗證**：

```bash
docker network create test-net && docker network rm test-net
# 能成功建立/刪除 = chain 已正常
```

---

## FAQ：效能與檔案問題

### Q15：Docker build / run 很慢

**常見原因**：
1. **第一次跑** — 要下載 base image（python:3.13-slim ~150MB），之後有快取會快很多
2. **專案放在 /mnt/c/** — 跨檔案系統慢 3-5 倍

**解法**：把專案移到 WSL 原生路徑：

```bash
# 不好（慢）
cd /mnt/c/Users/你的名字/Desktop/project

# 好（快）
cd ~/project
# 或
cd /home/你的ubuntu用戶名/project
```

### Q16：hot-reload 失效（webpack / nodemon / vite 偵測不到檔案變更）

**原因**：專案放在 `/mnt/c/`，Windows 檔案系統的 inotify 事件無法傳遞給 Linux。

**解法**：把專案移到 WSL 原生路徑（`~/project`）。

### Q17：WSL 吃太多記憶體

在 `C:\Users\你的名字\.wslconfig` 建立/編輯這個檔案：

```ini
[wsl2]
memory=4GB
processors=2
swap=2GB

[experimental]
autoMemoryReclaim=gradual
```

然後在 PowerShell 執行 `wsl --shutdown`，重新打開 WSL。

---

## FAQ：Docker Desktop 相關

### Q18：我之前裝了 Docker Desktop，要先移除嗎？

**不一定**。兩種情況：

1. **Desktop 還能用** → 可以不移除，但建議不要同時開 Docker Desktop 和 WSL 裡的 Docker Engine，可能互搶 Docker socket
2. **想完全改用 Engine** → 建議移除 Desktop：
   - Windows：控制台 → 程式與功能 → 解安裝 Docker Desktop
   - 然後在 WSL 裡裝 Docker Engine（本文件步驟）

### Q19：移除 Desktop 後 WSL 裡的 docker 指令消失了

**正常**。Docker Desktop 的 WSL Integration 會把 docker CLI 注入 WSL。移除 Desktop 後注入也沒了。

**解法**：按本文件步驟在 WSL 裡直接裝 Docker Engine，之後不依賴 Desktop。

### Q20：Desktop 和 Engine 可以共存嗎？

技術上可以但不建議。兩者可能互搶 Docker daemon socket，造成指令連到錯的 daemon。

建議擇一使用：
- Desktop 全開 → 在 WSL 裡不另外裝 Engine
- WSL 裡裝 Engine → 不開 Docker Desktop（或移除）

---

## FAQ：Mac / Colima 問題

### Q21：`docker compose` 報 `not a docker command`

**原因**：Docker CLI 找不到 compose plugin。

**解法**：

```bash
mkdir -p ~/.docker
echo '{"cliPluginsExtraDirs": ["/opt/homebrew/lib/docker/cli-plugins"]}' > ~/.docker/config.json

# 驗證
docker compose version
```

### Q22：Colima 啟動後 `docker ps` 報 connection refused

**原因**：Docker socket 路徑不對。

**解法**：

```bash
export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"

# 驗證
docker ps

# 如果 OK，加到 shell profile
echo 'export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"' >> ~/.zshrc
```

### Q23：重開機後 `docker ps` 報錯

**原因**：Colima 不會自動啟動。

**解法**：

```bash
# 手動啟動
colima start

# 或設定自動啟動
brew services start colima
```

### Q24：Colima 和 Docker Desktop 可以共存嗎？

可以。自 Colima v0.3.0 起使用 Docker contexts。切換方式：

```bash
# 看所有 context
docker context ls

# 切到 Colima
docker context use colima

# 切到 Desktop
docker context use desktop-linux
```

---

## FAQ：架構問題（Apple Silicon Mac 老師注意）

> 這一段主要給**用 Apple Silicon Mac（M1/M2/M3/M4）示範的老師**。學生用 Windows WSL（amd64）不會遇到。

### Q25：`docker compose up` 後某個服務一直 Restarting，log 顯示 `exec format error`

**完整錯誤訊息**：

```
exec /docker-entrypoint.sh: exec format error
# 或
apache2: symbol lookup error: ... opcache.so: undefined symbol
```

**原因**：那個 image 只有 **amd64 版本，沒有 arm64 變體**。Apple Silicon Mac 是 arm64，跑不動 amd64 的 binary。

**實測案例**：`phpmyadmin/phpmyadmin:5.2` 是 amd64-only。
- 學生 Windows WSL（amd64）→ 正常 ✅
- 老師 Apple Silicon Mac（arm64）→ exec format error ❌

**怎麼確認 image 有沒有 arm64**：

```bash
docker manifest inspect phpmyadmin/phpmyadmin:5.2 | grep architecture
# 只看到 amd64 = 單一架構，arm64 跑不了
```

**解法（擇一）**：

1. **改用多架構 tag（最簡單，老師 Mac 推薦）**：把 `phpmyadmin:5.2` 改成 `phpmyadmin:latest`（有 arm64 原生）。實測 arm64 上 `phpmyadmin:latest` 正常 HTTP 200。
   ```yaml
   # docker-compose.yml
   phpmyadmin:
     image: phpmyadmin:latest   # 原本是 phpmyadmin/phpmyadmin:5.2
   ```

2. **裝 amd64 模擬層**（保留原版本號，但模擬下部分 image 不穩，phpmyadmin 實測仍會掛）：
   ```bash
   docker run --privileged --rm tonistiigi/binfmt --install amd64
   ```
   ⚠️ 模擬不保證所有 image 都能跑，phpmyadmin:5.2 模擬下仍有 symbol error，建議用解法 1。

3. **老師改用和學生一樣的環境示範**：在 Apple Silicon Mac 上用 Lima 開一顆 Ubuntu VM 教學（見下方），雖然 VM 也是 arm64，phpmyadmin 一樣要用解法 1。

> 教學建議：投影片/repo 的 `docker-compose.yml` 維持 `phpmyadmin:5.2`（學生 amd64 適用）。老師若在 Apple Silicon Mac demo，自己本機把該行改成 `phpmyadmin:latest` 即可，不影響學生。

### Q26：老師想在 Mac 上用「和學生一樣的 apt 安裝流程」示範（不用 Colima）

Colima 會自動裝好 Docker，**沒辦法示範 EP03 的 Docker Engine 安裝步驟**。如果老師想在 Mac 上 demo 和學生 Windows WSL 一模一樣的 apt 安裝流程，用 **Lima 開一顆乾淨 Ubuntu VM**：

```bash
# Lima 是 Colima 的底層，brew 裝 colima 時已附帶
# 開一顆乾淨 Ubuntu 22.04（沒有 Docker，和學生 WSL 一樣）
limactl start --name=tibame-class --vm-type=vz \
  /opt/homebrew/share/lima/templates/ubuntu-22.04.yaml

# 進入 VM
limactl shell tibame-class

# 進去後就是乾淨 Ubuntu，照本文件「WSL Ubuntu 安裝 Docker Engine」步驟 demo
```

⚠️ Lima VM 也是 arm64，phpmyadmin 一樣要套用 Q25 解法 1。
⚠️ Lima VM 預設 disk 配額大（100GiB 稀疏），Mac 磁碟要留足空間。

---

## 指令速查表

### Docker 基本指令

```bash
# Image 操作
docker build -t <name> .                    # Build image
docker images                               # 列出所有 image
docker rmi <name>                           # 刪除 image
docker pull <name>                          # 從 DockerHub 下載 image
docker push <name>                          # 推上 DockerHub

# Container 操作
docker run -it <image>                      # 互動模式跑 container
docker run -d -p 8000:8000 <image>          # 背景模式 + port mapping
docker ps                                   # 看正在跑的 container
docker ps -a                                # 看所有 container（含已停止）
docker stop <id>                            # 停止 container
docker rm <id>                              # 刪除 container
docker logs <id>                            # 看 container log
docker exec -it <id> bash                   # 進入正在跑的 container

# Docker Compose
docker compose up -d                        # 背景啟動所有服務
docker compose down                         # 停止並移除所有服務
docker compose ps                           # 查看服務狀態
docker compose logs -f <service>            # 看即時 log
docker compose restart <service>            # 重啟特定服務

# 清理
docker system prune                         # 清理所有未使用的資源
docker system prune -a                      # 清理所有（含未使用的 image）
```

### Docker daemon 管理（WSL）

```bash
# 有 systemd
sudo systemctl start docker                # 啟動
sudo systemctl stop docker                 # 停止
sudo systemctl restart docker              # 重啟
sudo systemctl status docker               # 看狀態
sudo systemctl enable docker               # 開機自動啟動

# 沒有 systemd
sudo service docker start                  # 啟動
sudo service docker stop                   # 停止
sudo service docker restart                # 重啟
sudo service docker status                 # 看狀態
```

### Colima 管理（Mac）

```bash
colima start                               # 啟動
colima stop                                # 停止
colima status                              # 看狀態
colima delete                              # 刪除 VM（重新建立用）
brew services start colima                  # 設定自動啟動
brew services stop colima                   # 取消自動啟動
```
