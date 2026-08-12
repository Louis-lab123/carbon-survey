# 部署手册：碳中和宣传效果调研问卷（oTree 6 · 免费 · 国内可访问 · 无需国际信用卡）

本目录是一个完整的 oTree 6 项目，已实现：
- 32 题问卷（含 4 组随机阅读材料的 A/B 测试、注意力检测题、行为意愿与人口统计）
- 指南《日常低碳行动极简指南》**仅下载、不预览**（通过 HTTP `Content-Disposition: attachment` 强制浏览器保存，任何平台/浏览器含微信/iOS 均不会内联预览）
- 服务端真实计数：每位参与者的下载次数、总下载次数、总下载人数，以及每次下载的审计明细
- 管理端可导出 4 张表（逐人答案+下载次数 / 各子会话汇总 / 各组下载统计 / 下载明细）

## 架构（全部免费、国内可访问、关机不影响收数据、无需国际信用卡）
GitHub（代码，已推送）→ **Replit 免费 Python 服务（`*.repl.co`）** → **Supabase 免费 Postgres**（数据持久化）→ **cron-job.org** 保活。

> 为什么不用 Render / Koyeb / Railway：这三家目前**都强制绑定国际信用卡**（预授权 1 美元或要求付款方式）才能部署，没有 Visa/Mastercard 无法上线。
> **Replit 免费层不绑卡**，支持从 GitHub 直接拉 Python 项目、自动按 `requirements.txt` 安装依赖，国内访问 `replit.com` 正常（已实测 HTTP 200）。因此作为主方案。

已在本地验证：模型导入正常、`resetdb` 成功、下载字节级还原一致（`%PDF-` 头、317915 字节）、计数逻辑正确（连续两次下载 1→2）。
GitHub 仓库已就绪：https://github.com/Louis-lab123/carbon-survey

---

## 第 1 步：Supabase 数据库（免费、不过期）— 你已建好，只需拿到 URI
1. 打开 https://supabase.com → 进入你的 Project。
2. 左侧主菜单点 **Database**（不是 Settings）→ 页面顶部找 **Connection string / URI**，形如：
   `postgresql://postgres:密码@db.xxxx.supabase.co:5432/postgres`
   - 若页面只显示密码框、不显示完整串，手动拼：`postgresql://postgres:<你的密码>@db.uyanhgxnsucpkhvrmcfb.supabase.co:5432/postgres`（密码忘了可 Reset password）。
3. **Settings → Database → 打开 "Allow access from anywhere"**（否则 Replit 连不上）。
4. 区域选 **Singapore（新加坡）**，离国内近。
5. 把完整 `postgresql://...` 串（含密码）**只填进 Replit 的环境变量 `DATABASE_URL`**，不要发到聊天里。

> 不要用 Replit 自带的数据库：本项目的问卷数据全部存 Supabase，重启/重部署不丢。Supabase 免费版 500MB、长期有效（约 7 天无活动才暂停，有 cron 保活不会触发）。

## 第 2 步：Replit 部署（免费、无需信用卡）
1. 打开 https://replit.com 注册（建议用 GitHub 登录，与你的仓库同一账号）。
2. 首页点 **Create Repl → Import from GitHub** → 授权并选中仓库 `Louis-lab123/carbon-survey`，语言选 **Python**，点 **Import**。
   - 仓库根目录已含 `.replit` 文件，Replit 会自动用里面的 `run` 命令启动：
     `otree prodserver 0.0.0.0:${PORT:-8000}`
   - Replit 会自动读取 `requirements.txt` 安装 oTree 6.0.13 等依赖（首次构建约 1–2 分钟）。
3. 构建完成后点 **Run**，等日志出现 `Uvicorn running on ...` 即启动成功；页面右上角会显示你的域名，形如：
   `https://carbon-survey.<你的replit用户名>.repl.co`

> 若 Replit 没自动识别 `.replit`，可在侧边文件树确认仓库里有 `.replit`；或手动在 Console 跑：
> `pip install -r requirements.txt && otree prodserver 0.0.0.0:$PORT`

## 第 3 步：设置环境变量（Replit 左侧工具条 → Secrets / Environment Variables）
点 **Tools → Secrets**（旧版叫 Environment Variables），逐项添加：
| Key | Value | 说明 |
|---|---|---|
| `OTREE_PRODUCTION` | `1` | 关闭 DEBUG |
| `OTREE_AUTH_LEVEL` | `STUDY` | 参与者免登录直接填；管理端需密码 |
| `OTREE_ADMIN_PASSWORD` | 一个强密码 | 管理后台登录密码 |
| `OTREE_SECRET_KEY` | 任意长随机串（如 `openssl rand -hex 32` 生成） | **必须稳定**，否则重启后会话失效 |
| `OTREE_REST_KEY` | 任意长随机串 | 用于建会话 / 导出数据的 REST API |
| `DATABASE_URL` | 第 1 步复制的 Supabase URI | 外部数据库，数据持久化 |

保存后 Replit 会重启服务。首次启动 oTree 会按 `DATABASE_URL` 自动建表，数据落在 Supabase，**绝不丢数据**。

## 第 4 步：建会话 + 拿到分享链接（400 人共用一个链接）
方式 A（推荐，REST API，无需点界面）：
```bash
curl -X POST https://carbon-survey.<你的replit用户名>.repl.co/api/sessions \
  -H "otree-rest-key: <OTREE_REST_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"session_config_name":"carbon_survey","num_participants":400,"room_name":"carbon"}'
```
方式 B：登录管理后台 `https://<域名>/login` → Sessions → Create session，选 `carbon_survey`、400 人、Room 选 `carbon`。

**分享给参与者的唯一链接**（任意设备/网络、微信里也能开）：
```
https://carbon-survey.<你的replit用户名>.repl.co/room/carbon
```
打开后是欢迎页，点"开始"即进入问卷。

## 第 5 步：保活（防止免费实例空闲休眠）
Replit 免费实例在零流量约 1 小时后会休眠，首次请求有约数秒冷启动。用 cron-job.org 保活：
1. 注册 https://cron-job.org → Create cronjob。
2. URL 填 `https://carbon-survey.<你的replit用户名>.repl.co/room/carbon`。
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
- 数据持久化：所有问卷数据都在 Supabase，Replit 实例重启/重部署不丢。
- `DATABASE_URL` 前缀必须是 `postgresql://`（不是 `postgres://`）。
- 下载计数只在浏览器**确认完整保存后**才 +1，断网不会虚高。
- 微信内打开 PDF 不能直下，页面已提示"在浏览器打开"；iPhone 下载后到"文件"App 查看。
- Replit 免费层仅 1 个活跃 Repl（本项目只需 1 个，足够）；如需"Always On"永不停机需升级付费 Core 计划，非必须。
- 部署方式采用的是**纯 HTTP 下载**（非 WebSocket）：兼容性最好、任何 PaaS 都能跑；也因此本项目不再依赖 WebSocket 支持平台。
- 本地调试：`otree devserver`；正式跑数据务必走上面的生产部署。
