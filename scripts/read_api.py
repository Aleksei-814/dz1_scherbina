import os
import requests
import pandas as pd


API= 'https://earthquake.usgs.gov/fdsnws/event/1/query'


def get_base_dir():
    if '__file__' in globals():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getcwd()


base_dir= get_base_dir()
data_dir= os.path.join(base_dir, 'data')
csv_path = os.path.join(data_dir, 'earthquakes.csv')


def fetch_earthquakes(limit=150, min_mag=3):   #запрос последних 150 магнитуд, что были более заднной минимальной
    params = {'format': 'geojson','limit': limit, 'minmagnitude': min_mag, 'orderby': 'time'}
    print(f'Запрос к {API} ...')
    response = requests.get(API, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()
    features = data.get('features')
    if not isinstance(features, list):
        raise RuntimeError(f'Неожиданный формат ответа: {str(data)[:300]}')
    return features


def build_dataframe(features):       #преобразование JSON в обычный датафрейм .csv
    rows = []
    for f in features:
        props = f.get('properties') or {}
        coords = (f.get('geometry') or {}).get('coordinates') or [None, None, None]
        time_utc = pd.to_datetime(props.get('time'), unit='ms', errors='coerce')   # время в данном JSON - в миллисекундах
        rows.append({'magnitude': props.get('mag'),'place': props.get('place'),'time_utc': time_utc,
            'longitude': coords[0],'latitude': coords[1], 'depth_km': coords[2], 'tsunami': props.get('tsunami'),      
            'significance': props.get('sig'),'url': props.get('url')})
    df = pd.DataFrame(rows)
    df = df.sort_values('time_utc', ascending=False).reset_index(drop=True)       #сортировка по времени землетрясения
    return df


def save_csv(df):                    #сохраняем полученный датафрейм в .csv формате
    os.makedirs(data_dir, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f'\nCSV сохранён: {csv_path}')


if __name__ == '__main__':
    features = fetch_earthquakes(limit=150, min_mag=3)
    df = build_dataframe(features)

    print(f'\nПолучено записей: {len(df)}')

    # настройка вывода, чтобы длинные тексты не ломали таблицу
    pd.set_option('display.max_colwidth', 50)
    pd.set_option('display.width', 200)
    print('\nПервые 15 строк датасета:')
    print(df.head(20).to_string())

    save_csv(df)
