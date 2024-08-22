import requests
import time
from colorama import Fore, Style, init
from datetime import datetime, timedelta, timezone

# Colorama
init(autoreset=True)

# edit user id
user_id = '7340833090'

# Headers
headers = {
    'accept-language': 'en-US,en;q=0.9',
    'host': 'api.tondrips.com',
    'if-none-match': 'W/"2d3-yhzEWF9Od6JAXOoNO3xRaqLEsSo"',
    'origin': 'https://www.tondrips.com',
    'priority': 'u=1, i',
    'referer': 'https://www.tondrips.com/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
}

def userinfo():
    api_url = f'https://api.tondrips.com/user/{user_id}'

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        # 'user' anahtarının altındaki 'balance' değerini al
        balance = data.get('user', {}).get('balance')
        
        # 'last_claim' zamanını al ve parse et
        last_claim_str = data.get('user', {}).get('last_claim')
        if last_claim_str:
            # Offset-aware datetime oluştur
            last_claim_time = datetime.fromisoformat(last_claim_str.replace('Z', '+00:00'))
        else:
            last_claim_time = datetime.now(timezone.utc)
        
        return balance, last_claim_time

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Kullanıcı bilgileri istenirken bir hata oluştu: {e}" + Style.RESET_ALL)
        return None, None

def claim():
    claim_url = f'https://api.tondrips.com/user/claim/{user_id}'

    try:
        response = requests.get(claim_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Yanıt mesajını al
        message = data.get('message')
        return message

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Talepte bulunurken bir hata oluştu: {e}" + Style.RESET_ALL)
        return None

if __name__ == '__main__':
    last_claim_time = datetime.now(timezone.utc)  # Başlangıçta `claim` çağrısının zamanı
    claim_interval = timedelta(minutes=5)  # 5 dakika

    while True:
        balance, last_claim_time = userinfo()

        if balance is not None:
            current_time = datetime.now(timezone.utc)

            # 5 dakika geçmişse claim fonksiyonunu çağır
            if current_time - last_claim_time >= claim_interval:
                message = claim()
                last_claim_time = current_time  # Son `claim` çağrısının zamanını güncelle

            # Kalan süreyi hesapla
            time_remaining = claim_interval - (current_time - last_claim_time)

            # Ekranı temizle ve güncellenmiş bilgileri yazdır
            print(Fore.YELLOW + f"\rBalance: {balance}", end='')
            print(Fore.YELLOW + f" | Next claim in: {int(time_remaining.total_seconds())} seconds", end='')

        else:
            print(Fore.RED + "Balance bilgisi alınamadı", end='')

        # Bekle
        time.sleep(1)  # 1 saniyede bir döngüyü devam ettir
