# app/core/email.py

"""
邮件发送模块 — 基于 smtplib

用法:
    from app.core.email import send_welcome_email, send_password_reset_email
    await send_welcome_email(to="user@example.com", username="张三")
"""

from __future__ import annotations

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from app.core.config import settings
from app.core.logging import logger


TEMPLATES_DIR = Path(__file__).parent / "templates"


# ---------------------------------------------------------------------------
# 核心发送函数
# ---------------------------------------------------------------------------


def _send_email_sync(
    to: str,
    subject: str,
    html_body: str,
) -> None:
    """同步发送邮件（在线程池中调用）"""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if settings.SMTP_TLS:
            with smtplib.SMTP(
                settings.SMTP_HOST, settings.SMTP_PORT, timeout=30
            ) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAILS_FROM_EMAIL, [to], msg.as_string())
        else:
            with smtplib.SMTP(
                settings.SMTP_HOST, settings.SMTP_PORT, timeout=30
            ) as server:
                server.ehlo()
                if settings.SMTP_USER:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAILS_FROM_EMAIL, [to], msg.as_string())
        logger.info("邮件发送成功 | to={} | subject={}", to, subject)
    except Exception as e:
        logger.error(
            "邮件发送失败 | to={} | subject={} | error={}", to, subject, str(e)
        )
        raise


async def send_email(
    to: str,
    subject: str,
    html_body: str,
) -> None:
    """异步发送邮件"""
    if not settings.smtp_enabled:
        logger.warning("SMTP 未配置，跳过邮件发送 | to={} | subject={}", to, subject)
        return
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_email_sync, to, subject, html_body)


# ---------------------------------------------------------------------------
# 模板渲染辅助
# ---------------------------------------------------------------------------


def _render_template(template_name: str, **kwargs: str) -> str:
    """读取 HTML 模板并替换占位符"""
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        logger.error("邮件模板不存在: {}", template_path)
        raise FileNotFoundError(f"邮件模板不存在: {template_path}")

    html = template_path.read_text(encoding="utf-8")
    for key, value in kwargs.items():
        html = html.replace(f"{{{{{key}}}}}", value)
    return html


# ---------------------------------------------------------------------------
# 业务邮件
# ---------------------------------------------------------------------------


async def send_welcome_email(to: str, username: str) -> None:
    """发送注册欢迎邮件"""
    html = _render_template(
        "welcome.html",
        username=username,
        project_name=settings.PROJECT_NAME,
    )
    await send_email(
        to=to,
        subject=f"欢迎加入 {settings.PROJECT_NAME}",
        html_body=html,
    )


async def send_password_reset_email(to: str, username: str, token: str) -> None:
    """发送密码重置邮件"""
    html = _render_template(
        "reset_password.html",
        username=username,
        token=token,
        project_name=settings.PROJECT_NAME,
    )
    await send_email(
        to=to,
        subject=f"密码重置 — {settings.PROJECT_NAME}",
        html_body=html,
    )
