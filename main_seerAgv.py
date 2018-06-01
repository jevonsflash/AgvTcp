import driver.seerAgv.roboKit as roboKit
import  json
if __name__ == '__main__':
	server = roboKit.robotServer('127.0.0.1', 19204)
	server.start()
	client1= roboKit.robotClient()
	client1.connect('127.0.0.1', 19204)
	data = {"x": 10.0, "y": 3.0, "angle": 0}  # 发送数据
	sendData = json.dumps(data).encode()
	client1.send(sendData)
	client1.send(sendData)
	client1.disconnect()