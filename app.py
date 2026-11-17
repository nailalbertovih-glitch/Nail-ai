import os, json, sqlite3, secrets
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from openai import OpenAI

load_dotenv()
DB = Path(os.getenv("DB_PATH", "nail_ai.sqlite3"))
app = FastAPI(title="NAIL AI backend", version="0.1.0")


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_connection_id TEXT NOT NULL,
        chat_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL,
        sender_id INTEGER,
        incoming_text TEXT NOT NULL,
        draft_text TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL
    )""")
    con.commit()
    return con


def require_admin(value):
    expected = os.getenv("ADMIN_TOKEN", "")
    if not expected or not secrets.compare_digest(value or "", expected):
        raise HTTPException(401, "Unauthorized")


@app.get("/health")
def health():
    return {"ok": True, "service": "nail-ai", "mode": "draft-only"}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if not secret or not secrets.compare_digest(x_telegram_bot_api_secret_token or "", secret):
        raise HTTPException(403, "Bad webhook secret")
    update = await request.json()
    msg = update.get("business_message")
    if not msg or not msg.get("text"):
        return {"ok": True, "ignored": True}
    connection_id = msg.get("business_connection_id")
    chat_id = msg.get("chat", {}).get("id")
    message_id = msg.get("message_id")
    sender_id = msg.get("from", {}).get("id")
    incoming = msg["text"]
    if not connection_id or not chat_id or not message_id:
        return {"ok": True, "ignored": True}

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system = (
        "Ты помощник владельца Telegram-аккаунта. Создавай короткий черновик ответа на русском. "
        "Не выдумывай факты о владельце, не обещай встречи, деньги или действия. "
        "Если сообщение касается денег, обязательств, личных данных, конфликтов или важных решений, "
        "предложи нейтральный ответ: 'Я уточню и отвечу сам'. Верни только текст черновика."
    )
    completion = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        messages=[{"role": "system", "content": system}, {"role": "user", "content": incoming}],
        temperature=0.7,
    )
    draft = completion.choices[0].message.content or "Я увидел сообщение, отвечу чуть позже."
    con = db()
    con.execute("INSERT INTO drafts (business_connection_id,chat_id,message_id,sender_id,incoming_text,draft_text,created_at) VALUES (?,?,?,?,?,?,?)",
                (connection_id, chat_id, message_id, sender_id, incoming, draft, datetime.now(timezone.utc).isoformat()))
    con.commit(); con.close()
    return {"ok": True, "draft_created": True}


@app.get("/drafts")
def list_drafts(authorization: str | None = Header(default=None)):
    require_admin((authorization or "").removeprefix("Bearer "))
    con = db(); rows = con.execute("SELECT * FROM drafts WHERE status='pending' ORDER BY id DESC LIMIT 100").fetchall(); con.close()
    return [dict(r) for r in rows]


@app.post("/drafts/{draft_id}/approve")
async def approve_draft(draft_id: int, authorization: str | None = Header(default=None)):
    require_admin((authorization or "").removeprefix("Bearer "))
    con = db(); row = con.execute("SELECT * FROM drafts WHERE id=? AND status='pending'", (draft_id,)).fetchone()
    if not row:
        con.close(); raise HTTPException(404, "Draft not found")
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        con.close(); raise HTTPException(503, "Telegram bot is not configured")
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
            "business_connection_id": row["business_connection_id"],
            "chat_id": row["chat_id"],
            "text": row["draft_text"],
            "reply_parameters": {"message_id": row["message_id"]}
        })
    if response.status_code != 200 or not response.json().get("ok"):
        con.close(); raise HTTPException(502, "Telegram send failed")
    con.execute("UPDATE drafts SET status='sent' WHERE id=?", (draft_id,)); con.commit(); con.close()
    return {"ok": True, "sent": True}


@app.post("/drafts/{draft_id}/reject")
def reject_draft(draft_id: int, authorization: str | None = Header(default=None)):
    require_admin((authorization or "").removeprefix("Bearer "))
    con = db(); cur = con.execute("UPDATE drafts SET status='rejected' WHERE id=? AND status='pending'", (draft_id,)); con.commit(); con.close()
    if not cur.rowcount: raise HTTPException(404, "Draft not found")
    return {"ok": True, "rejected": True}
