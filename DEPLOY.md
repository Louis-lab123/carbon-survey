# PythonAnywhere 免费部署完整教程（小白版 · 一步一步照做）

适用对象：从没碰过服务器、命令行的人。
前提：一个能收验证码的邮箱 + 一个 GitHub 账号。**不需要信用卡、不花钱。**
目标：把"碳中和宣传效果调研"问卷（32 题 + 指南 PDF 强制下载 + 下载计数）跑在
`https://sylace.pythonanywhere.com` 上，400 人共用一个链接填写。

> 你之前已经做过一部分（建了 Web app、clone 了代码）。如果某一步你已经做过了，
> 直接跳到没做的那一步继续。全文以用户名 **Sylace** 为例，请自行替换成你的真实用户名。

---

## 第 1 步：注册 PythonAnywhere

1. 浏览器打开 https://www.pythonanywhere.com/
2. 点右上角 **Register**（或 "Create a free account"）。
3. 填：用户名、邮箱、密码 → 计划选 **Beginner**（页面写 Free / 不收费）→ 提交。
4. 去邮箱点验证链接（没收到就翻垃圾箱）。
5. 登录后进入控制台主页。✅

---

## 第 2 步：开一个“黑框框”终端（Bash 控制台）

1. 顶部点 **Consoles** 标签。
2. 点 **New console** 下面的蓝色按钮 **`$ Bash`**。
3. 浏览器弹出一个黑框（这就是命令行）。以后所有命令都打在这里。

> 在黑框里粘贴命令的方法：先用鼠标**点一下黑框里面**（让光标闪），再按
> `Ctrl+V`（Mac 用 `Cmd+V`；不行就试 `Ctrl+Shift+V`，或右键 → Paste），最后按回车。

---

## 第 3 步：把问卷代码下载到 PythonAnywhere

在黑框里**一行一行**粘贴，每行回车：

```bash
cd ~
git clone https://github.com/Louis-lab123/carbon-survey.git
ls carbon-survey
```

最后看到列出一堆文件（含 `wsgi.py`、`requirements.txt`、`settings.py`、`carbon/`、`carbon/guide.pdf`）就成功。

> 如果报 "Authentication failed"：说明 GitHub 仓库是私有的。去 GitHub 把
> `Louis-lab123/carbon-survey` 设为 Public（仓库 Settings → 最底下 Change visibility → Public），
> 然后重跑 `git clone ...` 那一行。

---

## 第 4 步：建独立 Python 环境并装依赖

继续在黑框粘贴（每行回车）：

```bash
python3.10 -m venv ~/.virtualenvs/carbon-survey
source ~/.virtualenvs/carbon-survey/bin/activate
pip install -r ~/carbon-survey/requirements.txt
```

- 第 2 行之后，黑框最前面会出现 `(carbon-survey)` 字样 → 说明“激活”成功。
- 第 3 行要等 **2–5 分钟**（联网装 otree 等包），看到 `Successfully installed ...` 才完。
  期间**别关黑框**。

---

## 第 5 步：在 PA 后台建网站（Web app）

1. 顶部点 **Web** 标签 → 点 **Add a new web app** → 一路 **Next**。
2. 到 "Manual configuration"（手动配置）这一项，**选它** → Python 版本选 **Python 3.10** → Next。
3. 出现应用设置页。本步只先记下页面，先去第 6 步改 WSGI 文件内容。

> 说明：免费 Beginner 计划里，“WSGI configuration file”那个**路径框是灰的、改不了**，
> 它固定是 `/var/www/sylace_pythonanywhere_com_wsgi.py`。我们不去改路径，而是**直接改这个文件的内容**。

---

## 第 6 步：编辑 WSGI 文件（最关键的一步）

1. 在 Web 应用设置页找到 **WSGI configuration file**，点它右边那个链接
   （形如 `.../files/var/www/sylace_pythonanywhere_com_wsgi.py?edit`），打开在线编辑器。
2. 在编辑器里**全选并删除**原有所有内容（`Ctrl+A` 再按删除键）。
3. 粘贴下面这段（用户名已替你写死 `Sylace`，你只需改 3 处中文占位符）：

```python
import os
import sys

# ===== 环境变量（免费版没有 Environment variables 界面，写在这里）=====
os.environ['OTREE_SETTINGS_MODULE'] = 'settings'
os.environ['OTREE_PRODUCTION'] = '1'
os.environ['OTREE_AUTH_LEVEL'] = 'STUDY'

# 下面三行改成你自己的值（把单引号里的中文替换掉）
os.environ['OTREE_ADMIN_PASSWORD'] = '在这里写你的后台登录密码'
os.environ['OTREE_SECRET_KEY'] = '在这里写第一串随机字符'
os.environ['OTREE_REST_KEY'] = '在这里写第二串随机字符'

# ===== 项目目录（用户名 Sylace 已写死）=====
PROJECT_DIR = '/home/Sylace/carbon-survey'
sys.path.insert(0, PROJECT_DIR)

# 关键两行：oTree 6 生产模式要用相对目录 _static，必须先切到项目根，否则崩溃
os.chdir(PROJECT_DIR)
os.makedirs('_static', exist_ok=True)

from a2wsgi import ASGIMiddleware
from otree.asgi import app as asgi_app

application = ASGIMiddleware(asgi_app)
```

