from flask import Flask, request, session, redirect, url_for, render_template, make_response, jsonify, flash
from huoZiYinShua import *
import json
import time
from random import randint

app = Flask(__name__)


def makeid():
    id = str(int(time.time()))
    id += str(randint(0, 99))
    return id




@app.route('/')
def index():
    return render_template("home.html")


@app.route('/make', methods=['POST'])
def HZYSS():
    configFile = open("./settings.json", encoding="utf8")
    configurations = json.load(configFile)
    configFile.close()
    HZYS = huoZiYinShua(configurations)
    rawData = request.form.get("text")
    try:
        id = makeid()
        HZYS.export(rawData, "./{}.wav".format(id))
    except:return jsonify({"code": 400}), 400
    return jsonify({"text": rawData, "id": id }), 200


@app.route('/<id>.wav')
def get_audio(id):
    with open('./{}.wav'.format(id), 'rb') as f:
        audio = f.read()
    response = make_response(audio)
    response.content_type = "audio/wav"
    return response


if __name__ == '__main__':
    app.run(port=8989,host='0.0.0.0')
