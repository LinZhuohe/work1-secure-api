"""数据模型：User（用户）、Post（文章）。

所有数据库访问都通过 SQLAlchemy ORM 完成 —— 这是防 SQLi 的第一道防线：
ORM 会把参数作为绑定变量传给数据库驱动，永远不会把用户输入拼进 SQL 字符串。
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # 只存 bcrypt 哈希，绝不存明文密码
    password_hash = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        # 对外序列化时只暴露 id 和 username，绝不带出 password_hash
        return {"id": self.id, "username": self.username}


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(80), nullable=False)
