import morph
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    morph.main()
    return 'Completed'

@app.route('/complete')
def complete():
    task_url = str(request.data)
    morph.task_complete(task_url)
    return 'Completed task complete actions.'

if __name__ == '__main__':
    app.run()
