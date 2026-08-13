# 部署手册：碳中和宣传效果调研问卷（oTree 6 · 免费 · 国内可访问 · 无需国际信用卡）

本目录是一个完整的 oTree 6 项目，已实现：
- 32 题问卷（含 4 组随机阅读材料的 A/B 测试、注意力检测题、行为意愿与人口统计）
- 指南《日常低碳行动极简指南》**仅下载、不预览**（HTTP `Content-Disposition: attachment` 强制浏览器保存，任何平台含微信/iOS 均不内联预览）
- 服务端真实计数：每位参与者的下载次数、总下载次数、总下载人数，以及每次下载的审计明细
- 管理端可导出 4 张表（逐人答案+下载次数 / 各子会话汇总 / 各组下载统计 / 下载明细）

## 架构（全部免费、国内可访问、关机不影响收数据、无需国际信用卡）
GitHub（代码，已推送）→ **PythonAnywhere 免费 Beginner 账户（`*.pythonanywhere.com`）** → **本地 SQLite（PythonAnywhere 持久化文件系统）** → **cron-job.org** 保活。

> 为什么用 PythonAnywhere：Render / Koyeb / Railway 目前都强制绑定国际信用卡，没有 Visa/Mastercard 无法部署。PythonAnywhere 免费版**不绑卡**。
> 注意：免费版**出站白名单屏蔽非 HTTP 协议**，连不上外部 Postgres（如 Supabase 的 5432 端口），所以本方案**用 PythonAnywhere 本地 SQLite** 存数据（文件系统持久化，重启/重部署不丢）。oTree 6 默认数据库就是 SQLite，开箱即用。

已在本地验证：模型导入正常、`resetdb` 成功、下载字节级还原一致（`%PDF-` 头、317915 字节）、计数逻辑正确（连续两次下载 1→2）、`a2wsgi` 把 oTree 的 ASGI 应用成功桥接为 WSGI（PythonAnywhere 只支持 WSGI）。
GitHub 仓库已就绪：https://github.com/Louis-lab123/carbon-survey

---

## ⚠️ 免费版两个硬限制（请先读）
1. **每天仅 100 CPU 秒**。oTree 每次请求都要渲染模板+写库。400 人若**集中在 1–2 天**访问，可能撑爆配额、当天剩余时间返回 **503**，直到次日 UTC 零点重置。
   → 缓解：**把邀请分摊到一周**；或升级 PA 付费 Developer 计划（需绑卡，不在本方案内）。
2. **一个 Web 应用 / 一个免费 MySQL 也没有（SQLite 替代）**。数据在 `db.sqlite3`，位于仓库目录，持久化。请勿重复 `otree resetdb`（会清空数据）。

---

## 第 1 步：注册 PythonAnywhere（免费、不绑卡）
1. 打开 https://www.pythonanywhere.com → **Sign up** → 选 **Beginner / Free** 套餐，填用户名+密码邮箱即可（**无需信用卡**）。
2. 记下你的用户名 `<user>`，部署后域名为 `https://<user>.pythonanywhere.com`。

## 第 2 步：克隆代码 + 建虚拟环境 + 装依赖（在 PA 的 Bash 控制台里做）
进入 PA 后点顶部 **Consoles → Bash**，依次执行：
```bash
cd ~
git clone https://github.com/Louis-lab123/carbon-survey.git
cd carbon-survey
python3.10 -m venv ~/.virtualenvs/carbon-survey     # PythonAnywhere 自带 3.10；用你控制台显示的版本
source ~/.virtualenvs/carbon-survey/bin/activate
pip install -r requirements.txt                       # 装 otree 6.0.13 + psycopg2-binary + a2wsgi
```
> 仓库是 public，免登录即可 clone。装完 `otree --version` 应显示 6.0.13。

## 第 3 步：配置 Web 应用（WSGI 入口 + 环境变量）
1. 顶部 **Web** 标签 → **Add a new web app** → 选 **Manual configuration** → 选 **Python 3.10**（与第 2 步 venv 同版本）→ 下一步。
2. 在该 Web app 配置页设置这两项：
   - **Source code directory**：`/home/<user>/carbon-survey`
   - **Virtualenv**：`/home/<user>/.virtualenvs/carbon-survey`
   > 注意：**PythonAnywhere 免费 Beginner 计划在 Web 标签里没有 "Environment variables" 区域**，所以环境变量要直接写进下面的 WSGI 文件。
