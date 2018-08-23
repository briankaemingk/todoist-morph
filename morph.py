from dotenv import load_dotenv
load_dotenv()
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
import os
from datetime import datetime
from dateutil.parser import parse
import pytz
import re
from todoist.api import TodoistAPI


# Get user's Todoist API Key
def get_token():
    token = os.getenv('TODOIST_APIKEY')
    return token


# Initiate and sync Todoist API
def initiate_api():
    API_TOKEN = get_token()
    if not API_TOKEN:
        logging.warn('Please set the API token in environment variable.')
        exit()
    api = TodoistAPI(API_TOKEN)
    api.sync()
    return api


def is_overdue(due_date, now):
    if due_date <= now and due_date.date() == now.date(): return 1


# If due in the past and it's due today,
# update to end of today (default for all day tasks)
def update_to_all_day(now, task):
    new_due_date = datetime(year=now.year,
                            month=now.month,
                            day=now.day,
                            hour=23,
                            minute=59,
                            second=59).astimezone(pytz.utc)
    return new_due_date


# Get user's timezone
def get_user_timezone(api):
    return pytz.timezone(api.state["user"]["tz_info"]["timezone"])


# Get current time in user's timezone
def get_now_user_timezone(api):
    user_timezone = get_user_timezone(api)
    return datetime.now(tz=user_timezone)

# Get all tasks
def get_tasks(api):
    return api.state['items']

def is_recurrance_snooze(task_content):
    return re.search(r'\s<(\d+:\d+)>', task_content)


def update_overdue_tasks(user_timezone, now, tasks):
    for task in tasks:
        if task["due_date_utc"]:
            # Convert to user's timezone
            due_date = parse(task["due_date_utc"]).astimezone(user_timezone)

            if is_overdue(due_date, now):
                new_due_date = update_to_all_day(now, task)
                task.update(due_date_utc=new_due_date)
                print("Updating task <{0}> to due date: {1}".format(task["content"], new_due_date))


def convert_time_str_datetime(time_str, user_timezone):
    return datetime.strptime(time_str, '%a %d %b %Y %H:%M:%S %z').astimezone(user_timezone)


def convert_datetime_str(date):
    return date.strftime('%Y-%m-%dT%H:%M')


def replace_due_date_time(new_due_time, due_date_utc, user_timezone):
    due_date_localtz_date = convert_time_str_datetime(due_date_utc, user_timezone)
    new_due_time_split = new_due_time.split(":")
    new_due_date_localtz_date = due_date_localtz_date.replace(hour=int(new_due_time_split[0]), minute=int(new_due_time_split[1]))
    new_due_date_utc_date = new_due_date_localtz_date.astimezone(pytz.utc)
    return new_due_date_utc_date


def update_recurrance_date(api):
    user_timezone = get_user_timezone(api)

    # Iterate over tasks, look for tasks to update
    tasks = api.state['items']
    for task in tasks:
        if task["due_date_utc"]:
            if task["due_date_utc"] and is_recurrance_snooze(task["content"]):
                new_due_time = is_recurrance_snooze(task["content"]).group(1)
                new_due_date_utc = replace_due_date_time(new_due_time, task["due_date_utc"], user_timezone)
                new_due_date_utc_str = convert_datetime_str(new_due_date_utc)
                task.update(due_date_utc=new_due_date_utc_str)
                task.update(content= re.sub(is_recurrance_snooze(task["content"]).group(0), '', task["content"]))

# Run the following actions continually (every 15 minuites)
def main():
    api = initiate_api()
    user_timezone = get_user_timezone(api)
    tasks = get_tasks(api)
    now = get_now_user_timezone(api)
    update_overdue_tasks(user_timezone, now, tasks)
    update_recurrance_date(api)
    api.commit()

# Run the following actions when a task is completed, recieves the task URL
def task_complete(task_url):
    api = initiate_api()
    api.commit()
