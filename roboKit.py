import socket
import time
import threading
import json
import struct



class protocolHeader(object):
	def __init__(self, m_sync,m_version,m_number,m_length,m_type,m_reserved,m_reserved2):
		self.m_sync = m_sync
		self.m_version = m_version
		self.m_number = m_number
		self.m_length = m_length
		self.m_type = m_type
		self.m_reserved = m_reserved
		self.m_reserved2 = m_reserved2


	def getsturct(self):
		structed= struct.pack('>BBHIHIH', self.m_sync, self.m_version, self.m_number, self.m_length,self.m_type,self.m_reserved,self.m_reserved2)
		return structed


class baseResultData(object):
	def __init__(self, ret_code,err_msg):
		self.ret_code = ret_code
		self.err_msg = err_msg

	def getdict(self):
		dict = {}
		dict.update(self.__dict__)
		return dict






# 1000 robot_status_info_req 查询机器人信息
# 1002 robot_status_run_req 查询机器人的运行状态信息(如运行时间、里程等)
# 1003 robot_status_mode_req 查询机器人运行模式
# 1004 robot_status_loc_req 查询机器人位置
# 1005 robot_status_speed_req 查询机器人速度
# 1006 robot_status_block_req 查询机器人被阻挡状态
t1000 = {"id": "S001", "version": "v1.1.0", "model": "S1", "dsp_version": "v1.2.2", "map_version": "v1.0.0","model_version": "v1.1.0", "netprotocol_version": "v1.2.0"}
t1002={"odo": 0,"time": 6.0,"total_time": 2.0,"controller_temp": 1.57,"controller_humi": 0.9,"controller_voltage": 0.9}
t1003={"mode": 0}
t1004={"x": 6.0,"y": 2.0,"angle": 1.57,"confidence": 0.9}
t1005={"vx": 6.0,"vy": 2.0,"w": 1.57}
t1006={"blocked": 6.0,"block_reason": 2.0,"block_x": 1.57,"block_y": 0.9,"block_di": 0.9,"block_ultrasonic_id": 0.9}

# 2000 robot_control_stop_req 停止运动
# 2001 robot_control_gyrocal_req 标定陀螺仪
# 2002 robot_control_reloc_req 重定位
# 2003 robot_control_comfirmloc_req 确认定位正确

# 3051 robot_task_gotarget_req 固定路径导航(根据地图上站点及固定路径导航)
# 3052 robot_task_patrol_req 巡检(设定路线进行固定路径导航)
# 3057 robot_task_gostart_req 去起始点
# 3058 robot_task_goend_req 去终止点
# 3059 robot_task_gowait_req 去待命点
# 3060 robot_task_charge_req 去充电

basedata=baseResultData(0,"success").getdict()

demoDict=dict()
demoDict['11000']=dict(basedata,**t1000)
demoDict['11002']=dict(basedata,**t1002)
demoDict['11003']=dict(basedata,**t1003)
demoDict['11004']=dict(basedata,**t1004)
demoDict['11005']=dict(basedata,**t1005)
demoDict['11006']=dict(basedata,**t1006)
demoDict['12000']=dict(basedata)
demoDict['12002']=dict(basedata)
demoDict['12003']=dict(basedata)
demoDict['12001']=dict(basedata)
demoDict['13051']=dict(basedata)
demoDict['13052']=dict(basedata)
demoDict['13058']=dict(basedata)
demoDict['13059']=dict(basedata)
demoDict['13060']=dict(basedata)
demoDict['13057']=dict(basedata)


def action(index, bodyResult):
	print('using function type is:%s' % index)
	print('deling with params of:%s' % bodyResult)


