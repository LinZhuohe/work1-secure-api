"""API 功能与安全措施的单元测试（unittest，无需额外依赖）。

覆盖：登录成功/失败、SQLi 注入被挡、无 token 拒绝、带 token 访问、
XSS 载荷被转义。CI 与本地均执行：python -m unittest test_api -v
"""

import unittest

import app as app_module


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app_module.app.test_client()

    def login(self, username="admin", password="Admin123!"):  # nosec B107 - 测试用固定账号
        return self.client.post(
            "/auth/login", json={"username": username, "password": password}
        )

    # ---- 认证 ----
    def test_login_ok(self):
        r = self.login()
        self.assertEqual(r.status_code, 200)
        self.assertIn("token", r.get_json())

    def test_login_wrong_password(self):
        r = self.login(password="wrong-password")  # nosec B106 - 测试用示例密码
        self.assertEqual(r.status_code, 401)

    # ---- SQLi 防护 ----
    def test_login_sqli_blocked(self):
        r = self.client.post(
            "/auth/login",
            json={"username": "admin' OR '1'='1", "password": "x"},  # nosec B105 - 注入测试载荷
        )
        self.assertEqual(r.status_code, 401)

    # ---- 访问控制（Broken Authentication）----
    def test_data_requires_token(self):
        r = self.client.get("/api/data")
        self.assertEqual(r.status_code, 401)

    def test_data_with_token(self):
        token = self.login().get_json()["token"]
        r = self.client.get("/api/data", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("users", r.get_json())

    def test_tampered_token_rejected(self):
        token = self.login().get_json()["token"]
        bad = token[:-1] + ("x" if token[-1] != "x" else "y")
        r = self.client.get("/api/data", headers={"Authorization": f"Bearer {bad}"})
        self.assertEqual(r.status_code, 401)

    # ---- XSS 防护 ----
    def test_xss_payload_escaped(self):
        token = self.login().get_json()["token"]
        r = self.client.post(
            "/api/posts",
            json={"title": "t", "content": "<script>alert(1)</script>"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(r.status_code, 201)
        self.assertNotIn("<script>", r.get_json()["content"])
        self.assertIn("&lt;script&gt;", r.get_json()["content"])


if __name__ == "__main__":
    unittest.main()
