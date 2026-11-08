# ДЗ 7: Скрипт чтения кредов

import sqlite3
from pathlib import Path


def read_creds(path: Path, target_db: str = "homeworks") -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Файл с кредами не найден: {path}. "
    f"Положите creds.db в корень проекта.")

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT url, port, user, pass, db_name "
            "FROM access WHERE db_name = ?",
            (target_db,))
        row = cur.fetchone()

        if row is None:
            cur.execute("SELECT db_name FROM access")
            available = [r["db_name"] for r in cur.fetchall()]
            raise RuntimeError(
                f"В creds.db нет записи с db_name={target_db!r}. "
                f"Доступные db_name: {available}")

        return {"url": row["url"],
            "port": row["port"],
            "user": row["user"],
            "password": row["pass"],
            "db_name": row["db_name"]}
    finally:
        conn.close()