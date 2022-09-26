from flask import Flask
from flask import request
from threading import Thread
import time
import pymysql

global m, id, cpu_usage, user_num
m = list()
id = list()
cpu_usage = list()
user_num = list()

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
#cur = conn.cursor()
#sql_select = 'select time from history'
#cur.execute(sql_select)
#
#for row in cur:
#    print(row)
    
    
# sql_insert = 'insert into history (name, time) values (%s, %s)'
#if len(m) != 0 :
#    cur.execute(sql_insert, ('t12', m))
#    conn.commit() # 확실하게 저장



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        req_data = request.args
        # print(req_data.get('time'))
        id.append(req_data.get('id'))
        m.append(req_data.get('time'))
        cpu_usage.append(req_data.get('cpu_usage'))
        user_num.append(req_data.get('user_num'))
        

        # print(req_data.get('name'))
        # print(req_data.get('state'))
        # print(req_data.get('info'))

    return 'Success!'

def run_server():
    app.run(debug=False)

def run_while():
    
#    name_inDB = list()
#    for row in cur:
#        name_inDB.append(row[0])
#        print('name in DB', name_inDB)
    
    cur = conn.cursor()
    sql_register = 'insert ignore into register (id, state) values (%s, %s) on duplicate key update state="ON"'
    
    cur2 = conn.cursor()
    sql_insert = 'insert ignore into history (id, time, cpu_usage, user_num) values (%s, %s, %s, %s)'
    
    while(1):
        # print('while')
        print(m)
        print(cpu_usage)
        # print(len(m))
        list_len = len(m)
#        cpu_len = len(cpu_usage)
#        user_len = len(user_num)

        if list_len > 0:
            print('m element: ', m[list_len-1])
            print('user_num element: ', user_num[list_len-1])
            cur.execute(sql_register, (id[list_len-1], 'ON')) # 처음 보낼 때 등록, OFF 되었다가 다시 전송되면 ON
            cur2.execute(sql_insert, (id[list_len-1], m[list_len-1], cpu_usage[list_len-1], user_num[list_len-1]))
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
