### Проект по созданию etl-пайплайна

Данный проект позволяет выполнить полный цикл подготовки данных на примере базы данных о закалке и отпуске различных марок сталей. Данные расположены в датасете по ссылке: [Google Drive](https://drive.google.com/file/d/1BtFPueekTleALZJKeWwrfsnWMtw-BuPj/view?usp=share_link)
Логика выполнения собрана в пакет `etl`.
В репозитории также лежат материалы предыдущих заданий, расположенные в папках `api_example`, `notebooks` и `homeworks`.

## Структура проекта на GitHub: 
```
dz1_scherbina/                          
│
├── src/
│   ├── api_example/                    # Пример работы с API и сохранения данных
│   │   ├── read_api.py                 # Скрипт для обращения к API 
│   │   ├── screenshot.png              # Результат запуска скрипта
│   │   └── README.md                   # Описание логики работы с API и шагов получения данных
│   │
│   ├── notebooks/                      # Папка с Jupyter ноутбуком для анализа и визуализации данных
│   │   └── EDA.ipynb                   # Ноутбук для разведочного анализа данных (EDA)
│   │   
│   ├── etl/                            # Пакет ETL
│   │   ├── __init__.py                 # Делает папку пакетом Python
│   │   ├── extract.py                  # Загрузка CSV и сохранение raw данных
│   │   ├── transform.py                # Трансформации: приведение типов, новые колонки
│   │   ├── load.py                     # Сохранение в PostgreSQL и parquet
│   │   ├── validate.py                 # Опциональная валидация данных
│   │   └── main.py                     # Сборка всех шагов ETL + CLI интерфейс
│   │ 
│   └── homeworks/                      # Папка с файлами из домашних заданий
│       ├── data_loader.py
│       ├── read_creds.py
│       └── write_to_db.py
│
├── README.md                           # Описание логики работы с проектом и шагов получения данных
├── environment.yml                     # Создание окружения проекта
├── pyproject.toml                      # Установка пакета etl
└──.gitignore                           # То, что не должно попасть в репозиторий
```

⚙️ Файл `__init__.py` делает папку `etl` пакетом Python. Необходим для работы импортов `.extract`, `.transform`, `.load`, `.validate`, `.main`.

⚙️ Папка `data/` добавлена в `.gitignore`, чтобы не заливать большие и изменяемые файлы в репозиторий.

⚙️ Файл `creds.db` хранится только локально и не загружается в репозиторий, так как содержит конфиденциальные данные.

⚙️ Сырой датасет **dataset.csv** и подготовленный **dataset.parquet** находятся локально и не коммитятся. Оба файла скачиваются/создаются автоматически при запуске `python -m etl.main run` или `python -m etl.main transform`.


### `environment.yml` - conda-окружение

Содержит все библиотеки, нужные для запуска etl: `python=3.11`, `pandas`,
`pyarrow`, `sqlalchemy`, а через блок `pip:` `gdown` и `psycopg2-binary`.

Активация окружения:
```bash
conda env create -f environment.yml
conda activate dz_environment
```

### `pyproject.toml` — установка пакета `etl`

Содержит:
- **runtime-зависимости**: `pandas`, `pyarrow`, `SQLAlchemy`, `psycopg2-binary`, `gdown`.
- **dev-блок**:`jupyter`, `plotly`, `kaleido`, `requests`, `pytest`.

Активация:
```bash
pip install -e .               
pip install -e ".[dev]"         # нужно для Jupyter, Plotly, Kaleido, pytest
```

### Запуск пайплайна

Команда для активации цикла с последующей записью 100 строк обработанного датасета в удаленную базу данных:
```bash
python -m etl.main run --rows 100
```
Отдельные стадии цикла:
```bash
python -m etl.main extract              # только скачивайте датасета
python -m etl.main transform            # преобразование в parquet
python -m etl.main validate             # валидация данных
python -m etl.main load --rows 100      # запись данных из parquet в БД
```

P.S. Установка Chromium для Plotly для запуска EDA(выполните один раз):
```bash
plotly_get_chrome -y
```
