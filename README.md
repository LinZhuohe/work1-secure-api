# Work 1: Secure REST API + CI/CD + Real CVE Analysis

课程：Information Security (HDU)
实验：Work 1 — Secure REST API Development with CI/CD and Real CVE Vulnerability Analysis
技术栈：Python / Flask + SQLAlchemy + bcrypt + PyJWT

---

## 1. 项目结构

（待补充：目录说明）

## 2. API 说明

（待补充：端点、请求/响应示例、调用方式）

| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| POST | /auth/login | 无 | 登录，返回 JWT |
| GET | /api/data | JWT | 获取数据（仅认证用户） |
| POST | /api/posts | JWT | 创建文章（自拟接口） |

## 3. 安全措施

（待补充：SQLi / XSS / 认证 具体实现方式）

## 4. CI/CD 与安全扫描

（待补充：SAST/SCA 报告截图）

## 5. CVE 分析

（待补充：CVE ID、漏洞描述、复现步骤、根因分析、修复方案、修复验证）
