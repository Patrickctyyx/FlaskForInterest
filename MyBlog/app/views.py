from flask import render_template
from app import app


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/blog/<id>')
def show_bolg(id):
    return render_template('blog.html')


@app.route('/index')
def all_blogs():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
