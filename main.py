from checkin import CheckInBot
from keep_alive import keep_alive
# from telegram.ext.updater import Updater
import pytz
from datetime import datetime, date, timedelta
from datetime import time as get_time
import datetime as dt
import time
import requests
import calendar
import os, json
import random
import logging


##custom function to send the message to telegram channel
def send_telegram_message(token, chat_id, msg):
  url = f'https://api.telegram.org/bot{token}/sendMessage'
  params = {
    "chat_id": chat_id,
    "text": msg,
  }
  requests.get(url, params=params)

def decrypt(encrypted_data, key):
    decrypted_data = ""
    key_index = 0
    for char in encrypted_data:
        decrypted_data += chr(ord(char) ^ ord(key[key_index]))
        key_index = (key_index + 1) % len(key)
    return decrypted_data

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

decrypt_key = os.environ.get('DECRYPT_KEY')
BOT_TOKEN = os.environ.get('BOT_TOKEN') #'5836627566:AAFtwNffd9hEgj2M2WrMQ1SHE1m1DUnCJpw'
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') #'969004992'

keep_alive()
WEEKEND_DAYS = ['Saturday', 'Sunday']

WEEKDAY_TIME_RANGES = {
  'Monday': {
    'checkin': (get_time(8, 0), get_time(8, 10)),
    'checkout': (get_time(18, 0), get_time(18, 10))
  },
  'Tuesday': {
    'checkin': (get_time(8, 10), get_time(8, 20)),
    'checkout': (get_time(17, 35), get_time(17, 45))
  },
  'Wednesday': {
    'checkin': (get_time(8, 12), get_time(8, 19)),
    'checkout': (get_time(17, 50), get_time(18, 0))
  },
  'Thursday': {
    'checkin': (get_time(8, 6), get_time(8, 15)),
    'checkout': (get_time(17, 37), get_time(17, 51))
  },
  'Friday': {
    'checkin': (get_time(8, 7), get_time(8, 14)),
    'checkout': (get_time(17, 51), get_time(18, 0))
  },
  'Saturday': {
    'checkin': None,
    'checkout': None,
  },
  'Sunday': {
    'checkin': None,
    'checkout': None,
  }
}

LAST_CHECKIN_CHECKOUT_FILE = 'last_checkin_checkout.json'


def get_random_time_in_range(weekday, time_type):
  time_range = WEEKDAY_TIME_RANGES[weekday][time_type]
  try:
    start_time, end_time = time_range
    start_datetime = datetime.combine(date.min, start_time)
    end_datetime = datetime.combine(date.min, end_time)
    print(f'start: {start_datetime} and end: {end_datetime}')
    print(f'diff in seconds: {(end_datetime - start_datetime).seconds}')
    seconds = random.randint(0, (end_datetime - start_datetime).seconds)
    print(f'calculated seconds : {seconds}')
    return (start_datetime + timedelta(seconds=seconds)).time().strftime("%H:%M")
  except Exception as e:
     print(f'Could not get the time range. Maybe it is weekend days. No need to {time_type}. Happy Weekend !!')


def perform_bot_operation(operation_name, operation_func, display_date,user):
  try:
    operation_func()
    logger.info(f'{operation_name} successful for the date: {display_date} and user: {user}.')
    send_telegram_message(
      token=BOT_TOKEN,
      chat_id=TELEGRAM_CHAT_ID,
      msg=f'{operation_name} successful for the date: {display_date} and user : {user}.')
  except Exception as e:
    logger.error(
      f'{operation_name} unsuccessful for date {display_date} and user: {user}. Please perform the operation manually.\nError Message: {e}'
    )
    send_telegram_message(
      BOT_TOKEN,
      chat_id=TELEGRAM_CHAT_ID,
      msg=
      f'{operation_name} unsuccessful for date {display_date} and user: {user}. Please perform the operation manually.\nError Message: {e}'
    )


# def read_last_checkin_checkout_times():
#   try:
#     with open(LAST_CHECKIN_CHECKOUT_FILE) as f:
#       data = json.load(f)
#   except (FileNotFoundError, json.JSONDecodeError):
#     data = {'last_checkin': None, 'last_checkout': None}
#   return data
    
def read_last_checkin_checkout_times():
  try:
    with open(LAST_CHECKIN_CHECKOUT_FILE) as f:
      data = json.load(f)
    print(f"This is last checkin checkout data read : {data}")

  except (FileNotFoundError, json.JSONDecodeError):
    data = {'user':None,'last_checkin': None, 'last_checkout': None}
  return data


