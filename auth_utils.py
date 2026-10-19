"""认证核心：bcrypt 密码哈希 + JWT 签发/验证 + require_auth 装饰器。

安全要点：
1. 密码用 bcrypt 存储 —— 自带随机盐 + 可调工作因子，抗彩虹表和暴力破解，
   比 SHA-256（无盐、快速）更适合口令哈希。见手册控制问题 1。
2. JWT 用 HS256 签名，服务端持有 SECRET_KEY，令牌防篡改；
   payload 带 iat（签发时间）和 exp（过期时间），过期自动失效。
3. 密钥从环境变量读取；代码里只是开发环境默认值，生产必须注入。
"""

import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import jsonify, request

# 开发环境默认密钥（≥32 字节，满足 HS256 最小密钥长度要求）；
# 生产环境必须通过环境变量 JWT_SECRET 注入
SECRET_KEY = os.environ.get("JWT_SECRET", "dev-only-secret-change-me-0123456789abcdef")
ALGORITHM = "HS256"
TOKEN_TTL_HOURS = 1


def hash_password(password: str) -> str:
    """bcrypt 自动生成随机盐，哈希结果中包含盐信息。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """校验密码；bcrypt.checkpw 自带常数时间比较，抗时序攻击。"""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_token(username: str) -> str:
    """签发 JWT：sub=用户名，exp=1 小时后过期。"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(hours=TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user():
    """从 Authorization: Bearer <token> 解析并验证 JWT，返回用户名；失败返回 None。"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[len("Bearer "):]
    try:
        # 指定 algorithms 防止算法混淆攻击；PyJWT 会校验签名和 exp
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def require_auth(f):
    """受保护路由的装饰器：无有效 JWT 一律 401。"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        username = get_current_user()
        if username is None:
            return jsonify({"error": "Unauthorized: missing or invalid token"}), 401
        return f(username=username, *args, **kwargs)

    return wrapper
