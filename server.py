#!/usr/bin/env python3
"""Статический сайт + отправка заявок в Telegram."""
import json
import os
import sys
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / "telegram.env"


def load_telegram_config() -> dict:
    config = {
        "bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", "").strip(),
        "chat_id": os.environ.get("TELEGRAM_CHAT_ID", "").strip(),
    }
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip().upper()
            value = value.strip().strip('"').strip("'")
            if key == "BOT_TOKEN":
                config["bot_token"] = value
            elif key == "CHAT_ID":
                config["chat_id"] = value
    return config


def escape_telegram_html(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_order_message(data: dict) -> str:
    lines = [
        "<b>Новая заявка — kisura</b>",
        "",
        f"<b>Торт:</b> {escape_telegram_html(data.get('cakeName', '—'))}",
        f"<b>Стиль:</b> {escape_telegram_html(data.get('designName', '—'))}",
        f"<b>Вес:</b> {escape_telegram_html(data.get('weightLabel', '—'))}",
        f"<b>Цена:</b> {escape_telegram_html(data.get('priceLabel', '—'))}",
        "",
        f"<b>Имя:</b> {escape_telegram_html(data.get('name', '—'))}",
        f"<b>Телефон:</b> {escape_telegram_html(data.get('phone', '—'))}",
        f"<b>Email:</b> {escape_telegram_html(data.get('email') or '—')}",
        f"<b>Дата:</b> {escape_telegram_html(data.get('eventDate', '—'))}",
    ]
    comment = (data.get("comment") or "").strip()
    if comment:
        lines.append(f"<b>Комментарий:</b> {escape_telegram_html(comment)}")
    return "\n".join(lines)


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    body = json.dumps(
        {"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15.0) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("ok"):
        raise RuntimeError(payload.get("description") or "Telegram API error")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            config = load_telegram_config()
            self.send_json(
                200,
                {
                    "ok": True,
                    "message": "Сервер работает. Заявки отправляются POST с формы на /api/order.",
                    "telegramConfigured": bool(config["bot_token"] and config["chat_id"]),
                },
            )
            return
        if path == "/api/order":
            self.send_json(
                405,
                {
                    "ok": False,
                    "error": "Этот адрес не открывается в браузере напрямую. "
                    "Заполните форму на странице order.html — отправка идёт автоматически (POST).",
                    "check": "Откройте /api/health чтобы проверить сервер.",
                },
            )
            return
        super().do_GET()

    def do_OPTIONS(self) -> None:
        if urlparse(self.path).path.startswith("/api/"):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            return
        super().do_OPTIONS()

    def do_POST(self) -> None:
        if urlparse(self.path).path == "/api/order":
            self.handle_order()
            return
        self.send_error(404)

    def handle_order(self) -> None:
        config = load_telegram_config()
        if not config["bot_token"] or not config["chat_id"]:
            self.send_json(
                503,
                {
                    "ok": False,
                    "error": "Telegram не настроен. Создайте файл telegram.env (см. telegram.env.example).",
                },
            )
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"ok": False, "error": "Некорректные данные формы"})
            return

        name = (data.get("name") or "").strip()
        phone = (data.get("phone") or "").strip()
        event_date = (data.get("eventDate") or "").strip()
        if not name or not phone or not event_date:
            self.send_json(400, {"ok": False, "error": "Заполните обязательные поля"})
            return

        try:
            send_telegram_message(
                config["bot_token"],
                config["chat_id"],
                build_order_message(data),
            )
        except (urllib.error.URLError, TimeoutError, OSError, RuntimeError) as err:
            self.send_json(502, {"ok": False, "error": f"Не удалось отправить в Telegram: {err}"})
            return

        self.send_json(200, {"ok": True})

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        if self.path.startswith("/api/"):
            sys.stderr.write(f"[api] {args[0]} {args[1]}\n")
            return
        super().log_message(format, *args)


def main() -> int:
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    config = load_telegram_config()
    tg_status = "настроен" if config["bot_token"] and config["chat_id"] else "НЕ настроен (telegram.env)"
    print(f"Serving {ROOT} at http://127.0.0.1:{port}")
    print(f"Telegram: {tg_status}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
