# щербина алексей 3 дз
import pandas as pd
import gdown
import os

URL= 'https://drive.google.com/file/d/1BtFPueekTleALZJKeWwrfsnWMtw-BuPj/view?usp=share_link'

base = os.path.dirname(os.path.abspath(__file__))
dspath = os.path.join(base, 'data', 'raw', 'dataset.csv')
parquetpath = os.path.join(base, 'data', 'processed', 'dataset.parquet')


def downloadDF():                      # скачиваем таблицу с гугл диска
    if not os.path.exists(dspath):
        print('Загрузка датасета ...')
        os.makedirs(os.path.dirname(dspath), exist_ok=True)
        gdown.download(URL, dspath, quiet=False)
        print('Датасет загружен, ниже представлены первые 10 строк:')
    else:
        print('Датасет уже загружен в локальную директорию, ниже представлены первые 10 строк:')
    data = pd.read_csv(dspath)
    print(data.head(10))
    return data
def convertDF(df):         #приводим типы колонок к правильным
    df = df.copy()
    missing= ['?', '', 'NA', 'N/A', 'nan', 'None', '-']
    str_cols = ['Source']          #строки
    for col in str_cols:
        df[col] = df[col].astype('string')
    cat_cols = ['Steel type']      #категории
    for col in cat_cols:
        df[col] = df[col].astype('category')
    int_cols = ['Tempering time (s)']          #целые числа
    for col in int_cols:
        df[col] = df[col].replace(missing, pd.NA)
        df[col] = pd.to_numeric(df[col]).astype('Int64')
    float_cols = ['Initial hardness (HRC) - post quenching','Tempering temperature (ºC)','C (%wt)','Mn (%wt)','P (%wt)','S (%wt)','Si (%wt)','Ni (%wt)','Cr (%wt)','Mo (%wt)','V (%wt)','Al (%wt)','Cu (%wt)','Final hardness (HRC) - post tempering',]
    for col in float_cols:                           #столбцы в которых данные с плавающей точкой
        df[col] = df[col].replace(missing, pd.NA)
        df[col] = pd.to_numeric(df[col]).astype('float64')
    return df

def parquet_saving(df):                     #сохраним DataFrame в формате parquet
    os.makedirs(os.path.dirname(parquetpath), exist_ok=True)
    df.to_parquet(parquetpath, index=False)
    print(f'Parquet сохранён: {parquetpath}')

if __name__ == '__main__':
    data = downloadDF()
    data = convertDF(data)
    print(data.dtypes)
    parquet_saving(data)