3. 保持 **WSGI configuration file** 为默认值 `/var/www/<user>_pythonanywhere_com_wsgi.py`，点击该链接打开编辑器。
4. **全选并删除**原文件内容，粘贴下面这段，并把 `<user>` 换成你的 PA 用户名，把 `<...>` 换成你自己的值：
   ```python
   import os
   import sys

   # PythonAnywhere 免费 Beginner 计划没有 Web 标签 "Environment variables" 区，
   # 因此把环境变量直接写在这个 WSGI 入口文件里。
   os.environ['OTREE_SETTINGS_MODULE'] = 'settings'
   os.environ['OTREE_PRODUCTION'] = '1'
   os.environ['OTREE_AUTH_LEVEL'] = 'STUDY'
   os.environ['OTREE_ADMIN_PASSWORD'] = '<设一个强密码>'
   os.environ['OTREE_SECRET_KEY'] = '<任意长随机串，务必保存好、别改>'
   os.environ['OTREE_REST_KEY'] = '<任意长随机串>'

   # 把仓库目录加入 Python 路径
   PROJECT_DIR = '/home/<user>/carbon-survey'
   sys.path.insert(0, PROJECT_DIR)

   from a2wsgi import ASGIMiddleware
   from otree.asgi import app as asgi_app

   application = ASGIMiddleware(asgi_app)
   ```
   > 不需要 `DATABASE_URL`——oTree 默认用本地 SQLite（`db.sqlite3`）。
   > `OTREE_AUTH_LEVEL=STUDY` 让参与者免登录直接填；管理后台需上面密码。
5. 保存文件（`Ctrl+S` 或点编辑器顶部 Save），回到 Web 标签。

## 第 4 步：首次初始化数据库（仅需一次）
回到 **Bash 控制台**（venv 已激活、目录在 `~/carbon-survey`）：
```bash
cd ~/carbon-survey
source ~/.virtualenvs/carbon-survey/bin/activate
otree resetdb          # 建表；首次部署只跑这一次
```
> 之后**不要**再跑 `resetdb`（会清空数据）。表建好后，重启/重部署数据都在 `db.sqlite3` 里。

## 第 5 步：启动 + 拿到域名
1. 回到 **Web** 标签，点大大的绿色 **Reload <user>.pythonanywhere.com**。
2. 稍等约 10–30 秒，打开 `https://<user>.pythonanywhere.com` 应能看到 oTree 欢迎页。
3. 确认 `https://<user>.pythonanywhere.com/room/carbon` 能进入问卷。

## 第 6 步：建会话 + 拿到分享链接（400 人共用一个链接）
方式 A（REST API，推荐）：
```bash
curl -X POST https://<user>.pythonanywhere.com/api/sessions \
  -H "otree-rest-key: <OTREE_REST_KEY>" -H "Content-Type: application/json" \
  -d '{"session_config_name":"carbon_survey","num_participants":400,"room_name":"carbon"}'
```
方式 B：登录管理后台 `https://<user>.pythonanywhere.com/login` → Sessions → Create session，选 `carbon_survey`、400 人、Room 选 `carbon`。

**分享给参与者的唯一链接**（任意设备/网络、微信里也能开）：
```
https://<user>.pythonanywhere.com/room/carbon
```

## 第 7 步：保活（防止免费 Web 应用被回收）
免费 Web 应用在无流量一段时间后会被回收（冷启动较慢）。用 cron-job.org 保活：
1. 注册 https://cron-job.org → Create cronjob。
2. URL 填 `https://<user>.pythonanywhere.com/room/carbon`。
3. 频率 **每 10 分钟** 一次（不要勾"仅当宕机时"）。

## 第 8 步：在管理后台查看 / 导出数据
- 后台：`https://<user>.pythonanywhere.com/login`（用 `OTREE_ADMIN_PASSWORD`）→ **Sessions** 看各会话、参与者逐条数据（含每人下载次数）。
- 导出 4 张汇总表：
  ```bash
  curl -H "otree-rest-key: <OTREE_REST_KEY>" \
    "https://<user>.pythonanywhere.com/api/export_app_custom?app=carbon&format=csv_bom" -o export.csv
  ```
  `csv_bom` 带 BOM，Excel 打开中文不乱码；也可在后台 `/ExportIndex` 点选导出。

---

## 备注 / 坑
- 数据在 `~/carbon-survey/db.sqlite3`（持久化）；**切勿重复 `otree resetdb`**。
- 升级代码：在 Bash 控制台 `cd ~/carbon-survey && git pull`，再回 Web 标签 **Reload** 即可。
- 微信里打开 PDF 不能直下，页面已提示"在浏览器打开"；iPhone 下载后到"文件"App 查看。
- PythonAnywhere 免费域名自带 HTTPS；无自定义域名（付费才有）。
- 若某天访问返回 503，多半是触了 100 CPU 秒上限，等次日 UTC 零点自动恢复；下次把邀请分摊开。
- 仓库里的 `.replit` 是给 Replit 用的，**在 PythonAnywhere 上忽略它即可**（PA 不读该文件）。
- 若日后你能用上 Replit（解决浏览器完整性校验），可切回 Supabase Postgres 方案——代码无需改，只是环境变量不同。
- 本地调试：`otree devserver`；正式跑数据务必走上面的生产部署。
