# -*- coding: utf-8 -*-
"""
    Github Example
    --------------

    Shows how to authorize users with Github.
"""
import os
import json
from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort
from flaskext.github import GithubAuth

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# load config
with open(os.path.join(os.getcwd(), 'config.json'), 'r') as f:
    config_data = f.read()
config = json.loads(config_data)

# setup flask
app = Flask(__name__)
app.config.update(
    SECRET_KEY = config['secret_key'],
    DEBUG = True,
)

# setup flask-github
github = GithubAuth(
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    session_key='github_access_token'
)

@app.before_request
def before_request():
    g.github_access_token = None
    if 'github_access_token' in session:
        g.user = session['github_access_token']

@app.route('/')
def index():
    if 'github_access_token' in session:
        return github.authorize(callback_url=url_for('authorized', _external=True))
    else:
        return app.send_static_file('github_notification.html')

@github.access_token_getter
def token_getter():
    return g.user

@app.route('/oauth/callback')
@github.authorized_handler
def authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        return redirect(next_url)

    token = resp['access_token']
    g.github_access_token = token
    session['github_access_token'] = token

@app.route('/orgs/<name>')
def orgs(name):
    if github.has_org_access(name):
        return 'Heck yeah he does!'
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('github_access_token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8010)
