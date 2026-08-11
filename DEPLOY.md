# 部署手册：碳中和宣传效果调研问卷（oTree 6 · 免费 · 国内可访问 · 无需国际信用卡）

本目录是一个完整的 oTree 6 项目，已实现：
- 32 题问卷（含 4 组随机阅读材料的 A/B 测试、注意力检测题、行为意愿与人口统计）
- 指南《日常低碳行动极简指南》**仅下载、不预览**（通过 WebSocket 分块下发 + Blob 强制保存，任何浏览器含微信/iOS 均不会内联预览）
- 服务端真实计数：每位参与者的下载次数、总下载次数、总下载人数，以及每次下载的审计明细
- 管理端可导出 4 张表（逐人答案+下载次数 / 各子会话汇总 / 各组下载统计 / 下载明细）

## 架构（全部免费、国内可访问、关机不影响收数据、无需国际信用卡）
GitHub（代码，已推送）→ **Koyeb 免费 Docker Web 服务（Singapore）** → **Supabase 免费 Postgres**（数据持久化）→ **cron-job.org** 保活。

> 为什么不用 Render：Render 免费 Web 服务强制绑定国际信用卡（预授权 1 美元），没有 Visa/Mastercard 无法部署。
> Koyeb 免费层**不强制绑卡**，且支持 Docker + WebSocket，有 Singapore 节点，对国内网络可达，因此作为主方案。

已在本地验证：模型导入正常、`resetdb` 成功、下载字节级还原一致、计数逻辑正确。
GitHub 仓库已就绪：https://github.com/Louis-lab123/carbon-survey

---

## 第 1 步：Supabase 数据库（免费、不过期）— 你已建好，只需拿到 URI
1. 打开 https://supabase.com → 进入你的 Project。
2. 左侧主菜单点 **Database**（不是 Settings）→ 页面顶部找 **Connection string / URI**，形如：
   `postgresql://postgres:密码@db.xxxx.supabase.co:5432/postgres`
   - 若页面只显示密码框、不显示完整串，手动拼：`postgresql://postgres:<你的密码>@db.uyanhgxnsucpkhvrmcfb.supabase.co:5432/postgres`（密码忘了可 Reset password）。
3. **Settings → Database → 打开 "Allow access from anywhere"**（否则 Koyeb 连不上）。
4. 区域选 **Singapore（新加坡）**，离国内近。
5. 把完整 `postgresql://...` 串（含密码）**只填进 Koyeb 的环境变量 `DATABASE_URL`**，不要发到聊天里。

> 不要用 Koyeb 自带的免费 Postgres：它每月仅 5 小时活跃时长，不够长期收数据。Supabase 免费版 500MB、长期有效（约 7 天无活动才暂停，有 cron 保活不会触发）。

## 第 2 步：Koyeb 部署（免费、无需信用卡）
1. 打开 https://koyeb.com 注册（建议用 GitHub 登录，与你的仓库同一账号）。
   - 免费层：1 个 Web 服务（512MB RAM / 0.1 vCPU / 2GB SSD），**永不收费**；多数地区注册不绑卡。
2. 控制台点 **Create App / Service** → 选择 **GitHub** → 授权并选中仓库 `carbon-survey`。
3. 部署方式选 **Docker**（仓库根目录有 `Dockerfile`，会自动识别）；分支 `main`。
4. 区域选 **Singapore**（ap-southeast）。
5. 设置端口为 **8000**（应用 `start.sh` 会监听 `$PORT`，默认 8000）。
   - Health check 路径可填 `/`（或留默认）。
6. 添加环境变量（见下一步），然后点 Deploy，Koyeb 会自动拉取代码、构建 Docker 镜像并启动。

