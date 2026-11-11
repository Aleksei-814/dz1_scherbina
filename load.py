from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any
import pandas as pd
from sqlalchemy import URL, create_engine, text
from .extract import find_project_root
from .transform import default_parquet_path


name = "scherbinaam"
target_db = "homeworks"
rows = 100


# читает креды доступа с локального файла
def read_creds(path: str | Path | None = None, target_db: str = target_db) -> dict[str, Any]:
    if path is None:
        path = find_project_root() / "creds.db"
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Файл с кредами не найден: {path}, добавьте creds.db в корень проекта")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT url, port, user, pass, db_name "
            "FROM access WHERE db_name = ?",
            (target_db,))
        row = cur.fetchone()
        if row is None:
            cur.execute("SELECT db_name FROM access")
            available = [r["db_name"] for r in cur.fetchall()]
            raise RuntimeError(f"В creds.db нет записи с db_name={target_db!r}, доступные: {available}")
        return {"url": row["url"],
                "port": row["port"],
                "user": row["user"],
                "password": row["pass"],
                "db_name": row["db_name"]}
    finally:
        conn.close()


def make_engine(creds: dict[str, Any]):
    url = URL.create("postgresql+psycopg2",
        username=creds["user"],
        password=creds["password"],
        host=creds["url"],
        port=creds["port"],
        database=creds["db_name"])
    return create_engine(url, pool_recycle=3600)


# Приводим имена колонок к нижнему регистру чистим их
def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    new_cols= []
    for col in df.columns:
        c = str(col).lower()
        c = c.replace(" ", "_")
        c = c.replace("(", "").replace(")", "")
        c = c.replace("%", "")
        c = c.replace(".", "")
        while "__" in c:
            c = c.replace("__", "_")
        c = c.strip("_")
        new_cols.append(c)
    df = df.copy()
    df.columns = new_cols
    return df


# Загрузка датасета
def load_dataset(parquet_path: str | Path | None = None, rows: int = rows) -> pd.DataFrame:
    if parquet_path is None:
        parquet_path = default_parquet_path()
    parquet_path = Path(parquet_path)
    if not parquet_path.exists():
        raise FileNotFoundError(f"Датасет не найден: {parquet_path}. "
                                f"Сначала выполните python -m etl.main transform")
    df= pd.read_parquet(parquet_path)
    if len(df) < rows:
        raise RuntimeError(f"В датасете только {len(df)} строк, а нужно {rows}")
    return clean_columns(df.head(rows))


def write_to_db(df: pd.DataFrame, engine, schema: str = "public",
    table: str = name, if_exists: str = "replace") -> int:
    print(f"Запись {len(df)} строк в таблицу {schema}.{table} ...")
    inserted = df.to_sql(
        name=table,
        con=engine,
        schema=schema,
        if_exists=if_exists,
        index=False)
    print(f"  to_sql вернул: {inserted}")
    if inserted != len(df):
        raise RuntimeError(f"to_sql вставил {inserted} строк вместо {len(df)}")
    return int(inserted)


# проверка после загрузки
def verify(df: pd.DataFrame, engine, schema: str = "public",
    table: str = name, rows: int = rows) -> None:
    with engine.connect() as conn:
        count = conn.execute(
            text(f'SELECT COUNT(*) FROM {schema}."{table}"')).scalar()
        cols_db = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = :schema AND table_name = :table "
                "ORDER BY ordinal_position"),
            {"schema": schema, "table": table}).scalars().all()
    print(f"  В таблице {schema}.{table} строк: {count}")
    if count != rows:
        raise RuntimeError(f"Должно быть {rows} строк, а в БД {count}")
    cols_df = list(df.columns)
    if list(cols_db) != cols_df:
        raise RuntimeError("Колонки в БД не совпадают исходным датафреймом.\n"
            f"  Ожидалось: {cols_df}, а в БД: {list(cols_db)}")
    print(f"Проверка успешно пройдена: {count} строк, колонок {len(cols_df)}.")