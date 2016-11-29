#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import random

from flask import Flask, render_template, flash, redirect, url_for, session
from flask_wtf import Form
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TYTS,SN!'
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    # 用session来储存变量值
    session['number'] = random.randint(0, 100)
    session['times'] = 10
    return render_template('index.html')


@app.route('/guess', methods=['GET', 'POST'])
def guess():
    times = session['times']
    result = session.get('number')
    form = GuessNumberForm()
    if form.validate_on_submit():
        times -= 1
        session['times'] = times
        if times == 0:
            flash(u'你输啦')
            return redirect(url_for('.index'))
        answer = form.number.data
        if answer > result:
            flash(u'太大了！你还剩%s次机会' % times)
        elif answer < result:
            flash(u'太小了！你还剩%s次机会' % times)
        else:
            flash(u'猜对了，你真厉害！')
            return redirect(url_for('.index'))
    return render_template('guess.html', form=form)


class GuessNumberForm(Form):
    number = IntegerField(u'输入数字(0~100)', validators=[
        DataRequired(u'输入一个有效的数字！'),
        NumberRange(0, 100, u'请输入0~100以内的数字！')
    ])  # u means Unicode
    submit = SubmitField(u'提交')


if __name__ == '__main__':
    app.run(port=8000)
