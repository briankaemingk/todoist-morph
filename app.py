import morph
from flask import Flask

app = Flask(__name__)


@app.route('/')
def main():
    morph.main()
    return 'Completed'


if __name__ == '__main__':
    app.run()
