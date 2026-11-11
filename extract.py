from __future__ import annotations
from pathlib import Path
import gdown
import pandas as pd

URL = "https://drive.google.com/file/d/1BtFPueekTleALZJKeWwrfsnWMtw-BuPj/view?usp=share_link"


# ищем корень проекта по наличию окружения
def find_project_root() -> Path:     # поиск папки с environment.yml, как маркер корня проекта
    start = Path(__file__).resolve()
    for parent in start.parents:
        if (parent / "environment.yml").exists():
            return parent
    raise FileNotFoundError(f"Не найден environment.yml, добавьте environment.yml в корень проекта")


def default_raw_path() -> Path:
    return find_project_root() / "data" / "raw" / "dataset.csv"


# скачиваем датасет с Гугл диска или читаем его из локальной папки
def extract_df(csv_path: str | Path | None = None, url: str = URL, force: bool = False) -> pd.DataFrame:
    if csv_path is None:
        csv_path = default_raw_path() 
    csv_path = Path(csv_path)

    if force or not csv_path.exists():
        print("Загрузка датасета")
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        gdown.download(url, str(csv_path), quiet=False)
        print("Датасет загружен.")
    else:
        print("Датасет уже загружен в локальную директорию")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise RuntimeError(f"CSV пустой: {csv_path}")
    return df