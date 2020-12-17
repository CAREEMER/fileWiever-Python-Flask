from flask import Flask, render_template, redirect, request, url_for
import os
import stat

import configworker as cfgw

from configparser import ConfigParser

app = Flask(__name__)

wsgi_app = app.wsgi_app

FILE_SYSTEM_ROOT = cfgw.read("fileSystemRoot", "SERVERCONFIG", "cfg.ini")

@app.route('/')
def redirect_to_about():
    if cfgw.read("firstInit", "SERVERCONFIG", "cfg.ini") == "True":
        return redirect(url_for('fit'))
    return redirect(url_for('index'))

@app.route('/firstinitsettings')
def fit():
    if cfgw.read("firstInit", "SERVERCONFIG", "cfg.ini") == "False":
        return redirect(url_for('index'))
    return render_template('fit.html')

@app.route('/firstinitsettings', methods=['POST'])
def fit_post():
    text = request.form['text']
    cfgw.write("fileSystemRoot", "SERVERCONFIG", "cfg.ini", text)
    cfgw.write("firstInit", "SERVERCONFIG", "cfg.ini", "False")
    return text

@app.route('/settings')
def settings():
    if cfgw.read("firstInit", "SERVERCONFIG", "cfg.ini") == "True":
        return redirect(url_for('fit'))
    if cfgw.read("allowSettings", "SERVERCONFIG", "cfg.ini") == "False":
        return redirect(url_for('index'))
    return render_template('settings.html')

@app.route('/settings', methods=['POST'])
def settings_post():
    text = request.form['text']
    cfgw.write("fileSystemRoot", "SERVERCONFIG", "cfg.ini", text)
    return 0
    
@app.route('/about')
def index():
    return render_template('index.html')

@app.route('/repos')
def browse():
    if cfgw.read("firstInit", "SERVERCONFIG", "cfg.ini") == "True":
        return redirect(url_for('fit'))
    itemList = os.listdir(FILE_SYSTEM_ROOT)
    return render_template('repos.html', itemList=itemList)

@app.route('/repos/<path:urlFilePath>')
def browser(urlFilePath):
    if cfgw.read("firstInit", "SERVERCONFIG", "cfg.ini") == "True":
        return redirect(url_for('fit'))
    nestedFilePath = os.path.join(FILE_SYSTEM_ROOT, urlFilePath)
    nestedFilePath = nestedFilePath.replace("/", "\\")
    if os.path.realpath(nestedFilePath) != nestedFilePath:
        return "no directory traversal please."
    if os.path.isdir(nestedFilePath):
        itemList = os.listdir(nestedFilePath)
        fileProperties = {"filepath": nestedFilePath}
        if not urlFilePath.startswith("/"):
            urlFilePath = "/" + urlFilePath
        return render_template('repos.html', urlFilePath=urlFilePath, itemList=itemList)
    if os.path.isfile(nestedFilePath):
        fileProperties = {"filepath": nestedFilePath}
        sbuf = os.fstat(os.open(nestedFilePath, os.O_RDONLY)) #Opening the file and getting metadata
        fileProperties['type'] = stat.S_IFMT(sbuf.st_mode) 
        fileProperties['mode'] = stat.S_IMODE(sbuf.st_mode) 
        fileProperties['mtime'] = sbuf.st_mtime 
        fileProperties['size'] = sbuf.st_size 
        if not urlFilePath.startswith("/"):
            urlFilePath = "/" + urlFilePath
        return render_template('file.html', currentFile=nestedFilePath, fileProperties=fileProperties)
    return 'something bad happened'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=cfgw.read("port", "SERVERCONFIG", "cfg.ini"))
