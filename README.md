# Work 1: Secure REST API Development with CI/CD and Real CVE Vulnerability Analysis

- 课程：Information Security（HDU，杭州电子科技大学）
- 实验：Work 1（10 分）
- 技术栈：Python 3 / Flask + SQLAlchemy + bcrypt + PyJWT
- 仓库：<https://github.com/LinZhuohe/work1-secure-api>
- 最近一次成功的 CI Pipeline：<https://github.com/LinZhuohe/work1-secure-api/actions>

---

## 1. 项目结构

```
work1-secure-api/
├── app.py                # Flask 主程序：3 个接口
├── models.py             # 数据模型 User / Post（SQLAlchemy ORM，防 SQLi）
├── auth_utils.py         # bcrypt 密码哈希 + JWT 签发/校验 + require_auth 装饰器
├── security.py           # XSS 输出编码（markupsafe.escape）
├── test_api.py           # unittest 接口/安全测试（登录、JWT、SQLi、XSS）
├── requirements.txt      # 锁定精确版本的依赖
├── .github/workflows/ci.yml   # GitHub Actions：SAST + SCA + 单元测试
└── cve/CVE-2021-42013/       # 真实 CVE 复现、根因、修复、验证（见该目录 README）
    ├── vulnerable/  fixed/  verify.ps1  evidence/  README.md
```

---

## 2. API 说明

本地启动：

```bash
pip install -r requirements.txt
python app.py          # 监听 http://127.0.0.1:5000
```

启动时自动建表并预置账号 `admin / Admin123!`（可用环境变量 `SEED_PASSWORD`、`JWT_SECRET` 覆盖）。

| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| POST | `/auth/login` | 无 | 登录，校验通过后签发 JWT |
| GET | `/api/data` | JWT | 获取用户列表（仅认证用户） |
| POST | `/api/posts` | JWT | 创建文章（自拟接口，演示 XSS 转义） |

### 2.1 登录获取 token

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'
# 200: {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."}
# 密码错误 / 缺字段: 401 / 400
```

### 2.2 携带 token 访问受保护接口

```bash
# 无 token
curl http://127.0.0.1:5000/api/data
# 401: {"error":"Unauthorized: missing or invalid token"}

# 带 token
curl http://127.0.0.1:5000/api/data -H "Authorization: Bearer <TOKEN>"
# 200: {"users":[{"id":1,"username":"admin"}]}
```

### 2.3 创建文章（XSS 转义）

```bash
curl -X POST http://127.0.0.1:5000/api/posts \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"title":"hi","content":"<script>alert(1)</script>"}'
# 201，返回的 content 为转义后的 &lt;script&gt;alert(1)&lt;/script&gt;
```

---

## 3. 安全措施

### 3.1 认证与会话（JWT + bcrypt）
- 口令使用 **bcrypt** 哈希存储：自带随机盐、可调工作因子，`checkpw` 为常数时间比较，抗彩虹表/暴力破解/时序攻击；数据库只存哈希、不存明文。
- 登录成功签发 **HS256 JWT**，载荷含 `sub / iat / exp`（1 小时过期）；密钥从环境变量 `JWT_SECRET` 读取。
- 校验时**显式指定 `algorithms=["HS256"]`**，防止算法混淆攻击；验签与过期由 PyJWT 完成。
- 受保护接口用 `@require_auth` 装饰，无有效 token 一律 401。
- 用户不存在与密码错误返回**相同的 401 与文案**，避免账号枚举。

### 3.2 SQL 注入防护（SQLi）
- 所有数据库访问走 **SQLAlchemy ORM**，`filter_by(username=username)` 使用**绑定变量**，用户输入永远不会拼接进 SQL 语句。
- 测试用例以 `' OR '1'='1` 等载荷登录，返回 401，注入无效。

### 3.3 跨站脚本防护（XSS）
- 用户可控的 `title/content` 在入库/返回前用 **`markupsafe.escape` 做 HTML 输出编码**，`<script>` 变为 `&lt;script&gt;`，浏览器不会执行。
- 测试用例提交 `<script>alert(1)</script>`，断言返回内容中不存在可执行的 `<script>` 标签。

---

## 4. CI/CD 与安全扫描

流水线 `.github/workflows/ci.yml`（push/PR 触发）依次执行：

1. **单元测试**：`python -m unittest test_api -v`（覆盖登录、JWT、SQLi、XSS，共 7 个用例）；
2. **SAST（静态应用安全测试）**：`bandit` 扫描全部源码，输出 HTML 报告 `bandit-report` artifact；
3. **SCA（软件成分分析）**：`dependency-check/Dependency-Check_Action`（OWASP Dependency-Check）扫描 `requirements.txt` 依赖中的已知 CVE，输出 HTML 报告 `dependency-check-report` artifact。

> 截图位置（提交时附上）：
> - 图 4-1：GitHub Actions 流水线全绿
> - 图 4-2：Artifacts 中的 bandit-report（SAST）
> - 图 4-3：Artifacts 中的 dependency-check-report（SCA）
> - 图 4-4：接口测试（登录 200 / 错误密码 401 / 无 token 401 / SQLi 401 / XSS 被转义）

---

## 5. 真实 CVE 分析（CVE-2021-42013）

选用 **CVE-2021-42013：Apache HTTP Server 2.4.49/2.4.50 路径穿越并可升级为 RCE**，基于 Vulhub 用 Docker 复现。

- 受影响版本：Apache httpd **2.4.49 / 2.4.50**；修复版本：**2.4.51+**。
- 复现：用双重 URL 编码 `.%%32%65` 绕过 2.4.50 对 CVE-2021-41773 的不完整补丁，成功读到容器内 `/etc/passwd`；在开启 CGI 时经 `/cgi-bin/.../bin/sh` 执行 `id`，返回 `uid=1(daemon)`。
- 根因：`ap_normalize_path()` 对路径只做了**一层解码/规范化**，补丁采用黑名单特征匹配，多重编码可绕过（CWE-177 / CWE-22），配合 CGI 与宽松目录授权形成 RCE。
- 修复：基础镜像升级到 `httpd:2.4.51`（修复版保留与漏洞版**完全相同**的配置，仅改版本号）。
- 验证：同一载荷下，漏洞版 2.4.50 返回 200（读到 passwd / 执行命令），修复版 2.4.51 一律返回 **400** 且正常首页仍为 200。

完整复现命令、根因分析、修复文件、对比证据见：**[`cve/CVE-2021-42013/README.md`](cve/CVE-2021-42013/README.md)**（`vulnerable/`、`fixed/` 为修复文件文件夹，`evidence/` 为实测原始输出，`verify.ps1` 为一键对比脚本）。

---

## 6. 本地快速验证

```bash
# 1) 运行 API 单元测试
python -m unittest test_api -v

# 2) CVE 漏洞版与修复版（需 Docker）
cd cve/CVE-2021-42013/vulnerable && docker compose up -d --build   # 8080 漏洞版
cd ../fixed && docker compose up -d --build                        # 8081 修复版
cd .. && powershell -ExecutionPolicy Bypass -File verify.ps1       # 对比验证
```
