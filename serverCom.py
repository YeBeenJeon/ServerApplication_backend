from flask import Flask
from flask import request
from threading import Thread
from datetime import datetime
import time
import pymysql
import json

global previousSendingTime
previousSendingTime = dict()

app = Flask(__name__)

# db 연동
# pymysql.connect() -> db와 파이썬을 연결해주는 역할
with open("db.json",'r') as db:
    db_data = json.load(db)

conn = pymysql.connect(
    host=db_data['info']['host'],
    user=db_data['info']['user'],
    password=db_data['info']['password'],
    db=db_data['info']['db'],
    charset='utf8'
)

# cur(cursor) -> 커서는 db에 sql문을 실행하거나 실행된 결과를 돌려받는 통로
# conn.commit() # 확실하게 저장

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        req_data = request.args
        # print(req_data.get('time'))
        clientID = req_data.get('name')
        sendTime = req_data.get('time')
        previousSendingTime[clientID] = sendTime

        cur = conn.cursor()
        sql_register = 'insert ignore into register (id, state) values (%s, %s) on duplicate key update state="ON"'
        cur2 = conn.cursor()
        sql_insert = 'insert ignore into history (id, time) values (%s, %s)'

        cur.execute(sql_register, (clientID, 'ON')) # 처음 보낼 때 등록, OFF 되었다가 다시 전송되면 ON
        cur2.execute(sql_insert, (clientID, sendTime))
        conn.commit() # 확실하게 저장
        print('Done db insert')

    return 'Success!'

def run_server():
    app.run(debug=False)

def run_while():
    # sql_off = 'insert ignore into register (id, state) values (%s, %s) on duplicate key update state="OFF";'
    sql_off = 'UPDATE register SET state=%s WHERE id like %s'
    while(1):
        currTime = datetime.now()
        keys = list(previousSendingTime.keys())

        for key in keys:
            cur2 = conn.cursor()
            print(previousSendingTime[key])
            sendingTime = datetime.fromisoformat(previousSendingTime[key])
            diff = currTime-sendingTime
            if(diff.seconds > 30) :
                cur2.execute(sql_off, ("OFF", key))
                conn.commit()
                print(cur2.rowcount, "record(s) affected")
                print(key, "State is OFF")

        time.sleep(4) # Sleep for 3 seconds
        
if __name__ == '__main__':

    th1 = Thread(target=run_server)
    th2 = Thread(target=run_while)
    
    th1.start()
    th2.start()
    th1.join()
    th2.join()

conn.close() # 연결한 db 닫기

# 현재 8초마다 전송되고 있으니까 12초 안에 오지 않으면 연결 끊겼다고 간주
# 다시 보내면 ON이 되니까 12초 이후에 다시 전송되면 ON 상태임을 표시할 수 있음