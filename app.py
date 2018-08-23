import morph
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    morph.main()
    return 'Completed'

@app.route('/complete', methods=['GET', 'POST'])
def complete():
    content = request.get_json()
    url = content['url']
    morph.task_complete(url)
    return 'Completed task complete actions.'

if __name__ == '__main__':
    app.run()
