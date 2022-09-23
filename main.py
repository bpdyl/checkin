from checkin import CheckInBot
from keep_alive import keep_alive
import pytz 
from datetime import datetime,date
import time
import calendar
import os
username = os.environ['username']
pwd = os.environ['pwd']
login_cred = {
    "alias" : "Bibek Paudyal",
    "username" : username,
    "password" : pwd
}


keep_alive()
weekend = ['Saturday','Sunday']
while True:
    np_time = datetime.now(pytz.timezone('Asia/Kathmandu')).strftime("%H:%M:%S")
    d = date.today()
    day = calendar.day_name[d.weekday()]
    # cur_time = datetime.now().strftime("%H:%M:%S")
    if np_time == '17:32:30' and day not in weekend :
        bot = CheckInBot()
        bot.login(login_cred)
        print("Its about time to checkout")
        try:
            bot.checkout()
        except Exception as e:
            print("you might have already checked out",e)
        time.sleep(55800)

    if np_time == '08:19:10' and day not in weekend:
        bot = CheckInBot()      
        bot.login(login_cred)
        print("Now it's time to checkin")
        try:
            bot.checkin()
        except Exception as e:
            print("you might have already checked in",e)
        time.sleep(32400)

  