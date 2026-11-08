# ДЗ 7: Скрипт записи 100 строк датасета в удалённую базу данных.

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text, URL

from read_creds import read_creds

# пути файлов
base= Path(__file__).resolve().parent.parent
creds_path= base / "creds.db"
dataset_path= base / "data" / "processed" / "dataset.parquet"

# настройки записи файлов
name= "scherbinaam"
target_db= "homeworks"
rows= 100


def make_engine(creds: dict):
    url = URL.create(
    "postgresql+psycopg2",
    username=creds["user"], password=creds["password"],
    host=creds["url"], port=creds["port"], database=creds["db_name"])
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


# Загрузка датасета
def load_dataset() -> pd.DataFrame:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Датасет не найден: {dataset_path}. "
            f"Запустите python data_loader.py")
    df= pd.read_parquet(dataset_path)
    if len(df) < rows:
        raise RuntimeError(f"В датасете только {len(df)} строк, нужно {rows}")
    return clean_columns(df.head(rows))


def write_to_db(df: pd.DataFrame, engine, schema: str = "public") -> int:
    print(f"Записываю {len(df)} строк в таблицу {schema}.{name} ...")
    inserted = df.to_sql(
        name=name,
        con=engine,
        schema=schema,
        if_exists="replace",
        index=False)
    print(f"  to_sql вернул: {inserted}")
    if inserted != len(df):
        raise RuntimeError(
            f"to_sql вставил {inserted} строк вместо {len(df)}.")
    return inserted


def verify(df: pd.DataFrame, engine, schema: str = "public") -> None:
    with engine.connect() as conn:
        count = conn.execute(
            text(f'SELECT COUNT(*) FROM {schema}."{name}"')).scalar()
        cols_db = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = :schema AND table_name = :table "
                "ORDER BY ordinal_position"),
            {"schema": schema, "table": name},).scalars().all()

    print(f"  В таблице {schema}.{name} строк: {count}")

    if count != rows:
        raise RuntimeError(f"Должно быть {rows} строк, а в БД {count}")

    cols_df = list(df.columns)
    if list(cols_db) != cols_df:
        raise RuntimeError(
            "Колонки в БД не совпадают исходным датафреймом.\n"
            f"  Ожидалось: {cols_df}\n"
            f"  В БД:      {list(cols_db)}")

    print(f"Проверка успешно пройдена: {count} строк, колонок {len(cols_df)}.")


def main() -> None:
    creds = read_creds(creds_path, target_db)
    engine = make_engine(creds)
    df = load_dataset()
    print("Колонки базы данных:", list(df.columns))
    inserted = write_to_db(df, engine)
    verify(df, engine)
    print(f"\nФункция выполнена успешно: {inserted} строк записано в {creds['db_name']}.public.{name}")


if __name__ == "__main__":
    main()