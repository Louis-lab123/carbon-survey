# 部署手册：碳中和宣传效果调研问卷（oTree 6 · 免费 · 国内可访问）

本目录是一个完整的 oTree 6 项目，已实现：
- 32 题问卷（含 4 组随机阅读材料的 A/B 测试、注意力检测题、行为意愿与人口统计）
- 指南《日常低碳行动极简指南》**仅下载、不预览**（通过 WebSocket 分块下发 + Blob 强制保存，任何浏览器含微信/iOS 均不会内联预览）
- 服务端真实计数：每位参与者的下载次数、总下载次数、总下载人数，以及每次下载的审计明细
- 管理端可导出 4 张表（逐人答案+下载次数 / 各子会话汇总 / 各组下载统计 / 下载明细）

## 架构（全部免费、国内可访问、关机不影响收数据）
GitHub（代码）→ **Render 免费 Web 服务（Docker）** → **Supabase 免费 Postgres**（数据持久化）→ **cron-job.org** 保活。

已在本地验证：模型导入正常、`resetdb` 成功、下载字节级还原一致、计数逻辑正确。

---

## 第 0 步：本地自检（可选）
```bash
# 在 carbon_survey 目录下，使用本项目对应的 Python 虚拟环境
otree resetdb --noinput
python verify.py      # 应输出 ALL CHECKS PASSED
```

## 第 1 步：推送到 GitHub
```bash
cd carbon_survey
git init
git add -A
git commit -m "oTree6 carbon survey with secure guide download + counting"
git branch -M main
git remote add origin https://github.com/<你的用户名>/carbon-survey.git
git push -u origin main
```
（也可由 WorkBuddy 代推，需提供 GitHub Personal Access Token，见文末。）

## 第 2 步：创建 Supabase 数据库（免费、不过期）
1. 打开 https://supabase.com 注册并 New Project。
2. 进入 Project → **Settings → Database**，复制 URI（形如
   `postgresql://postgres:密码@db.xxxx.supabase.co:5432/postgres`）。
   - 把其中的 `[PASSWORD]` 替换为真实密码。
   - 前缀必须是 `postgresql://`（不是 `postgres://`）。
3. **Settings → Database → Connection → 打开 "Allow access from anywhere"**（否则 Render 连不上）。
4. 区域选 **Singapore（新加坡）** 或 Northeast Asia，离国内近。

> 不要用 Render 自带的免费 Postgres：它 30 天后会被删除并清空数据。Supabase 免费版 500MB、长期有效。

## 第 3 步：Render 部署（免费）
1. 打开 https://render.com 注册（可用 GitHub 登录）。
2. **New → Blueprint**（或 New → Web Service → 连接 GitHub 仓库 `carbon-survey`）。
3. 运行时选 **Docker**（仓库里有 Dockerfile，会自动识别）。
4. 计划选 **Free**。
5. 实例区域选 **Singapore**。

## 第 4 步：设置环境变量（Render 控制台 → 该服务 → Environment）
| Key | Value | 说明 |
|---|---|---|
| `OTREE_PRODUCTION` | `1` | 关闭 DEBUG |
| `OTREE_AUTH_LEVEL` | `STUDY` | 参与者免登录直接填；管理端需密码 |
| `OTREE_ADMIN_PASSWORD` | 一个强密码 | 管理后台登录密码 |
| `OTREE_SECRET_KEY` | 任意长随机串（Render 可 `Generate`） | **必须稳定**，否则重启后会话失效 |
| `OTREE_REST_KEY` | 任意长随机串 | 用于建会话 / 导出数据的 REST API |
| `DATABASE_URL` | 第 2 步复制的 Supabase URI | 外部数据库，数据持久化 |

保存后 Render 会自动构建并启动。首次启动 `start.sh` 会 `bootstrap_db.py` 检测表是否存在，不存在才 `resetdb`，**绝不丢数据**。

## 第 5 步：建会话 + 拿到分享链接（400 人共用一个链接）
方式 A（推荐，REST API，无需点界面）：
```bash
curl -X POST https://<你的render域名>.onrender.com/api/sessions \
  -H "otree-rest-key: <OTREE_REST_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"session_config_name":"carbon_survey","num_participants":400,"room_name":"carbon"}'
```
方式 B：登录管理后台 `https://<域名>/login` → Sessions → Create session，选 `carbon_survey`、400 人、Room 选 `carbon`。

**分享给参与者的唯一链接**（任意设备/网络、微信里也能开）：
```
https://<你的render域名>.onrender.com/room/carbon
```
打开后是欢迎页，点"开始"即进入问卷。

## 第 6 步：保活（防止免费实例休眠）
Render 免费实例 15 分钟无流量会休眠（约 1 分钟唤醒）。用 cron-job.org：
1. 注册 https://cron-job.org → Create cronjob。
2. URL 填 `https://<你的render域名>.onrender.com/room/carbon`。
3. 频率 **每 10 分钟** 一次（不要勾"仅当宕机时"）。
这样每月约 744 小时流量，低于免费 750 小时上限。

## 第 7 步：在管理后台查看数据
- 管理后台：`https://<域名>/login`（用 `OTREE_ADMIN_PASSWORD` 登录）→ **Sessions** 看各会话、参与者逐条数据。
- **导出 4 张汇总表**（含每人下载次数、总下载次数等）：
  ```bash
  curl -H "otree-rest-key: <OTREE_REST_KEY>" \
    "https://<域名>/api/export_app_custom?app=carbon&format=csv_bom" -o export.csv
  ```
  `csv_bom` 带 BOM，Excel 打开中文不乱码。也可在后台 `/ExportIndex` 页面点选导出。

---

## 备注 / 坑
- 文件系统临时：Render 免费实例磁盘是临时性的，**所有数据都在 Supabase**，重启不丢。
- `DATABASE_URL` 前缀必须是 `postgresql://`。
- 下载计数只在浏览器**确认完整保存后**才 +1，断网不会虚高。
- 微信内打开 PDF 不能直下，页面已提示"在浏览器打开"；iPhone 下载后到"文件"App 查看。
- 本地调试：`otree devserver`；正式跑数据务必走上面的生产部署。

## 如需 WorkBuddy 代推 GitHub
提供 **GitHub Personal Access Token（repo 权限）** 即可，我会初始化仓库并推送到 `carbon-survey`。
