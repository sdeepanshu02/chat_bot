from apscheduler.schedulers.blocking import BlockingScheduler
from app import send_message
from datetime import datetime,timedelta,date
sched = BlockingScheduler()
curr_time = datetime.utcnow()

@sched.scheduled_job('interval', minutes=3)
def timed_job():
    print('This job is run every three minutes.')
    send_message("1690740887619815","Hola It's "+str(curr_time)+" now")

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
    print('This job is run every weekday at 5pm.')

sched.start()
