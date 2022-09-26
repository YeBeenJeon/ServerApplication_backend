from flask import Flask
from flask import request
from threading import Thread
import time
import pymysql

global m, name
name = list()
m = list()

app = Flask(__name__)

# db 연동
# pymysql.connect() -> db와 파이썬을 연결해주는 역할
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='1q2w3e8255',
    db='http_data',
    charset='utf8'
)

# cur(cursor) -> 커서는 db에 sql문을 실행하거나 실행된 결과를 돌려받는 통로
# conn.commit() # 확실하게 저장

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        req_data = request.args
        # print(req_data.get('time'))
        name.append(req_data.get('name'))
        m.append(req_data.get('time'))

        # print(req_data.get('name'))
        # print(req_data.get('state'))
        # print(req_data.get('info'))

    return 'Success!'

def run_server():
    app.run(debug=False)

def run_while():
    
    cur = conn.cursor()
    sql_register = 'insert ignore into register (id, state) values (%s, %s) on duplicate key update state="ON"'
    
    cur2 = conn.cursor()
    sql_insert = 'insert ignore into history (id, time) values (%s, %s)'
    
    while(1):
        print(m)
        print(len(m))
        list_len = len(m)

        if list_len > 0:
            print('m element: ', m[list_len-1])
            cur.execute(sql_register, (name[list_len-1], 'ON')) # 처음 보낼 때 등록, OFF 되었다가 다시 전송되면 ON
            cur2.execute(sql_insert, (name[list_len-1], m[list_len-1]))
            conn.commit() # 확실하게 저장
            print('insert')
        
        time.sleep(2) # Sleep for 3 seconds
        
if __name__ == '__main__':
    # m = list()
    th1 = Thread(target=run_server)
    th2 = Thread(target=run_while)
    
    th1.start()
    th2.start()
    th1.join()
    th2.join()

    # print(f"Result: {sum(result)}")
conn.close() # 연결한 db 닫기

# 현재 8초마다 전송되고 있으니까 12초 안에 오지 않으면 연결 끊겼다고 간주
# 다시 보내면 ON이 되니까 12초 이후에 다시 전송되면 ON 상태임을 표시할 수 있음
