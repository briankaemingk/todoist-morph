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


def get_token():
    token = os.getenv('TODOIST_APIKEY')
    return token

def is_overdue(due_date, now):
    if due_date <= now and due_date.date() == now.date() : return 1

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

def is_recurrance_snooze(task_content):
    return re.search(r'\s{(\d+:\d+)}', task_content)

def parse_task_id(task_url):
    #URL is in format: https://todoist.com/showTask?id=2690174754
    task_match = re.search('https:\/\/todoist.com\/showTask\?id=([0-9]+)', task_url)
    task_id = task_match.group(1)
    return task_id

def update_overdue_tasks(api):
    user_timezone = get_user_timezone(api)
    now = get_now_user_timezone(api)

    # Iterate over tasks, look for tasks to update
    tasks = api.state['items']
    for task in tasks:
        if task["due_date_utc"]:
            # Convert to user's timezone
            due_date = parse(task["due_date_utc"]).astimezone(user_timezone)

            if is_overdue(due_date, now):
                new_due_date = update_to_all_day(now, task)
                task.update(due_date_utc=new_due_date)
                print("Updating task <{0}> to due date: {1}".format(task["content"], new_due_date))

def update_recurrance_date(api, task_url):
    user_timezone = get_user_timezone(api)

    task_id = parse_task_id(task_url)

    tasks = api.state['items']
    for task in tasks:
        if task["due_date_utc"] and is_recurrance_snooze(task["content"]):
            due_time = is_recurrance_snooze(task["content"]).group(1)

def main():
    API_TOKEN = get_token()
    if not API_TOKEN:
        logging.warn('Please set the API token in environment variable.')
        exit()
    api = TodoistAPI(API_TOKEN)
    api.sync()
    update_overdue_tasks(api)
    api.commit()


def task_complete(task_url):
    API_TOKEN = get_token()
    if not API_TOKEN:
        logging.warn('Please set the API token in environment variable.')
        exit()
    api = TodoistAPI(API_TOKEN)
    api.sync()
    update_recurrance_date(api, task_url)
    api.commit()
