import requests
import schedule
import time
import os

url = "http://127.0.0.1:5000"

# cpu load : cpu에 실행중이거나 대기중인 작업의 개수를 평균으로 보여주는 값
# workload : 주어진 기간에 시스템에 의해 실행되어야 할 작업의 할당량
# 명령어 - uptime, top,
info = os.popen('top').read(505)
line = info.split('\n')

info_str = ''
for i in range(len(line)):
	info_str += line[i]
	if i < len(line)-1:
		info_str += '\n'
	
print(info_str);

def sending():
	date = os.popen('date "+%Y-%m-%d %H:%M:%S"').read().split('\n')[0]
 
	on_datas = {
		'name' : '10',
		'time' : date,
		'state' : 'on',
		'info' : info_str,
	}

	
	response = requests.get(url, params=on_datas)
	
	if response.status_code == 200: 
		print(response.url);

schedule.every(8).seconds.do(sending)
# schedule.every(3).minutes.do(sending)

try:
	while True:
		schedule.run_pending()
		# time.sleep(1)
except KeyboardInterrupt:
	end_time = os.popen('date "+%Y-%m-%d %H:%M:%S"').read().split('\n')[0]
	off_datas = {
		'name' : '10',
		'time' : end_time,
		'state' : 'off',
		'info' : info_str,
	}
	response = requests.get(url, params=off_datas)
