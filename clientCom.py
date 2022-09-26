import requests
import schedule
import os
import pymysql
import json

# 암호화/복호화 모듈 사용
import base64

from Cryptodome import Random
from Cryptodome.Cipher import AES

from Cryptodome import Random
from Cryptodome.Cipher import AES

BS = 16
pad = lambda s: s + (BS - len(s.encode('utf-8')) % BS) * chr(BS - len(s.encode('utf-8')) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]

key = [0x10, 0x01, 0x15, 0x1B, 0xA1, 0x11, 0x57, 0x72, 0x6C, 0x21, 0x56, 0x57, 0x62, 0x16, 0x05, 0x3D, 0xFF, 0xFE, 0x11, 0x1B, 0x21, 0x31, 0x57, 0x72, 0x6B, 0x21, 0xA6, 0xA7, 0x6E, 0xE6, 0xE5, 0x3F]

class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw.encode('utf-8') ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))

with open("db.json",'r') as db:
    db_data = json.load(db)
        
conn = pymysql.connect(
    host=db_data['info']['host'],
    user=db_data['info']['user'],
    password=db_data['info']['password'],
    db=db_data['info']['db'],
    charset='utf8'
)

url = "http://127.0.0.1:5000"

# cpu load : cpu에 실행중이거나 대기중인 작업의 개수를 평균으로 보여주는 값
# workload : 주어진 기간에 시스템에 의해 실행되어야 할 작업의 할당량
# 명령어 - uptime, top


#info_str = ''
#for i in range(len(line)):
#	info_str += line[i]
#	if i < len(line)-1:
#		info_str += '\n'
#
#print(info_str)

def sending():
    uptime = os.popen('uptime').read()
    line = uptime.split(', ')
    # print(line[2][0]) # user number

    top = os.popen('top').read(200)
    # print('user index: ', top.find('idle'))
    line2 = top.split('\n')
    # print(line2)
    cpu = line2[3].split(' ')
    print('cpu_user: ', cpu[2])
    print('cpu_sys: ', cpu[4])
    
    cpu_user = cpu[2].split(' ')
    cpu_sys = cpu[4].split(' ')
    # print(cpu_user[0].split('%')[0])
    # print(cpu_sys[0].split('%')[0])
    
    cpuUser_float = float(cpu_user[0].split('%')[0])
    cpuSys_float = float(cpu_sys[0].split('%')[0])
    
    total_cpu = str(round((cpuUser_float + cpuSys_float), 2)) + '%'

    # print(type(total_cpu))
    print('total_cpu: ', total_cpu)
    
    date = os.popen('date "+%Y-%m-%d %H:%M:%S"').read().split('\n')[0]
    
    on_datas = {
		'id' : '10',
		'time' : date,
		'state' : 'on',
        'cpu_usage' : total_cpu,
		'user_num' : line[2][0],
	}
 
    response = requests.get(url, params=on_datas)
    
    if response.status_code == 200:
        print(response.url);

schedule.every(8).seconds.do(sending)
# schedule.every(3).minutes.do(sending)

try:
    check = 0; # 0 : id no exist, 1 : id exist
    try: # 파일에 id가 저장되어 있으면
        f = open('save_id.txt', 'rb') # 파일에 있는 id 불러오기
        file_id = f.read()
        
        id_dec = AESCipher(bytes(key)).decrypt(file_id) # 불러온 id 복호화
        dec_str = id_dec.decode('utf-8') # 바이트 형태를 string으로
        # print(dec_str)
        
        print('id를 자동으로 불러옵니다.')
        print('id : ' + dec_str)
        id = dec_str
        
        f.close()
        check = 1
    except:
        # print('no file')

        id = input("Client id 입력 : ")
        
        cur = conn.cursor()
        sql_select = 'select id from register'
        cur.execute(sql_select)
        
        for row in cur:
            # print("row: ", row[0])
            if row[0] == id: # db에 입력한 id가 있으면
                check = 1
                break
            else:
                check = 0
                
    # print("check: ", check);
    if(check == 1):
        print("'" + id + "'", "id로 접속 완료!")
    
        id_enc = AESCipher(bytes(key)).encrypt(id) # 암호화
        # print(id_enc)

        f = open('save_id.txt', 'wb') # 암호화 한 것 파일에 쓰기
        f.write(id_enc)

        f.close()
        while True:
            schedule.run_pending()
            # time.sleep(1)
    else:
        print("입력한 id는 등록이 되어 있지 않은 id입니다.\nWeb Server에서 등록 후 이용해주세요!")
except KeyboardInterrupt:
    end_time = os.popen('date "+%Y-%m-%d %H:%M:%S"').read().split('\n')[0]
    off_datas = {
        'id' : '10',
        'time' : end_time,
        'state' : 'off',
        # 'user_num' : line[2][0],
    }
    response = requests.get(url, params=off_datas)

# 새로 등록하면 접속 완료 됐을 때 새로운 텍스트 파일 만들어 줌
# 만들어진 텍스트 파일에는 id가 암호화되어 저장

# 텍스트 파일 있으면 등록된 id가 있다고 알려주기
# id를 복호화하여 불러와줌
# 불러온 id를 가지고 데이터 전송

