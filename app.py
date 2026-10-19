"""Work 1 安全 API 主程序。

三个接口：
  1. POST /auth/login   用户登录，校验 bcrypt 密码后签发 JWT
  2. GET  /api/data     仅认证用户可访问，返回用户列表
  3. POST /api/posts    自拟接口：认证用户发布文章（带 XSS 转义演示）

运行：python app.py （默认 http://127.0.0.1:5000）
"""

import os

from flask import Flask, jsonify, request

from auth_utils import create_token, hash_password, require_auth, verify_password
from models import Post, User, db
from security import sanitize_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def seed_user():
    """启动时建表，并预置一个演示账号（密码从环境变量读，便于 CI 覆盖）。"""
    db.create_all()
    if User.query.filter_by(username="admin").first() is None:
        seed_password = os.environ.get("SEED_PASSWORD", "Admin123!")
        db.session.add(
            User(username="admin", password_hash=hash_password(seed_password))
        )
        db.session.commit()


with app.app_context():
    seed_user()


@app.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    # SQLi 防护：ORM 参数化查询（filter_by 使用绑定变量），无字符串拼接
    user = User.query.filter_by(username=username).first()

    # 无论用户不存在还是密码错误，都返回同样的 401，避免账号枚举
    if user is None or not verify_password(password, user.password_hash):
        return jsonify({"error": "invalid credentials"}), 401

    return jsonify({"token": create_token(user.username)})


@app.get("/api/data")
@require_auth
def api_data(username):
    # 仅认证用户可访问（require_auth 装饰器验证 JWT）
    users = User.query.all()
    return jsonify({"users": [u.to_dict() for u in users]})


@app.post("/api/posts")
@require_auth
def create_post(username):
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")
    content = data.get("content", "")

    if not title or not content:
        return jsonify({"error": "title and content are required"}), 400

    # XSS 防护：入库前对用户可控内容做 HTML 转义（输出编码）
    post = Post(
        title=sanitize_text(title),
        content=sanitize_text(content),
        author=username,
    )
    db.session.add(post)
    db.session.commit()

    return (
        jsonify(
            {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "author": post.author,
            }
        ),
        201,
    )


if __name__ == "__main__":
    # 本地开发用 127.0.0.1；生产环境应交给 gunicorn 等 WSGI 服务器
    app.run(host="127.0.0.1", port=5000, debug=False)
