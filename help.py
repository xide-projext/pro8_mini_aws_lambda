from flask import Flask, render_template
import pymysql

app = Flask(__name__, template_folder='/home/cjy/pro8_mini_aws_lambda') 

@app.route('/')
def index():
    # 데이터베이스에서 값을 가져오는 로직
    connection = pymysql.connect(
        host='mini-lambda.cdeb8y0dqokw.ap-northeast-2.rds.amazonaws.com',
        user='admin',
        password='didwn123',
        database='User_Quiz',
        charset='utf8mb4',  
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Quiz_table"  # your_table_name을 실제 테이블 이름으로 변경
            cursor.execute(sql)
            result = cursor.fetchall()
            items = [row['Quizname'] for row in result]  # column_name을 실제 컬럼 이름으로 변경
            return render_template('index.html', items=items)
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
