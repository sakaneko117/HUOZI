from flask import Flask, request, render_template, make_response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from huoZiYinShua import *
import time
from os import path, remove, listdir
from threading import Thread, Lock
import logging



#临时文件存放目录
tempOutputPath = "./tempAudioOutput/"
#进程锁
locker = Lock()




#启动日志
hzysLogger = logging.getLogger()
hzysFileHandler = logging.FileHandler("record.log", encoding="utf8", mode="a")
hzysFormatter = logging.Formatter("%(asctime)s, %(message)s")
hzysFileHandler.setFormatter(hzysFormatter)
hzysLogger.addHandler(hzysFileHandler)
hzysLogger.setLevel(logging.DEBUG)



#生成ID
def makeid():
	id = str(int(time.time()))		#根据时间生成前缀
	queuePlace = 0					#同一秒内队列位次
	#从0开始遍历
	while True:
		#若已被占用，位次+1
		if path.exists(tempOutputPath + id + "_" + str(queuePlace) + ".hamood"):
			queuePlace += 1
		#若未被占用，获取位次
		else:
			id = id + "_" + str(queuePlace) + "_" + request.remote_addr
			break
	return id



#清理临时文件
def clearCache():
	while(True):
		currentTime = int(time.time())		#当前时间
		#输出目录下的所有文件
		for fileName in listdir(tempOutputPath):
			#文件名符合格式
			try:
				timeCreated = int(fileName.split("_")[0])		#创建时间
				if (currentTime - timeCreated) > 1800:			#间隔时间(秒)
					if fileName.endswith(".wav") or fileName.endswith(".hamood"):
						remove(tempOutputPath + fileName)
			#若文件名不符合格式，(currentTime - timeCreated)会报错
			except:
				pass
		
		time.sleep(60)



#----------------------------------------------------
#核心代码
#----------------------------------------------------


app = Flask(__name__)
#限制访问
limiter = Limiter(app, key_func=get_remote_address, default_limits=["6 per minute"])



@app.route('/')
@limiter.limit("30 per minute")
def index():
	return render_template("home.html")



#用户发出生成音频的请求
@app.route('/make', methods=['POST'])
def HZYSS():
	rawData = request.form.get("text")				#获取文本
	inYsddMode = request.form.get("inYsddMode")		#是否使用原声大碟模式
	inYsddMode = (inYsddMode == "true")
	app.logger.debug("%s", request.form)			#记录日志
	#如果文本过长，不予生成音频并返回错误代码
	if len(rawData) > 100:
		return jsonify({"code": 400, "message": "憋刷辣！"}), 200
	locker.acquire()								#锁住
	try:
		#获取ID
		id = makeid()
		#新建占位文件
		placeHolderFile = open(tempOutputPath+id+".hamood", mode="w")
		placeHolderFile.close()
		#解锁
		locker.release()
		#活字印刷实例
		HZYS = huoZiYinShua("./settings.json")
		#导出音频
		HZYS.export(rawData, filePath=tempOutputPath+id+".wav", inYsddMode=inYsddMode)
		#返回ID
		return jsonify({"code": 200, "id": id}), 200
	except:
		#解锁并返回错误代码
		locker.release()
		return jsonify({"code": 400, "message": "生成失败"}), 200
	


#用户发出下载音频的请求
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
