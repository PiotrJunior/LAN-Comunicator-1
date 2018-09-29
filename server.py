import time
import socket
import threading
import os, signal

IP = '192.168.42.195'
TEXT_PORT = 1255
FILE_PORT = 3461
BUFFER_SIZE = 8192

textSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fileSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connList = []

class User:
	def __init__(self,connT,addrT,connF,addrF):
		self.textConnection = connT
		self.textAdres = addrT
		self.fileConnection = connF
		self.fileAdres = addrF
	def setUsername(self,un):
		self.username = un

def msgServer():
	while True:
		msg = input()
		if msg == ':q':
			textSocket.close()
			fileSocket.close()
			os.system("clear")
			os.kill(os.getpid(), signal.SIGUSR1)
			os._exit(1)
		else:
			for x in connList:
				x.textConnection.send( ("Server~Server~" + time.strftime("%H:%M:%S") + "~" + msg.rstrip()).encode("utf-8") )

def initServer():
	try:
		textSocket.bind((IP,TEXT_PORT))
	except socket.error as e:
		print("Text: " + str(e))

	try:
		fileSocket.bind((IP,FILE_PORT))
	except socket.error as e:
		print("File: " + str(e))

	threadMsgServer = threading.Thread( target = msgServer )
	threadMsgServer.start()
	textSocket.listen(5)
	fileSocket.listen(5)
	print("Ready")


def clientThread(chatUser):
	print( chatUser.textAdres[0], "Connected!" )
	userNick = chatUser.textConnection.recv(BUFFER_SIZE).decode("utf-8").rstrip()
	chatUser.setUsername(userNick)
	print("Username", chatUser.username)
	for x in connList:
		x.textConnection.send( (chatUser.textAdres[0]+ "~" + time.strftime("%H:%M:%S") + "~User " + chatUser.username + " entered the chatroom" ).encode("utf-8") )
	SHEARED = -1
	while True:
		data = chatUser.textConnection.recv(BUFFER_SIZE).decode("utf-8").rstrip()
		if not data:
			for x in connList:
				x.textConnection.send( (chatUser.textAdres[0]+ "~" + time.strftime("%H:%M:%S") + "~User " + chatUser.username + " disconnected").encode("utf-8") )
			print("[" + chatUser.textAdres[0] + "] " + chatUser.username + " Disconnected")
			connList.remove(chatUser)
			chatUser.textConnection.close()
			break
		print( chatUser.textAdres[0] + '~' + chatUser.username + ":", data )
		for x in connList:
			x.textConnection.send( (chatUser.textAdres[0] + '~' + time.strftime("%H:%M:%S") + "~" + chatUser.username + "~: " + data).encode("utf-8") )


def filesThread(chatUser):
	while True:
		data = chatUser.fileConnection.recv(BUFFER_SIZE)
		#print( data.decode("utf-8") )
		for x in connList:
			print("SENDING")
			x.fileConnection.send( data )


initServer()
while True:
	connT, addrT = textSocket.accept()
	connF, addrF = fileSocket.accept()
	newUser = User(connT,addrT,connF,addrF)
	#print(str(connT)+str(addrT)+str(connF)+str(addrF))
	connList.append(newUser)
	t1 = threading.Thread( target = clientThread, args = [newUser] )
	t2 = threading.Thread( target = filesThread, args = [newUser] )
	t1.start()
	t2.start()
