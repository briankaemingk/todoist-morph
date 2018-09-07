import os
from datetime import datetime, timedelta
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
def initiate_api():
    API_TOKEN = get_token()
    if not API_TOKEN:
        logging.warning('Please set the API token in environment variable.')
        exit()
    api = TodoistAPI(API_TOKEN)
    api.sync()
    return api


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
    return re.search(r'<(\d+:\d+:*\d*)*>', task_content)


# Parse time string, convert to datetime object in user's timezone
def convert_time_str_datetime(time_str, user_timezone):
    return parse(time_str).astimezone(user_timezone)


# Convert a datetime object into the todoist due date string format
def convert_datetime_str(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S')


# Replace with the user-entered hour, minute and, optionally, second, and convert to utc datetime object
def replace_due_date_time(new_due_time, due_date_utc, user_timezone):
    due_date_localtz_date = convert_time_str_datetime(due_date_utc, user_timezone)
    if(new_due_time):
        new_due_time_split = new_due_time.split(":")
        new_due_date_localtz_date = due_date_localtz_date.replace(hour=int(new_due_time_split[0]),
                                                              minute=int(new_due_time_split[1]),
                                                              second= int(0))
    else:
        new_due_date_localtz_date = due_date_localtz_date.replace(hour=23, minute=23, second= 59)
    new_due_date_utc_date = new_due_date_localtz_date.astimezone(pytz.utc)
    return new_due_date_utc_date


# Determine if text has content text[streak n]
def is_habit(text):
    return re.search(r'\[streak\s(\d+)\]', text)


# Update streak contents from text [streak n] to text [streak n+1]
def update_streak(task, streak):
    streak_num = '[streak {}]'.format(streak)
    new_content = re.sub(r'\[streak\s(\d+)\]', streak_num, task['content'])
    task.update(content=new_content)


# Find task ID from a task URL in format https://todoist.com/showTask?id=2690174754
def parse_task_id(task_url):
    task_match = re.search('https:\/\/todoist.com\/showTask\?id=([0-9]+)', task_url)
    task_id = task_match.group(1)
    return task_id


# If a task
def is_due_yesterday(due_date, now):
    yesterday = now - timedelta(1)
    yesterday.strftime('%m-%d-%y')
    if due_date.strftime('%m-%d-%y') == yesterday.strftime('%m-%d-%y') : return 1


# Identify overdue tasks and schedule them for all day
def update_overdue_tasks(user_timezone, now, tasks):
    for task in tasks:
        due_date_utc = task["due_date_utc"]
        if due_date_utc:
            due_date = convert_time_str_datetime(due_date_utc, user_timezone)
            # If the task is due today and it is due in the past
            if due_date <= now and due_date.date() == now.date():
                task.update(due_date_utc=update_to_all_day(now))
            if is_habit(task['content']) and is_due_yesterday(due_date, now):
                update_streak(task, 0)
                task.update(due_date_utc=update_to_all_day(now))
                task.update(date_string=task['date_string'] + ' starting tod')


# Identify tasks with time strings (for example, <5:20>) and re-schedule due-time to that time
def update_recurrence_date(user_timezone, tasks):
    for task in tasks:
        if task["due_date_utc"] and is_recurrence_snooze(task["content"]):
            new_due_time = is_recurrence_snooze(task["content"]).group(1)
            new_due_date_utc = replace_due_date_time(new_due_time, task["due_date_utc"], user_timezone)
            new_due_date_utc_str = convert_datetime_str(new_due_date_utc)
            # # If the new due date is after the old due date
            # if new_due_date_utc > convert_time_str_datetime(task["due_date_utc"], user_timezone):
            #     task.update(content=re.sub(is_recurrence_snooze(task["content"]).group(0), '', task["content"]))
            # else:
            #     task.update(content= re.sub(is_recurrence_snooze(task["content"]).group(0), '', task["content"]) + '->')
            task.update(content=re.sub(is_recurrence_snooze(task["content"]).group(0), '', task["content"]))
            task.update(due_date_utc=new_due_date_utc_str)


# If a task is a habit, increase the streak by +1
def increment_streak(task, task_url):
    content = task['content']
    if is_habit(content):
        habit = is_habit(content)
        streak = int(habit.group(1)) + 1
        update_streak(task, streak)


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
    task_id = parse_task_id(task_url)
    task = api.items.get_by_id(int(task_id))
    increment_streak(task, task_url)
    api.commit()
