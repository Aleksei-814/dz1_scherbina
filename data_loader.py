# щербина алексей 3 дз
import pandas as pd
import gdown
import os

def downloadDF():
    url = 'https://drive.google.com/file/d/1BtFPueekTleALZJKeWwrfsnWMtw-BuPj/view?usp=share_link'    # ссылка на таблицу
    dataset = 'dataset.csv'
    if not os.path.exists(dataset):
        gdown.download(url, dataset, quiet=False)      # скачиваю таблицу с гугл диска
    df = pd.read_csv(dataset)            # читаю таблицу и вывожу первые 10 смысловых строк (от 0 до 9)
    print('ниже представлены первые 10 строк датасета:')
    tabl= df.head(10)
    print(tabl)
if __name__ == '__main__':
    downloadDF()
