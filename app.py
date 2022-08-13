from flask import Flask, request, session, redirect, url_for, render_template, make_response, jsonify, flash
from huoZiYinShua import *
import time
from os import path, remove, listdir
from threading import Thread, Lock


#临时文件存放目录
tempOutputPath = "./tempAudioOutput/"
#进程锁
locker = Lock()
#活字印刷实例
HZYS = huoZiYinShua("./settings.json")


#生成ID
def makeid():
	id = str(int(time.time()))		#根据时间生成前缀
	queuePlace = 0		#同一秒内队列位次
	#从0开始遍历
	while True:
		#若已被占用，位次+1
		if path.exists(tempOutputPath + id + "_" + str(queuePlace) + ".wav"):
			queuePlace += 1
		#若未被占用，获取位次
		else:
			id = id + "_" + str(queuePlace)
			break
	return id



def clearCache():
	while(True):
		currentTime = int(time.time())		#当前时间
		#输出目录下的所有文件
		for fileName in listdir(tempOutputPath):
			try:		#文件名符合格式
				timeCreated = int(fileName.split("_")[0])		#创建时间
				if (currentTime - timeCreated) > 1800:			#间隔时间(秒)
					if(fileName.endswith(".wav")):
						remove(tempOutputPath + fileName)
			except:
				pass
		
		time.sleep(60)




app = Flask(__name__)


@app.route('/')
def index():
	return render_template("home.html")


@app.route('/make', methods=['POST'])
def HZYSS():
	locker.acquire()	#锁住
	rawData = request.form.get("text")
	inYsddMode = request.form.get("inYsddMode")
	inYsddMode = (inYsddMode == "true")
	try:
		#获取ID并导出音频
		id = makeid()
		HZYS.export(rawData, filePath=tempOutputPath+id+".wav", inYsddMode=inYsddMode)
		#释放并返回ID
		locker.release()
		return jsonify({"text": rawData, "id": id }), 200
	except:
		#释放并返回错误代码
		locker.release()
		return jsonify({"code": 400}), 400
	


@app.route('/<id>.wav')
def get_audio(id):
	with open(tempOutputPath+id+".wav", 'rb') as f:
		audio = f.read()
	response = make_response(audio)
	f.close()
	response.content_type = "audio/wav"
	return response


if __name__ == '__main__':
	Thread(target=clearCache, args=( )).start()
	app.run(port=8989,host='0.0.0.0')
