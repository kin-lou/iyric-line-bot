from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello Flask'

@app.route('/test')
def test():
    return 'test api'

if __name__ == '__main__':
    app.run()
