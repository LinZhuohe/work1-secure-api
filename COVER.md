# Work 1 实验报告封面（Cover Page）

> 下面的待填信息请你手动补全；正文内容见 `README.md`（API 与安全、CI/CD）与 `cve/CVE-2021-42013/README.md`（CVE 部分）。

---

<div align="center">

# 杭州电子科技大学 信息安全实验报告

<br><br>

| 项目 | 内容 |
| --- | --- |
| 课程（Course） | Information Security（信息安全） |
| 实验编号（Work No.） | Work 1 |
| 实验标题（Title） | Secure REST API Development with CI/CD and Real CVE Vulnerability Analysis |
| Variant（变体号） | 待填（请向老师确认后补全） |
| 姓名（Name） | 林卓赫 |
| 学号（Student ID） | 23320224 |
| 技术栈 | Python / Flask + SQLAlchemy + bcrypt + PyJWT |
| 代码仓库 | https://github.com/LinZhuohe/work1-secure-api |
| 成功 Pipeline | https://github.com/LinZhuohe/work1-secure-api/actions |
| CVE 编号 | CVE-2021-42013（Apache HTTP Server 2.4.49/2.4.50） |

</div>

---

## 提交清单（Submission Checklist）

- [ ] 公开仓库可访问：https://github.com/LinZhuohe/work1-secure-api
- [ ] 最后一次 GitHub Actions 流水线为绿色（含 SAST bandit + SCA OWASP Dependency-Check）
- [ ] 报告中含：
  - 图 1：Actions 流水线全绿
  - 图 2：bandit-report（SAST，HTML artifact）
  - 图 3：dependency-check-report（SCA，HTML artifact）
  - 图 4：登录 200 / 错误密码 401 / 无 token 401 / SQLi 401 / XSS 被转义
  - 图 5：CVE 漏洞版读到 `/etc/passwd`（8080）
  - 图 6：CVE 漏洞版 RCE 返回 `uid=1(daemon)`（8080）
  - 图 7：CVE 修复版攻击载荷返回 400（8081）
- [ ] 修复文件文件夹：`cve/CVE-2021-42013/fixed/`（vulnerable/fixed 对比）
- [ ] 封面信息：姓名、学号、Variant 已补全

> 图 4 可用一键脚本 `demo-api.ps1` 生成；图 5–7 可用 `cve/CVE-2021-42013/verify.ps1` 生成。
