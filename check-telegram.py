#!/usr/bin/env python3
"""Проверка настроек Telegram: getUpdates и тестовое сообщение."""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / "telegram.env"


def load_config():
    if not ENV_FILE.is_file():
        print("Файл telegram.env не найден.")
        print(f"Создайте: cp telegram.env.example telegram.env")
        print("И заполните BOT_TOKEN и CHAT_ID.")
        return None, None
    token = ""
    chat_id = ""
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip().upper(), value.strip().strip('"').strip("'")
        if key == "BOT_TOKEN":
            token = value
        elif key == "CHAT_ID":
            chat_id = value
    return token, chat_id


def api_get(token: str, method: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    with urllib.request.urlopen(url, timeout=15.0) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    token, chat_id = load_config()
    if not token:
        return 1

    print("1) Проверка бота (getMe)...")
    try:
        me = api_get(token, "getMe")
        if me.get("ok"):
            print(f"   OK: бот @{me['result'].get('username', '?')}")
        else:
            print("   Ошибка:", me)
            return 1
    except Exception as err:
        print("   Не удалось связаться с Telegram:", err)
        return 1

    print("\n2) Последние сообщения боту (getUpdates)...")
    print("   Сначала в Telegram: откройте бота → кнопка «Запустить» или /start → напишите «Привет»")
    try:
        updates = api_get(token, "getUpdates")
        results = updates.get("result") or []
        if not results:
            print("   Пусто. Напишите боту /start и снова запустите этот скрипт.")
            print("   Или узнайте id через @userinfobot — проще.")
        else:
            seen = set()
            for item in results:
                msg = item.get("message") or item.get("edited_message") or {}
                chat = msg.get("chat") or {}
                cid = chat.get("id")
                if cid and cid not in seen:
                    seen.add(cid)
                    name = chat.get("first_name") or chat.get("title") or "?"
                    print(f"   CHAT_ID: {cid}  ({name})")
    except Exception as err:
        print("   Ошибка getUpdates:", err)

    if chat_id:
        print("\n3) Тестовая отправка в Telegram...")
        try:
            body = json.dumps(
                {
                    "chat_id": chat_id,
                    "text": "Тест kisura: если видите это — заявки с сайта будут приходить сюда.",
                },
                ensure_ascii=False,
            ).encode("utf-8")
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15.0) as response:
                out = json.loads(response.read().decode("utf-8"))
            if out.get("ok"):
                print("   OK: сообщение отправлено. Проверьте Telegram.")
            else:
                print("   Ошибка:", out.get("description"))
        except Exception as err:
            print("   Не отправилось:", err)
            print("   Проверьте CHAT_ID в telegram.env")
    else:
        print("\n3) CHAT_ID в telegram.env не указан — добавьте после шага 2.")

    print("\nЗапускайте сайт: python3 server.py 8080  (не python3 -m http.server)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
