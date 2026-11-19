# ECS 部署（Ubuntu，云助手/VNC）

仓库为私有仓库，使用 `deploy/ecs-miaoda` 分支。本文命令在 ECS 的 root 云助手中执行。

> 当前阶段先用于部署验证。飞书 OAuth 尚未完成，不要把后端直接开放给 50 名公网用户。测试期间请限制安全组来源 IP，8010 不要对公网开放。

## 1. 安装 Docker

```bash
apt update
apt install -y git ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
docker --version
docker compose version
```

## 2. 为私有仓库配置只读 Deploy Key

在 ECS 生成一把专门用于 GitHub 的密钥：

```bash
ssh-keygen -t ed25519 -f ~/.ssh/eva_github -N ''
cat ~/.ssh/eva_github.pub
```

把输出的 **公钥**添加到 GitHub：

```text
Image-indicator → Settings → Deploy keys → Add deploy key
```

只勾选只读，不给写权限。然后回到 ECS：

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/eva_github
ssh -T git@github.com
```

`ssh -T` 返回成功识别后，克隆：

```bash
git clone -b deploy/ecs-miaoda git@github.com:Flysheep1223/Image-indicator.git /opt/seedream-eva
cd /opt/seedream-eva
```

如果目录已存在：

```bash
cd /opt/seedream-eva
git pull origin deploy/ecs-miaoda
```

## 3. 配置环境变量

```bash
cd /opt/seedream-eva
cp .env.example .env
chmod 600 .env
nano .env
```

至少填写：

- `VLM_MODEL`、`SEEDREAM_MODEL`；
- TOS 的 Bucket、地域和凭证；
- `EVA_DOMAIN`；
- `EVA_CORS_ORIGINS`（等妙搭发布地址确定后再填）。

生成独立 SessionSecret：

```bash
openssl rand -hex 32
```

将结果填到 `EVA_SESSION_SECRET`，不要提交 `.env`。

## 4. 构建并启动

```bash
cd /opt/seedream-eva
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 app
```

容器内健康检查：

```bash
docker compose exec app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8010/health').read().decode())"
```

如果 UFW 已启用：

```bash
ufw allow 80/tcp
ufw allow 443/tcp
```

不要开放 8010。

## 5. HTTPS 和妙搭

把 `EVA_DOMAIN` 的 DNS A 记录指向 ECS 公网 IP。Caddy 会自动申请证书。证书成功后访问：

```text
https://你的API域名/health
```

妙搭前端确定发布域名后，将其 origin 填到：

```text
EVA_CORS_ORIGINS=https://你的妙搭域名
```

然后重启：

```bash
docker compose up -d
```

飞书 OAuth 回调和任务归属控制完成前，仅做受控测试，不进行公网 50 人正式使用。
