import re
from datetime import datetime, timedelta

def is_habit(text):
    return re.search(r'\[streak\s(\d+)\]', text)

def update_streak(item, streak):
    streak_num = '[streak {}]'.format(streak)
    text = re.sub(r'\[streak\s(\d+)\]', streak_num, item['content'])
    item.update(content=text)

def parse_task_id(task_url):
    #URL is in format: https://todoist.com/showTask?id=2690174754
    task_match = re.search('https:\/\/todoist.com\/showTask\?id=([0-9]+)', task_url)
    task_id = task_match.group(1)
    return task_id

def is_due(text):
    yesterday = datetime.utcnow().strftime("%a %d %b")
    return text[:10] == yesterday

def increment_streak(api, task_url):
    task_id = parse_task_id(task_url)
    task = api.items.get_by_id(task_id)
    content = task["item"]["content"]
    if is_habit(content):
        habit = is_habit(content)
        streak = int(habit.group(1)) + 1
        update_streak(task, streak)
        api.commit()


def reset_streak(api):
    tasks = api.state['items']
    for task in tasks:
        if task['due_date_utc'] and is_habit(task['content']) and is_due(task['due_date_utc']):
            update_streak(task, 0)
            date_string = task['date_string']
            task.update(date_string= date_string + ' starting tod')
    api.commit()