# def write_last_checkin_checkout_times(last_checkin_time, last_checkout_time):
#   data = {
#     'last_checkin': last_checkin_time,
#     'last_checkout': last_checkout_time
#   }
#   with open(LAST_CHECKIN_CHECKOUT_FILE, 'w') as f:
#     json.dump(data, f)

def write_last_checkin_checkout_times(user, last_checkin_time:None, last_checkout_time:None):
    with open(LAST_CHECKIN_CHECKOUT_FILE, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    if user not in data:
        data[user] = {'last_checkin': None, 'last_checkout': None}

    data[user]['last_checkin'] = last_checkin_time
    data[user]['last_checkout'] = last_checkout_time

    print(f"This is last checkin checkout data write: {data}")
    
    with open(LAST_CHECKIN_CHECKOUT_FILE, 'w') as f:
        json.dump(data, f)


def my_main(login_cred):
  np_time = datetime.now(
    pytz.timezone('Asia/Kathmandu')).time().strftime("%H:%M")
  logger.info(f'Current time in Kathmandu: {np_time}')

  d = date.today()
  day = calendar.day_name[d.weekday()]

  last_checkin_checkout_times = read_last_checkin_checkout_times()
  user = login_cred['user']
  if user not in last_checkin_checkout_times:
    # If the user doesn't exist in the data, write initial data
    write_last_checkin_checkout_times(user, None, None)
    last_checkin_checkout_times = read_last_checkin_checkout_times()  # Refresh data
  last_checkin_date = last_checkin_checkout_times[user]['last_checkin']
  last_checkout_date = last_checkin_checkout_times[user]['last_checkout']
  try:
    random_checkin_time = get_random_time_in_range(day,
                                                   'checkin')
    random_checkout_time = get_random_time_in_range(
      day, 'checkout')
    logger.info(f'Random checkin time: {random_checkin_time}')
    logger.info(f'Random checkout time: {random_checkout_time}')

    display_date = datetime.now(pytz.timezone('Asia/Kathmandu'))

    if np_time == random_checkout_time and day not in WEEKEND_DAYS and last_checkout_date != display_date.date(
    ).isoformat():
      bot = CheckInBot()
      bot.login(login_cred)
      logger.info(f"Random checkout time: {random_checkout_time}")
      logger.info(f'Last Checkin Time of user {user}: {last_checkin_date}')
      logger.info(f'Proceeding checkout for user: {user}')
      perform_bot_operation('Checkout', bot.checkout, display_date,user)
      write_last_checkin_checkout_times(user,last_checkin_date,
                                        display_date.date().isoformat())

    if np_time == random_checkin_time and day not in WEEKEND_DAYS and last_checkin_date != display_date.date(
    ).isoformat():
      bot = CheckInBot()
      bot.login(login_cred)
      logger.info(f"Random checkin time: {random_checkin_time}")
      logger.info(f'Last Checkin Time of user {user}: {last_checkin_date}')
      logger.info(f'Proceeding Checkin for user: {user}')
      perform_bot_operation('Checkin', bot.checkin, display_date,user)
      write_last_checkin_checkout_times(user,display_date.date().isoformat(),
                                        last_checkout_date)
  except Exception as e:
    print(f'Something went wrong while checking in. {e}')


def read_user_credentials_from_json(file_path):
    with open(file_path, 'r') as json_file:
        user_credentials = json.load(json_file)
    return user_credentials

def check_in_for_multiple_users(credentials_file_path):
    user_credentials = read_user_credentials_from_json(credentials_file_path)

    for user, credentials in user_credentials.items():
        try:
            # Perform check-in process for each user using their credentials
            # Create login_cred for current user
            username = decrypt(credentials["username"],decrypt_key)
            password = decrypt(credentials["password"],decrypt_key)
            login_cred = {"user": user,'alias':credentials['alias'], "username": username, "password": password}
            # Call my_main with updated login_cred for current user
            logger.info(f'Proceeding the operation for User: {login_cred["alias"]}')
            my_main(login_cred)

        except Exception as e:
            print(f'Something went wrong while checking in for {user}. Error: {e}')

while True:
  check_in_for_multiple_users('user_credentials.json')
  time.sleep(10)
