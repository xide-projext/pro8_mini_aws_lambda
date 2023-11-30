import pymysql

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
        
        # 결과 출력
        print("User_table 정보:")
        for row in user_result:
            print(f"User_Number: {row['User_Number']}")
            print(f"Nickname: {row['Nickname']}")
            print(f"ID: {row['ID']}")
            print(f"Password: {row['Password']}")
            print()

finally:
    connection.close()
