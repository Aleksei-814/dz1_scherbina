## Описание проделанной работы по сбор датасета через публичный API

## Откуда информация и о чем она

**Источник:** [USGS Earthquake Catalog API](https://earthquake.usgs.gov/fdsnws/event/1/) — публичный API Геологической службы США.

**Эндпоинт:** `https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=150&minmagnitude=3&orderby=time`

**Что получаем:** 150 последних землетрясений с магнитудой ≥ 3 по всему миру — магнитуда, место, время (UTC), координаты (широта, долгота), глубина, признак цунами, значимость события, ссылка на страницу на сайте USGS.


## Окружение
Управление окружением и зависимостями было осуществлено при помощи conda.

Установка окружения:
```bash
conda env create -f environment.yml
```

Активация окружения:
```bash
conda activate dz_enviroment
```

Запуск скрипта:
```bash
python read_api.py
```