from __future__ import annotations
import warnings
from pathlib import Path
import pandas as pd
from .extract import find_project_root

warnings.filterwarnings("ignore", category=FutureWarning)

miss= ["?", "", "NA", "N/A", "nan", "None", "-"]
string_col= ["Source"]
category_col= ["Steel type"]
int_col= ["Tempering time (s)"]
float_col= [
    "Initial hardness (HRC) - post quenching",
    "Tempering temperature (ºC)",
    "C (%wt)",
    "Mn (%wt)",
    "P (%wt)",
    "S (%wt)",
    "Si (%wt)",
    "Ni (%wt)",
    "Cr (%wt)",
    "Mo (%wt)",
    "V (%wt)",
    "Al (%wt)",
    "Cu (%wt)",
    "Final hardness (HRC) - post tempering"]


# приводим типы колонок к более аккуратным и правильным
# строки к string, категории к category, целые к Int64, дробные к float64
def convert_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in string_col: df[col] = df[col].astype("string")
    for col in category_col: df[col] = df[col].astype("category")
    for col in int_col:
        df[col] = df[col].replace(miss, pd.NA)
        df[col] = pd.to_numeric(df[col]).astype("Int64")
    for col in float_col:
        df[col] = df[col].replace(miss, pd.NA)
        df[col] = pd.to_numeric(df[col]).astype("float64")
    return df


def default_parquet_path() -> Path:
    return find_project_root() / "data" / "processed" / "dataset.parquet"


# сохраняем датафрейм в формате parquet
def parquet_saving(df: pd.DataFrame, path: str | Path | None = None) -> Path:
    if path is None: path = default_parquet_path()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    print(f"Parquet сохранён: {path}")
    return path
