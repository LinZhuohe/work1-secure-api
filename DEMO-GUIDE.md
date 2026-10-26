# Work 1 现场演示稿（Demo Script + 答辩要点）

> 林卓赫 · 23320224 · 选题：CVE-2021-42013
> 技术栈：Python / Flask + SQLAlchemy + bcrypt + PyJWT ｜ CI：GitHub Actions ｜ CVE：Docker + Vulhub
> 建议演示时长：6–8 分钟。

---

## 〇、开演前 5 分钟自检（照着敲一遍，出全绿再开始）

开一个 PowerShell 窗口，逐条执行：

```powershell
cd "C:\Users\32905\Desktop\[HDU-CS4-26-27-1] Information Security\work1-secure-api"
docker ps --format "{{.Names}}`t{{.Status}}`t{{.Ports}}"   # 应看到 8080 / 8081 两个容器 Up
curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8080/   # 200
curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8081/   # 200
```

全部正常后再按下面的顺序演示。**容器没起**才需要：

```powershell
cd "C:\Users\32905\Desktop\[HDU-CS4-26-27-1] Information Security\work1-secure-api\cve\CVE-2021-42013\vulnerable"; docker compose up -d
cd "C:\Users\32905\Desktop\[HDU-CS4-26-27-1] Information Security\work1-secure-api\cve\CVE-2021-42013\fixed"; docker compose up -d
```

> ⚠️ 两个坑（这条最重要）
> 1. 路径里有方括号 `[ ]`，**不要**用 `powershell -File xxx.ps1` 启动，会报「指定的通配符模式无效」。正确做法：先 `cd` 进目录，再敲 `.\demo-api.ps1`。
> 2. **不要**在资源管理器里双击 .ps1；也不要用 `Start-Process`。就手动在窗口里敲命令，方便讲解和截图。

---

## 〇.5、时间轴（8 分钟版）

| 时间 | 做什么 | 说什么（一句话） |
|---|---|---|
| 0:00–1:00 | 浏览器：仓库 → Actions → 最新 run → Artifacts | "每次 push 自动跑测试 + SAST + SCA" |
| 1:00–3:00 | `cd` 项目根 → `.\demo-api.ps1`（6 项） | "6 个安全检查，401/201/转义全在这" |
| 3:00–5:00 | `cd` 到 cve 目录 → `.\screenshot.ps1` | "同一载荷：漏洞版 200，修复版 400" |
| 5:00–6:00 | 打开报告 PDF / README | "根因 + 修复 + 验证都写进文档" |
| 6:00–8:00 | 答辩问答 | 见第五节 |

---

## 一、30 秒开场白（照着念）

> "我做的是 Work 1，包含两部分：第一，用 Flask 开发了一个安全的 REST API，实现了登录、JWT 鉴权和数据接口，并针对 SQL 注入、XSS、弱口令做了防护；第二，用 GitHub Actions 搭建了 CI/CD，每次提交自动做静态代码扫描（SAST/bandit）和依赖漏洞扫描（SCA/OWASP Dependency-Check）。最后我用 Vulhub 复现了一个真实漏洞 CVE-2021-42013（Apache 路径穿越+命令执行），分析了根因，升级版本修复并验证。所有代码都在我的 GitHub 公开仓库。"

---

## 二、现场演示流程（按顺序操作）

### 第 1 步：仓库与 CI（约 1 分钟）
打开 https://github.com/LinZhuohe/work1-secure-api
- **点 Code**：展示结构——`app.py`(3 个接口)、`auth_utils.py`(认证)、`security.py`(XSS)、`models.py`(ORM)、`.github/workflows/ci.yml`(流水线)、`cve/`(CVE 全套)。
- **点 Actions**：展示每次提交都自动跑、全部绿色。
- **点最新 run → 底部 Artifacts**：下载并打开 `bandit-report`（SAST）和 `dependency-check-report`（SCA）。

**一句话**："我配置了 SAST 静态扫描看我自己写的代码有没有漏洞，SCA 扫描第三方依赖里有没有已知 CVE，每次 push 自动执行并出报告。"

### 第 2 步：现场演示 API（约 2 分钟）
PowerShell 里：
```powershell
cd "C:\Users\32905\Desktop\[HDU-CS4-26-27-1] Information Security\work1-secure-api"
.\demo-api.ps1
```
边出结果边讲解（脚本会自动起停 Flask，依次显示 6 项）：
1. 正确账号登录 → 200，返回 JWT；
2. 错误密码 → 401；
3. SQL 注入 `' OR '1'='1` 登录 → 401（被参数化查询挡住）；
4. 不带 token 访问数据 → 401；
5. 带正确 token → 200 拿到用户列表；
6. 提交含 `<script>` 的文章 → 201，内容被转义成 `&lt;script&gt;`。

