from dotenv import load_dotenv
load_dotenv()
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
import os
from datetime import datetime
from dateutil.parser import parse
import pytz

from todoist.api import TodoistAPI

def get_token():
    token = os.getenv('TODOIST_APIKEY')
    return token

def update_overdue_tasks(api):
    # Get user's timezone
    user_timezone = pytz.timezone(api.state["user"]["tz_info"]["timezone"])

    # Get current time in user's timezone
    now = datetime.now(tz=user_timezone)

    # Iterate over tasks, look for tasks to update
    tasks = api.state['items']
    for task in tasks:
        if task["due_date_utc"]:
            # Convert to user's timezone
            due_date = parse(task["due_date_utc"]).astimezone(user_timezone)

            # If due in the past and it's due today,
            # update to end of today (default for all day tasks)
            if due_date <= now and due_date.date() == now.date():
                print("Identified newly due task: {0}".format(task["content"]))
                new_due_date = datetime(year=now.year,
                                        month=now.month,
                                        day=now.day,
                                        hour=23,
                                        minute=59,
                                        second=59).astimezone(pytz.utc)
                task.update(due_date_utc=new_due_date)
                print("Updating task <{0}> to due date: {1}".format(task["content"], new_due_date))

def main():
    API_TOKEN = get_token()
    if not API_TOKEN:
        logging.warn('Please set the API token in environment variable.')
        exit()
    api = TodoistAPI(API_TOKEN)
    api.sync()
    update_overdue_tasks(api)
    api.commit()
