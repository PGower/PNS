from flask import Flask, abort, redirect, url_for, jsonify, request
import json
import re
import os
import sqlite3
import arrow
import logging
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser

base_path = os.path.dirname(os.path.abspath(__file__))

ip_regex = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

db_path = os.path.join(base_path, 'db.sqlite')
src_sql = os.path.join(os.path.dirname(db_path), 'tables.sql')

whoosh_path = os.path.join(base_path, 'ft_search')

app = Flask(__name__)
app.debug = True

logger = logging.getLogger(__name__)
debug = logger.debug
warn = logger.warning
info = logger.info


# DB
def get_cursor():
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    return c.cursor()

# Whoosh
def get_index():
    return open_dir(whoosh_path)


# API
@app.route('/api/v1/user/<username>', methods=['GET'])
def api_get_address_for_user(username):
    c = get_cursor()
    c.execute('SELECT ip_address, created FROM PersonAddresses WHERE username = ? AND expired = 0', (username,))
    r = c.fetchone()
    if not r:
        abort(404)
    else:
        return jsonify(**r)


@app.route('/api/v1/address/<address>', methods=['GET'])
def api_get_user_for_address(address):
    c = get_cursor()
    c.execute('SELECT username, created FROM PersonAddresses WHERE ip_address = ? AND expired = 0', (address,))
    r = c.fetchone()
    if not r:
        abort(404)
    else:
        return jsonify(**r)


@app.route('/api/v1/search', methods=['GET'])
def api_get_info_for_name():
    ix = get_index()
    with ix.searcher() as searcher:
        query_text = request.args.get('q')
        info(query_text)
        limit = int(request.args.get('limit', 15))
        query = QueryParser("name", ix.schema).parse(query_text)
        whoosh_results = searcher.search(query)
        return jsonify({'length':len(whoosh_results)})


@app.route('/api/v1/action/login', methods=['POST'])
def api_action_login():
    c = get_cursor()
    # Set any records with the same username as expired
    c.execute('UPDATE PersonAddresses SET expired = 1 WHERE username = ?', (request.form['username'],))
    # Create new record
    c.execute('INSERT INTO PersonAddresses (username, computer_name, ip_address, created) VALUES (?, ?, ?, ?)', (request.form['username'], request.form['computer_name'], request.form['ip_address'], arrow.now().timestamp))
    # Get newly created ROWID
    c.connection.commit()

    ix = get_index()
    writer = ix.writer()
    writer.add_document(username=request.form['username'], name=request.form['fullname'])
    writer.commit()

    info('Created new mapping for user: {} to address: {}'.format(request.form['username'], request.form['ip_address']))
    return redirect(url_for('api_get_address_for_user', username=request.form['username']))


@app.route('/api/v1/action/logout', methods=['POST'])
def api_action_logout():
    c = get_cursor()
    c.execute('UPDATE PersonAddresses SET expired = 1 WHERE username = ?', (request.form['username'],))
    c.connection.commit()
    info('Deleted mappings for user: {}'.format(username))


@app.route('/api/v1/action/update', methods=['POST'])
def api_action_update():
    return api_action_login()


if __name__ == '__main__':
    # If there is no table, create one
    if not os.path.exists(db_path):
        c = sqlite3.connect(db_path)
        cursor = c.cursor()
        with open(os.path.join(os.path.dirname(db_path), 'tables.sql'), 'r') as f:
            cursor.executescript(f.read())
    # Setup Whoosh
    if not os.path.exists(whoosh_path):
        os.mkdir(whoosh_path)
        whoosh_schema = Schema(username=TEXT(stored=True), name=NGRAMWORDS(stored=True, minsize=2, maxsize=10, queryor=True))
        create_in(whoosh_path, whoosh_schema)


    app.run()