## 第 3 步：设置环境变量（Koyeb 控制台 → 该 Service → Settings → Environment）
| Key | Value | 说明 |
|---|---|---|
| `OTREE_PRODUCTION` | `1` | 关闭 DEBUG |
| `OTREE_AUTH_LEVEL` | `STUDY` | 参与者免登录直接填；管理端需密码 |
| `OTREE_ADMIN_PASSWORD` | 一个强密码 | 管理后台登录密码 |
| `OTREE_SECRET_KEY` | 任意长随机串（如 `openssl rand -hex 32` 生成） | **必须稳定**，否则重启后会话失效 |
| `OTREE_REST_KEY` | 任意长随机串 | 用于建会话 / 导出数据的 REST API |
| `DATABASE_URL` | 第 1 步复制的 Supabase URI | 外部数据库，数据持久化 |

保存后 Koyeb 会自动构建并启动。首次启动 `start.sh` 会先跑 `bootstrap_db.py` 检测表是否存在，不存在才 `resetdb`，**绝不丢数据**。

## 第 4 步：建会话 + 拿到分享链接（400 人共用一个链接）
方式 A（推荐，REST API，无需点界面）：
```bash
curl -X POST https://<你的koyeb域名>.koyeb.app/api/sessions \
  -H "otree-rest-key: <OTREE_REST_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"session_config_name":"carbon_survey","num_participants":400,"room_name":"carbon"}'
```
方式 B：登录管理后台 `https://<域名>/login` → Sessions → Create session，选 `carbon_survey`、400 人、Room 选 `carbon`。

**分享给参与者的唯一链接**（任意设备/网络、微信里也能开）：
```
https://<你的koyeb域名>.koyeb.app/room/carbon
```
打开后是欢迎页，点"开始"即进入问卷。

## 第 5 步：保活（防止免费实例空闲休眠）
Koyeb 免费服务在零流量时会自动缩容/休眠，首次请求有约 1–2 秒冷启动。用 cron-job.org 保活：
1. 注册 https://cron-job.org → Create cronjob。
2. URL 填 `https://<你的koyeb域名>.koyeb.app/room/carbon`。
3. 频率 **每 10 分钟** 一次（不要勾"仅当宕机时"），保持常驻。
（cron-job.org 从你的网络可达，免费。）

## 第 6 步：在管理后台查看数据
- 管理后台：`https://<域名>/login`（用 `OTREE_ADMIN_PASSWORD` 登录）→ **Sessions** 看各会话、参与者逐条数据（含每人下载次数）。
- **导出 4 张汇总表**（含每人下载次数、总下载次数等）：
  ```bash
  curl -H "otree-rest-key: <OTREE_REST_KEY>" \
    "https://<域名>/api/export_app_custom?app=carbon&format=csv_bom" -o export.csv
  ```
  `csv_bom` 带 BOM，Excel 打开中文不乱码。也可在后台 `/ExportIndex` 页面点选导出。

---

## 备注 / 坑
- 文件系统临时：Koyeb 免费实例磁盘是临时性的，**所有问卷数据都在 Supabase**，重启/重部署不丢。
- `DATABASE_URL` 前缀必须是 `postgresql://`（不是 `postgres://`）。
- 下载计数只在浏览器**确认完整保存后**才 +1，断网不会虚高。
- 微信内打开 PDF 不能直下，页面已提示"在浏览器打开"；iPhone 下载后到"文件"App 查看。
- Koyeb 免费层仅 1 个活跃服务 —— 本项目只需 1 个，足够。
- 若 Koyeb 在你所在地区注册仍要求绑卡：退而求其次可选 Render（需国际信用卡），或把下载改成普通 HTTP 接口后部署到 PythonAnywhere（无卡但免费层不支持 WebSocket）。
- 本地调试：`otree devserver`；正式跑数据务必走上面的生产部署。

## 备选：Render（需国际信用卡）
若你后续有 Visa/Mastercard，可改用 Render（见历史版本）：New → Web Service → 连 `carbon-survey` → Docker → Free → Singapore，环境变量同上，`DATABASE_URL` 同样用 Supabase。域名形如 `*.onrender.com`。
