import os
from datetime import datetime
from dateutil.parser import parse
import pytz
import re
from todoist.api import TodoistAPI
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Get user's Todoist API Key
def get_token():
    token = os.getenv('TODOIST_APIKEY')
    return token


# Initiate and sync Todoist API
# noinspection PyPep8Naming
def initiate_api():
    API_TOKEN = get_token()
    if not API_TOKEN:
        logging.warning('Please set the API token in environment variable.')
        exit()
    api = TodoistAPI(API_TOKEN)
    api.sync()
    return api


# If the task is due today and it is due in the past
def is_overdue(due_date, now):
    if due_date <= now and due_date.date() == now.date(): return 1


# Update due date to end of today (default for all day tasks)
def update_to_all_day(now):
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


# Find hours, minutes and, optionally, seconds
def is_recurrence_snooze(task_content):
    return re.search(r'\s<(\d+:\d+:*\d*)>', task_content)


# Parse time string, convert to datetime object in user's timezone
def convert_time_str_datetime(time_str, user_timezone):
    return parse(time_str).astimezone(user_timezone)


# Convert a datetime object into the todoist due date string format
def convert_datetime_str(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S')


# Replace with the user-entered hour, minute and, optionally, second, and convert to utc datetime object
def replace_due_date_time(new_due_time, due_date_utc, user_timezone):
    due_date_localtz_date = convert_time_str_datetime(due_date_utc, user_timezone)
    new_due_time_split = new_due_time.split(":")
    new_due_date_localtz_date = due_date_localtz_date.replace(hour=int(new_due_time_split[0]),
                                                              minute=int(new_due_time_split[1]))
    if len(new_due_time_split) > 2: new_due_date_localtz_date = due_date_localtz_date.replace(
        second=int(new_due_time_split[2]))
    new_due_date_utc_date = new_due_date_localtz_date.astimezone(pytz.utc)
    return new_due_date_utc_date


# Identify overdue tasks and schedule them for all day
def update_overdue_tasks(user_timezone, now, tasks):
    for task in tasks:
        if task["due_date_utc"]:
            due_date = convert_time_str_datetime(task["due_date_utc"], user_timezone)
            if is_overdue(due_date, now):
                new_due_date = update_to_all_day(now)
                task.update(due_date_utc=new_due_date)


# Identify tasks with time strings (for example, <5:20>) and re-schedule due-time to that time
def update_recurrence_date(user_timezone, tasks):
    for task in tasks:
        if task["due_date_utc"] and is_recurrence_snooze(task["content"]):
            new_due_time = is_recurrence_snooze(task["content"]).group(1)
            new_due_date_utc = replace_due_date_time(new_due_time, task["due_date_utc"], user_timezone)
            new_due_date_utc_str = convert_datetime_str(new_due_date_utc)
            task.update(due_date_utc=new_due_date_utc_str)
            task.update(content=re.sub(is_recurrence_snooze(task["content"]).group(0), '', task["content"]))


# Run the following actions continually (every 15 minutes)
def main():
    api = initiate_api()
    user_timezone = get_user_timezone(api)
    tasks = get_tasks(api)
    now = get_now_user_timezone(api)
    update_overdue_tasks(user_timezone, now, tasks)
    update_recurrence_date(user_timezone, tasks)
    api.commit()


# Run the following actions when a task is completed, receives the task URL
def task_complete(task_url):
    api = initiate_api()
    api.commit()
