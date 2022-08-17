from os import path, remove, listdir

tempOutputPath = "./tempAudioOutput/"

confirmMessage = input("此程序将清理所有临时文件\n输入“confirm”以继续：")
if confirmMessage != "confirm":
	exit()

for fileName in listdir(tempOutputPath):
	if fileName.endswith(".wav") or fileName.endswith(".hamood"):
		remove(tempOutputPath + fileName)
print("清理完成")