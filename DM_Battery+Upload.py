import requests
from datetime import datetime, timedelta
from telegram import Bot
import pytz  # Importa la libreria pytz
import sys
sys.stderr = open("/path/to/error.log", "a")


# Inserisci il tuo token del bot Telegram
TELEGRAM_BOT_TOKEN = '6845653655:AAGc__iu9HKR-jfQHNxQ8ukWuYHD-JNjoaE'

# Inserisci l'ID del tuo chat su Telegram
TELEGRAM_CHAT_ID = '-1002079278580'


def check_remote_file_update(file_url, threshold_minutes=16):
    try:
        # Effettua una richiesta HEAD per ottenere l'ultimo aggiornamento del file
        response = requests.head(file_url)
        last_modified_header = response.headers.get('Last-Modified')

        # Converti la data dell'ultimo aggiornamento in formato datetime
        last_modified_time = datetime.strptime(last_modified_header, '%a, %d %b %Y %H:%M:%S %Z')

        # Aggiungi il fuso orario corretto usando pytz
        last_modified_time = last_modified_time.replace(tzinfo=pytz.utc)
        last_modified_time = last_modified_time.astimezone(pytz.timezone('Australia/Sydney'))

        # Calcola la differenza di tempo in minuti
        time_difference = datetime.now(pytz.timezone('Australia/Sydney')) - last_modified_time
        minutes_difference = time_difference.total_seconds() / 60

        return minutes_difference <= threshold_minutes
    except Exception as e:
        print(f"Errore durante il controllo dell'aggiornamento del file {file_url}: {e}")
        return False


def main():
    # URL dei tuoi file CSV sul sito
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

    all_files_updated = all(check_remote_file_update(file_url) for file_url in csv_file_urls)

    if all_files_updated:
        print("Tutte le schede sono in funzione.")

        # Invia un messaggio Telegram
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        message = "Tutte le schede sono in funzione:)"
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    else:
        for file_url in csv_file_urls:
            if not check_remote_file_update(file_url):
                print(f"Il file {file_url} non è stato aggiornato da più di 16 minuti. Invio messaggio Telegram.")

                # Invia un messaggio Telegram
                bot = Bot(token=TELEGRAM_BOT_TOKEN)
                message = f"Attenzione! Il file {file_url} non è stato aggiornato da più di 16 minuti."
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


if __name__ == "__main__":
    main()
