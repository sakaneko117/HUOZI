from flask import Flask, request, session, redirect, url_for, render_template, make_response, jsonify, flash
from huoZiYinShua import *

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("home.html")


@app.route('/make', methods=['POST'])
def HZYSS():
    HZYS = huoZiYinShua("/home/ubuntu/HUOZI/sources/", "/home/ubuntu/HUOZI/dictionary.csv")
    rawData = request.form.get("text")
   # print(rawData)
    #filepath = HZYS.export(rawData)
    try: id = HZYS.export(rawData)
    except:return jsonify({"code": 400}), 400
    return jsonify({"text": rawData, "id": id }), 200


@app.route('/<id>.wav')
def get_audio(id):
    with open('/home/ubuntu/HUOZI/{}.wav'.format(id), 'rb') as f:
        audio = f.read()
    response = make_response(audio)
    response.content_type = "audio/wav"
    return response


if __name__ == '__main__':
    app.run(port=8989,host='0.0.0.0')
