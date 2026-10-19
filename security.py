"""XSS 防护：输出编码（Output Encoding）。

原理：把用户可控的文本在返回给客户端之前做 HTML 转义，
把 <script> 之类的标签变成无害的 &lt;script&gt;，浏览器端就不会把它当代码执行。
这是 OWASP XSS Prevention Cheat Sheet 的核心手段之一。
"""

from markupsafe import escape


def sanitize_text(value) -> str:
    """对用户输入做 HTML 转义，返回纯文本（str），而非 Markup 对象。"""
    return str(escape(value or ""))
