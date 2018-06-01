# #include <stdint.h>
# struct ProtocolHeader {
# uint8_t m_sync;
# uint8_t m_version;
# uint16_t m_number;
# uint32_t m_length;
# uint16_t m_type;
# uint8_t m_reserved[6];
# };

import struct
import json
import datetime
import time
import driver.seerAgv.roboKit as roboKit

g_demoSendData = dict()
f2002 = {"x": 10.0, "y": 3.0, "angle": 0}
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
f3051 = {"id":"S03", "x": 10.0, "y": 3.0, "max_speed": 0, "max_wspeed": 0, "max_acc": 0, "angle": 0, "max_wacc": 0}
f3052 = {"route":"route03", "loop": 10}


g_demoSendData['2002'] = f2002


def assembleData(code):
	global g_demoSendData
	data = None
	bodyData = None
	dataLen = 0
	if code in g_demoSendData:
		data = g_demoSendData[code]
	if data is not None:
		dataLen = len(data)
		bodyData = json.dumps(data).encode("GBK")
	codeNum = int(code)
	sendObj = roboKit.protocolHeader(90, 1, 0, dataLen, codeNum, 0, 0)
	# sendObj= roboKit.protocolHeader(90,1,0,0,1000,0,0)

	headData = sendObj.getsturct()
	sendData = headData + bodyData
	return sendData


def sendData(data):
	client1 = roboKit.robotClient()
	client1.connect('10.10.105.184', 19204)
	i = 0
	while i < 100:
		result = client1.send(data)
		print(result)
		i += 1
		time.sleep(5)
	client1.disconnect()


def test_sendMsg():
	data1 = assembleData('2002')
	assert data1
	sendData(data1)


def test_timeout():
	data1 = assembleData('2002')
	assert data1
	client1 = roboKit.robotClient()
	client1.connect('10.10.105.184', 19204)
	i = 0
	while i < 100:
		startTime = datetime.datetime.now()
		result = client1.send(data1)
		if result == -1:
			endTime = datetime.datetime.now()
			span = endTime - startTime
			assert span < datetime.timedelta(seconds=11)
			assert span > datetime.timedelta(seconds=9)
		print(result)
		i += 1
		time.sleep(5)
	client1.disconnect()


def test_reconnect():
	data1 = assembleData('2002')
	assert data1
	client1 = roboKit.robotClient()
	client1.connect('10.10.105.184', 19204)
	i = 0
	while i < 100:
		startTime = datetime.datetime.now()
		result = client1.send(data1)
		if result == -2:
			endTime = datetime.datetime.now()
			span = endTime - startTime
			assert span < datetime.timedelta(seconds=6)
			assert span > datetime.timedelta(seconds=4)
		print(result)
		i += 1
		time.sleep(5)
	client1.disconnect()


if __name__ == '__main__':
	test_sendMsg()