class robotServer:
	def __init__(self, IP, port):
		self.address = IP
		self.port = port
		self.sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def dataHandler(self, client, addr):
		try:
			while True:
				client.settimeout(10)
				recvData = client.recv(1024)
				# print("recvData: ", recvData)
				if len(recvData) < 16:
					return
				headerRaw=recvData[0:16]
				bodyResult = recvData[17:]
				header=None
				headerResult = struct.unpack('>BBHIHIH',headerRaw)

				index=0
				data=None
				if len(headerResult) >= 6:
					m_sync = headerResult[0]
					m_version = headerResult[1]
					m_number = headerResult[2]
					m_length = headerResult[3]
					m_type = headerResult[4]
					m_reserved = headerResult[5]
					m_reserved2 = headerResult[6]
					header=protocolHeader(m_sync,m_version,m_number,m_length,m_type,m_reserved,m_reserved2)

					index="1"+m_type.__str__()

					data= demoDict[index]

					action(index, bodyResult)

				if data is not None:
					jsonData=json.dumps(data)
					jsonLen = len(jsonData)
					bodyData = jsonData.encode("GBK")
					header.m_length=jsonLen
					header.m_type= int(index)
					headerData= header.getsturct()
					result= headerData+bodyData
					client.send(result)
					print('data has been sent')

				else:
					print('no data has been sent')
		except socket.timeout:
			print("socket time out,do reconnect ")
			client.close()
		except socket.error:
			print("socket error,do reconnect ")
			client.close()
		except:
			print("other error occur ")
			client.close()

	def start(self):

		self.sock.bind((self.address, self.port))
		self.sock.listen(50)
		while True:
			client, address =self.sock.accept()
			thread = threading.Thread(target=self.dataHandler, args=(client, address))
			thread.start()
			print('server started!')

	def end(self):
		self.sock.close()
		print('server ended!')


class robotClient:
	def __init__(self):
		self.tcpClientSocket=None
		self.serverAddr=None


	def __connect(self, serverAddr):
		while True:
			try:
				if  serverAddr is None:
					return
				self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				print('socket---%s' % self.tcpClientSocket)
				# 链接服务器
				self.tcpClientSocket.connect(serverAddr)
				print('connect success!')
				return
			except socket.error:
				print("socket error,do reconnect ")
				time.sleep(3)
				self.__connect(self.serverAddr)

	def connect(self, server, port):
		self.serverAddr = (server, port)
		self.__connect(self.serverAddr)

	def send(self,sendData):
		while True:
			try:
				if len(sendData) > 0:
					self.tcpClientSocket.send(sendData)
				else:
					return
					# 接收数据
				self.tcpClientSocket.settimeout(10)
				recvData = self.tcpClientSocket.recv(1024)
				# 打印接收到的数据
				print('the receive message is:%s' % recvData)
				headerData = recvData[0:15]
				bodyData= recvData[16:]
				print('header is:%s' % headerData)
				print('body is:%s' % bodyData)
				return bodyData

			except socket.timeout:
				print("socket time out,do reconnect ")
				self.tcpClientSocket.close()
				return -1

			except socket.error as err:
				print("socket error,do reconnect ")
				time.sleep(3)
				print(err)
				self.__connect(self.serverAddr)
				return -2

			except:
				print("other error occur ")
				time.sleep(3)
				return -3

	def disconnect(self):
		# 关闭套接字
		self.tcpClientSocket.close()
		print('close socket!')

def test_protocolHeader():
	t1 = {"x": 10.0, "y": 3.0, "angle": 0}
	dataLen= len(t1)
	m_version = 1
	m_number = 0
	m_sync = 90
	m_type = 1000
	m_reserved = 0
	m_reserved2 = 0
	bodyData = json.dumps(t1).encode("GBK")
	dataLen=int(dataLen)
	sendObj= protocolHeader(m_sync,m_version,m_number,dataLen,m_type,m_reserved,m_reserved2)
	result= sendObj.getsturct()
	assert result
	unpacked= struct.unpack('>BBHIHIH', result)
	assert m_sync == unpacked[0]
	assert m_version == unpacked[1]
	assert m_number == unpacked[2]
	assert dataLen == unpacked[3]
	assert m_type == unpacked[4]
	assert m_reserved == unpacked[5]
	assert m_reserved2 == unpacked[6]
	assert sendObj

def test_robotserver():
	server = robotServer('10.10.105.184', 19204)
	server.start()

def test_robotclient():
	client1= robotClient()
	client1.connect('10.10.105.184', 19204)

	data = {"x": 10.0, "y": 3.0, "angle": 0}  # 发送数据
	sendData = json.dumps(data).encode()
	client1.send(sendData)
	client1.disconnect()

if __name__ == '__main__':

	thread1 = threading.Thread(target=test_robotserver)
	thread1.start()
	test_protocolHeader()
	# while(True):
	#
	# 	thread2 = threading.Thread(target=test_robotclient)
	# 	thread2.start()
	#
	# 	time.sleep(3)


