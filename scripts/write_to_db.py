# ДЗ 7: cкрипт записи 100 строк датасета в удалённую базу данных

import sqlite3
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


# пути файлов
base= Path(__file__).resolve().parent.parent
creds_path= base / "creds.db"
dataset_path= base / "data" / "processed" / "dataset.parquet"

# настройки записи файлов
name= "scherbinaam"
target_db= "homeworks"
rows= 100


# чтение кредов из таблицы файла creds.db
def read_secret_creds(path: Path, target_db: str) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Файл кредов не найден: {path}")
    conn= sqlite3.connect(path)
    conn.row_factory= sqlite3.Row
    try:
        cur= conn.cursor()
        cur.execute("SELECT url, port, user, pass, db_name "
            "FROM access WHERE db_name = ?", (target_db,))
        row= cur.fetchone()
        if not row:
            cur.execute("SELECT db_name FROM access")
            available = [r["db_name"] for r in cur.fetchall()]
            raise RuntimeError(
                f"В creds.db нет записи с db_name={target_db!r}. "
                f"Доступные db_name: {available}")
        return {
            "url": row["url"],
            "port": row["port"],
            "user": row["user"],
            "password": row["pass"],
            "db_name": row["db_name"]}
    finally:
        conn.close()


def make_engine(creds: dict):
    url = (f"postgresql+psycopg2://{creds['user']}:{creds['password']}"
        f"@{creds['url']}:{creds['port']}/{creds['db_name']}")
    return create_engine(url, pool_recycle=3600)


# Приводим имена колонок к нижнему регистру чистим их
def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    new_cols = []
    for col in df.columns:
        c = col.lower()
        c = c.replace(" ", "_")
        c = c.replace("(", "").replace(")", "")
        c = c.replace("%", "")
        c = c.replace(".", "")
        while "__" in c:
            c = c.replace("__", "_")
        c = c.strip("_")
        new_cols.append(c)
    df= df.copy()
    df.columns = new_cols
    return df


# подготавливаем датасет к загрузке 
def load_dataset() -> pd.DataFrame:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Датасет не найден: {dataset_path}. "
            f"Запустите python data_loader.py")
    df= pd.read_parquet(dataset_path)
    if len(df) < rows:
        raise RuntimeError(f"В датасете только {len(df)} строк, нужно {rows}")
    return clean_columns(df.head(rows))


def write_to_db(df: pd.DataFrame, engine, schema: str = "public") -> None:
    print(f"Пишу {len(df)} строк в таблицу {schema}.{name} ...")
    df.to_sql(name=name,
        con=engine,
        schema=schema,
        if_exists="replace",
        index=False)
    print("Готово")


# проверяем правильность загрузки нашего датасета в базу данных
def verify(engine, schema: str = "public") -> None:
    with engine.connect() as conn:
        count = conn.execute(
            text(f'select count(*) from {schema}."{name}"')).scalar()
    print(f"В таблице {schema}.{name} строк: {count}")
    if count != rows:
        raise RuntimeError(f"Должно быть {rows} строк, а в базе данных {count}")


def main() -> None:
    creds= read_secret_creds(creds_path, target_db)
    engine= make_engine(creds)
    df= load_dataset()
    print("Колонки базы данных:", list(df.columns))
    write_to_db(df, engine)
    verify(engine)


if __name__ == "__main__":
    main()