### 第 3 步：现场演示 CVE（约 2 分钟）
PowerShell 里：
```powershell
cd "C:\Users\32905\Desktop\[HDU-CS4-26-27-1] Information Security\work1-secure-api\cve\CVE-2021-42013"
.\screenshot.ps1
```
- **PART 1（漏洞版 2.4.50，端口 8080）**：
  - 路径穿越读到服务器的 `/etc/passwd`（HTTP 200）；
  - 进一步执行命令 `id`，返回 `uid=1(daemon)`（RCE，HTTP 200）。
- **PART 2（修复版 2.4.51，端口 8081）**：
  - 同样的攻击全部返回 **400 Bad Request**；
  - 正常首页仍返回 **200**（回归测试，说明没把服务改坏）。

> 演示时强调："两个版本我故意保留了完全相同的高风险配置（都开 CGI、放开根目录），**唯一差别就是 Apache 版本**，所以能证明漏洞确实是版本缺陷导致的。"

---

## 三、"我做了什么 / 用了什么方法"（讲清原理）

### 1. 安全 API
- **SQL 注入**：用 SQLAlchemy ORM，`filter_by(username=...)` 走**绑定变量（参数化查询）**，用户输入永远不拼进 SQL。
- **XSS**：用 `markupsafe.escape` 对用户输入做 **HTML 输出编码**，`<script>` 变 `&lt;script&gt;`，浏览器不执行。
- **认证（JWT + bcrypt）**：
  - 密码用 **bcrypt** 哈希（自带随机盐、工作因子可调、校验是常数时间比较），数据库只存哈希；
  - 登录成功签发 **HS256 JWT**，带 `iat/exp`（1 小时过期），中间件对每个受保护接口验签，失败一律 401；
  - 校验时**显式指定算法 `HS256`**，防算法混淆；用户不存在和密码错误返回相同 401，防账号枚举。

### 2. CI/CD
- `.github/workflows/ci.yml`：checkout → 装依赖 → 跑单元测试 → **bandit（SAST）** → **OWASP Dependency-Check（SCA）**，报告作为 artifact 上传。
- 每次 push / PR 自动运行。

### 3. CVE-2021-42013
- **现象**：Apache 2.4.49 有路径穿越（CVE-2021-41773），2.4.50 打补丁但不完整，攻击者用**双重 URL 编码**绕过，即 CVE-2021-42013。
- **绕过原理（重点）**：
  ```
  .%%32%65
   第一次解码：%32→2、%65→e  ⇒  .%2e   （补丁只看到字面 %，放行）
   第二次解码：%2e→.          ⇒  ..     （7 个 .. 跳出网站根目录）
  ```
- **根因**：路径规范化函数 `ap_normalize_path` 只解码/检查了一层（CWE-177 编码处理不彻底），补丁靠黑名单特征匹配而不是保证路径仍在允许目录内（CWE-22）；开 CGI 时还能指向 `/bin/sh` 形成命令执行（CWE-78）。
- **修复**：升级到 2.4.51；纵深防御是根目录别放开、非必要不开 CGI、加 WAF。
- **验证**：同样的攻击从 200 变 400，正常页面仍 200。

---

## 四、交付物清单（对照"老师要什么"）

1. 公开仓库：https://github.com/LinZhuohe/work1-secure-api
2. README.md：API 说明、安全措施、SAST/SCA 报告、CVE 编号+描述+复现+根因+修复+验证
3. 最后成功 pipeline 链接：https://github.com/LinZhuohe/work1-secure-api/actions
4. 修复文件文件夹：`cve/CVE-2021-42013/fixed/`（vulnerable/fixed 两套对比）
5. 封面：实验编号/标题、variant、姓名（林卓赫）、学号（23320224）

---

## 五、老师可能问的问题（控制问题，简答版）

1. **bcrypt 为什么比 SHA-256 好？** SHA-256 是快速哈希、无盐，易被彩虹表和暴力破解；bcrypt 自带随机盐、工作因子可调、故意算得慢，抗暴力破解。
2. **SAST 和 DAST 区别？** SAST 静态扫描，看源码/字节码、不运行程序（我用的 bandit）；DAST 动态扫描，运行时从外部发请求测漏洞（Work 2 的 ZAP）。
3. **JWT 原理？** 服务端用密钥对"用户+签发时间+过期时间"做签名生成令牌；客户端请求时带上，服务端验签和有效期，内容没加密但不可篡改。
4. **不审计第三方依赖的风险？** 依赖里的已知 CVE 会被直接带进来，依赖链越深越难发现，攻击者可利用现成漏洞。
5. **Docker/Vulhub 的优势？** 一键复现、环境隔离不污染本机、可随时销毁重建、每个人环境一致。
6. **漏洞（vulnerability）和利用（exploit）的区别？** 漏洞是系统里的缺陷本身；利用是实际利用该缺陷的代码/手法。我这次既展示了漏洞（路径穿越），也演示了利用（读到 passwd、执行命令）。
7. **修复后为什么还要回归测试？** 补丁可能影响正常功能；要确认攻击被挡住的同时，业务依旧可用（我这里修复版首页仍 200）。
8. **复现 CVE 对安全工作有什么用？** 理解攻击链才能做防御；渗透测试用它验证暴露面，SOC 分析师用它判断告警、评估影响和处置。
