import requests
import time
import curses
import random
from threading import Thread, Lock
from datetime import datetime, timedelta, timezone

# List of user IDs
user_ids = ['1111111111', '2222222222', '3333333333', '4444444444', '7420569840', '5555555555']  # Add more user IDs here

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

# State management for users
user_data = {}
user_colors = {}  # To store the color pairs for each user
lock = Lock()

def userinfo(user_id):
    api_url = f'https://api.tondrips.com/user/{user_id}'

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Extract balance and last_claim
        balance = data.get('user', {}).get('balance')
        last_claim_str = data.get('user', {}).get('last_claim')
        if last_claim_str:
            last_claim_time = datetime.fromisoformat(last_claim_str.replace('Z', '+00:00'))
        else:
            last_claim_time = datetime.now(timezone.utc)
        
        with lock:
            user_data[user_id] = {
                'balance': balance,
                'last_claim_time': last_claim_time
            }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching user info for {user_id}: {e}")

def claim(user_id):
    claim_url = f'https://api.tondrips.com/user/claim/{user_id}'

    try:
        response = requests.get(claim_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Extract message
        message = data.get('message')
        return message

    except requests.exceptions.RequestException as e:
        print(f"Error claiming for {user_id}: {e}")
        return None

def setup_curses_colors(stdscr):
    curses.start_color()
    # Define color pairs for users
    for i in range(len(user_ids)):
        curses.init_pair(i + 1, random.randint(1, 7), curses.COLOR_BLACK) 

def user_thread(user_id, stdscr):
    claim_interval = timedelta(minutes=5)  # 5 minutes
    color_pair_id = user_ids.index(user_id) + 1 

    while True:
        userinfo(user_id)

        with lock:
            user_info = user_data.get(user_id, {})
            balance = user_info.get('balance')
            last_claim_time = user_info.get('last_claim_time', datetime.now(timezone.utc))
        
        if balance is not None:
            current_time = datetime.now(timezone.utc)

            if current_time - last_claim_time >= claim_interval:
                message = claim(user_id)
                msg = f"User {user_id} claimed: {message}"
                with lock:
                    user_data[user_id]['last_claim_time'] = current_time
                stdscr.addstr(user_ids.index(user_id), 0, msg, curses.color_pair(color_pair_id))
            else:
                time_remaining = claim_interval - (current_time - last_claim_time)
                msg = f"User {user_id} Balance: {balance} | Next claim in: {int(time_remaining.total_seconds())} seconds"
                stdscr.addstr(user_ids.index(user_id), 0, msg, curses.color_pair(color_pair_id)) 

        else:
            msg = f"User {user_id} Balance info unavailable"
            stdscr.addstr(user_ids.index(user_id), 0, msg, curses.color_pair(color_pair_id)) 

        stdscr.refresh()
        time.sleep(1)

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    setup_curses_colors(stdscr)

    threads = []
    for user_id in user_ids:
        thread = Thread(target=user_thread, args=(user_id, stdscr))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    curses.wrapper(main)
