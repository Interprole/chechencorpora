from flask import Flask, render_template, request, redirect, Response, session

app = Flask(__name__)


@app.route('/')
def base():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(port=80, debug=False)
