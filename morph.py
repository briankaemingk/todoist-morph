from dotenv import load_dotenv
load_dotenv()
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

from todoist.api import TodoistAPI


def get_token():
    token = os.getenv('TODOIST_APIKEY')
    return token
