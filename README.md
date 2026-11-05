## Описание проделанной работы
В ходе выполнения задания был создан скрипт data_loader.py, загружающий датасет с [Google Drive](https://drive.google.com/file/d/1BtFPueekTleALZJKeWwrfsnWMtw-BuPj/view?usp=share_link) и выводящий первые 10 строк из таблицы в консоль, заранее приведенных к правильному типу данных.
В ходе выполнения 7 дз был создан скрипт write_to_db.py, который записывает 100 строк датасета в удалённую базу данных в виде таблицы с названием scherbinaam.

## Окружение
Управление окружением и зависимостями было осуществлено при помощи conda.

Установка окружения:
```bash
conda env create -f environment.yml
```

Активация окружения:
```bash
conda activate dz_environment
```

Запуск скрипта загрузки:
```bash
python data_loader.py
```

Запуск скрипта записи базы данных:
```bash
python write_to_db.py
```

Установка Chromium для Plotly (выполните один раз):
```bash
plotly_get_chrome -y
```
