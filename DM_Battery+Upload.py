import requests
from datetime import datetime, timedelta
from telegram import Bot
import pytz
import pandas as pd
from bs4 import BeautifulSoup
import os
from io import BytesIO
from telegram.ext import Updater
import asyncio
import logging
import urllib.parse


TELEGRAM_BOT_TOKEN = '6845653655:AAGc__iu9HKR-jfQHNxQ8ukWuYHD-JNjoaE'
TELEGRAM_CHAT_ID = '-1002079278580'

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

async def check_remote_file_update(file_url, threshold_minutes=16):
    try:
        last_modified_time = datetime.strptime(requests.head(file_url).headers.get('Last-Modified'), '%a, %d %b %Y %H:%M:%S %Z') \
            .replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Australia/Sydney'))
        return (datetime.now(pytz.timezone('Australia/Sydney')) - last_modified_time).total_seconds() / 60 <= threshold_minutes
    except Exception as e:
        logger.error(f"Errore durante il controllo dell'aggiornamento del file {file_url}: {e}")
        return False

async def scarica_e_unisci_csv(url, cartella_destinazione, file_excel_destinazione):
    links = [urllib.parse.urljoin(url, link['href']) for link in BeautifulSoup(requests.get(url).text, 'html.parser').find_all('a', href=lambda href: (href and href.endswith('.csv')))]
    df_dict = {os.path.splitext(os.path.basename(file_csv_url))[0]: pd.read_csv(BytesIO(requests.get(file_csv_url).content)) for file_csv_url in links}

    file_excel_path = os.path.join(cartella_destinazione, file_excel_destinazione)
    with pd.ExcelWriter(file_excel_path, engine='xlsxwriter') as writer:
        for nome_foglio, df in df_dict.items():
            df.to_excel(writer, sheet_name=nome_foglio, index=False)

    messaggi = [f"Batteria {nome_foglio} {'carica' if df.iloc[-1, 2] > 3700 else 'scarica'}, Ultimo valore: {df.iloc[-1, 2]}" for nome_foglio, df in df_dict.items()]

    await invia_notifica_telegram("\n".join(messaggi))

async def invia_notifica_telegram(messaggio):
    try:
        Updater(token=TELEGRAM_BOT_TOKEN, use_context=True).bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio)
    except Exception as e:
        logger.error(f"Errore nell'invio del messaggio a Telegram: {e}")

async def main():
    csv_file_urls = [
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/C1.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/C2.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/C3.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/C4.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/C5.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/P1.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/P2.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/P3.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/P4.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/P5.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/S1.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/S2.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/S3.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/S4.csv',
        'https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/S5.csv'
    ]

    if not all(await asyncio.gather(*(check_remote_file_update(file_url) for file_url in csv_file_urls))):
        for file_url in csv_file_urls:
            if not await check_remote_file_update(file_url):
                Bot(token=TELEGRAM_BOT_TOKEN).send_message(chat_id=TELEGRAM_CHAT_ID, text=f"Attenzione! Il file {file_url} non è stato aggiornato da più di 16 minuti.")

    await scarica_e_unisci_csv('https://www.bosl.com.au/IoT/wsudwatch/FYP_SGI/', r'C:\Users\cmare\Desktop', 'Download_separate_sheets.xlsx')

if __name__ == "__main__":
    asyncio.run(main())
