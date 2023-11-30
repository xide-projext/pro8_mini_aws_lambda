from flask import Flask, render_template
import pymysql

app = Flask(__name__, template_folder='/home/cjy/pro8_mini_aws_lambda')

@app.route('/')
def display_users():
    # MySQL 데이터베이스에 연결
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
            # User_table 정보 출력 쿼리
            select_user_query = "SELECT * FROM User_table"
            
            # 쿼리 실행
            cursor.execute(select_user_query)
            
            # User_table 결과 가져오기
            user_result = cursor.fetchall()

            # HTML 템플릿 렌더링
            return render_template('users.html', users=user_result)

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
