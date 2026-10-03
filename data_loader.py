# щербина алексей 2 дз
import pandas as pd
import gdown
import os

def skachivanie():
    ssylka = 'https://drive.google.com/file/d/1BtFPueekTleALZJKeWwrfsnWMtw-BuPj/view?usp=share_link'    # ссылка на таблицу
    dataset = 'dataset.csv'
    if not os.path.exists(dataset):
        gdown.download(ssylka, dataset, quiet=False)         # скачиваю таблицу с гугл диска
    df = pd.read_csv(dataset)            # читаю таблицу и вывожу первые 10 смысловых строк
    print('ниже представлены первые 10 строк датасета:')
    tabl= df.head(10)
    print(tabl)
    
if __name__ == '__main__':
    skachivanie()