4. 按 **`Ctrl+S`** 保存（或点编辑器顶部的 **Save**）。
5. 关掉编辑器，回到 **Web** 标签。

> 那三处随机字符怎么来：回到第 2 步的 Bash 黑框，运行下面命令**两次**，
> 各得到一串乱码，分别填进 `OTREE_SECRET_KEY` 和 `OTREE_REST_KEY`：
> ```bash
> python3.10 -c "import secrets;print(secrets.token_urlsafe(40))"
> ```
> （`OTREE_SECRET_KEY` 一旦定下**千万别改**，改了已收问卷会作废。）

---

## 第 7 步：设 Source code 和 Virtualenv（这两个框可编辑）

在 Web 应用设置页的 **Code** 区，确认/填写这两项（普通输入框，点一下就能改）：

- **Source code**：`/home/Sylace/carbon-survey`
- **Virtualenv**：`/home/Sylace/.virtualenvs/carbon-survey`

改完点旁边的小对勾/保存。

> 注：免费版 Web 标签**没有 “Environment variables” 区域**——所以我们在第 6 步把
> 环境变量写进了 WSGI 文件，不需要在这个页面找环境变量框（找不到是正常的）。

---

## 第 8 步：初始化数据库（整个项目只做这一次！）

回 Bash 黑框：

```bash
cd ~/carbon-survey
source ~/.virtualenvs/carbon-survey/bin/activate
otree resetdb
```

看到它列一堆表名、最后说 `Creating tables...` 完成就 OK。
> 🚨 **严重警告**：`otree resetdb` 会清空所有已收数据。整个生命周期**只跑这一次**，以后绝不再跑。

---

## 第 9 步：重新加载网站 + 测试

1. 回 **Web** 标签，点页面最上方的绿色大按钮 **Reload sylace.pythonanywhere.com**。
2. **免费版首次重载很慢（1–2 分钟）**，PA 可能提示“无法确认是否 reload 成功”——
   **忽略它**，直接去开下面的链接验证。
3. 浏览器开这 3 个（把 `sylace` 换成你的用户名）：
   - `https://sylace.pythonanywhere.com/` → 欢迎页
   - `https://sylace.pythonanywhere.com/room/carbon` → 问卷开始页（**这就是最后发给 400 人的链接**）
   - `https://sylace.pythonanywhere.com/login` → 管理后台登录（用第 6 步的 `OTREE_ADMIN_PASSWORD` 登）

三个都能开 = 部署成功 🎉

---

## 第 10 步：把两样发给我，我收尾

测试成功后，把下面两样发我：
- **① 你的 PA 域名**：`https://sylace.pythonanywhere.com`
- **② 你第 6 步填的 `OTREE_REST_KEY`**

我会替你做完剩下的：
- 用 REST 一键建好 **400 人共用会话**（`room=carbon`），给你唯一分享链接；
- 配好 **cron-job.org 每 10 分钟保活**（防止免费实例变慢）；
- 告诉你管理后台怎么看**每人下载次数**、怎么导出 4 张汇总表。

---

## 附录 A：常见报错对照（小白急救）

### “something went wrong”
这是 PA 的应用崩溃页。真正的错误在日志里。在 Bash 黑框跑：
```bash
tail -40 /var/log/sylace.pythonanywhere.com.error.log
```
把最后的红色文字发我。

### `RuntimeError: Directory '_static' does not exist`
说明 WSGI 文件里**缺了** `os.chdir(PROJECT_DIR)` 和 `os.makedirs('_static', exist_ok=True)`
这两行。回到第 6 步，确认那段代码**完整**粘贴并保存，再 Reload。

### 改了 WSGI 还是老样子
日志时间戳没变 → 说明没真正 reload。在 WSGI 文件末尾加个空行 → 保存 → 再点 Reload → 等 2 分钟。

### ImportError: No module named 'a2wsgi'
`a2wsgi` 没装进 venv。Bash 里跑：
```bash
source ~/.virtualenvs/carbon-survey/bin/activate
pip install a2wsgi
```
装完 Reload。

---

## 附录 B：免费版硬限制（务必知道）

- **每天仅 100 CPU 秒**：400 人若挤在 1–2 天填，可能触发 503（次日 UTC 零点自动恢复）。
  **把邀请分摊到一周**最稳。
- **MySQL：无** → 所以用本地 SQLite（`db.sqlite3`，PA 磁盘持久化、重启不丢）。
- **始终在线任务 / 计划任务：无** → 不需要，我们用 cron-job.org 外部保活。
- **Environment variables 界面：无** → 环境变量写在 WSGI 文件里（第 6 步已做）。
