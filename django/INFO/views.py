from django.shortcuts import render, redirect
from django.http import JsonResponse #추가
import pymysql, logging
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout


# Create your views here.

logger = logging.getLogger(__name__)

def index(request):
    user_id = request.session.get('userid')
    user_password = request.session.get('userpassword')
    if not (user_id and user_password):
        return redirect('login')
    #return render(request, 'INFOtemp/index.html')
    return render(request, 'INFOtemp/index.html', {'user_id': user_id, 'user_password': user_password})
    
def login(request):
    return render(request, 'login/login.html')

def list(request):
    return render(request, 'list/list.html')

def list2(request):
    user_id = request.session.get('userid')
    user_password = request.session.get('userpassword')
    print(user_id)
    print(user_password)
    # 세션에 사용자 정보가 없으면 로그인 페이지로 리디렉션
    if not (user_id and user_password):
        return redirect('login')

    # 여기에 사용자 정보를 활용한 작업 수행
    # ...
    return render(request, 'list/list2.html', {'user_id': user_id, 'user_password': user_password})

def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_protect
def Insert_into_table(request):
    logger.info(request.method)
    
    if request.method == 'POST':
        nickname = request.POST.get('Nickname')
        user_id = request.POST.get('ID')
        passwd = request.POST.get('Password')
        
        logger.info(f"Received data - Nickname: {nickname}, ID: {user_id}")

        # 파라미터화된 쿼리 사용
        sql = "INSERT INTO User_table (Nickname, ID, Password) VALUES (%s, %s, password(%s))"
        params = (nickname, user_id, passwd)

        database_settings = settings.DATABASES
        mysql_settings = database_settings['default']
        NAME = mysql_settings['NAME']
        USER =  mysql_settings['USER']
        PASSWORD =  mysql_settings['PASSWORD']
        HOST =  mysql_settings['HOST']

        try:
            # MySQL 연결 및 데이터베이스에 데이터 삽입
            with pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=NAME, charset='utf8') as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    conn.commit()

            return JsonResponse({'message': 'Data inserted successfully'})
        except Exception as e:
            # 예외 처리: 데이터 삽입 실패 시
            logger.error(f'Error: {str(e)}')
            return JsonResponse({'error': 'Failed to insert data'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('ID')
        password = request.POST.get('Password')
        # RDS에 직접 연결
        database_settings = settings.DATABASES
        mysql_settings = database_settings['default']
        NAME = mysql_settings['NAME']
        USER = mysql_settings['USER']
        PASSWORD = mysql_settings['PASSWORD']
        HOST = mysql_settings['HOST']

        conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=NAME, charset='utf8')
        cursor = conn.cursor()

        try:
            # 사용자 정보 대조 쿼리
            sql = f"SELECT * FROM User_table WHERE ID = '{user_id}' AND Password = password('{password}')"
            cursor.execute(sql)
            result = cursor.fetchone()
#---------기존코드 있던자리
            if result:
                print(result)
                # 사용자 정보를 기반으로 세션에 저장
                request.session['userid'] = result[2]
                request.session['userpassword'] = result[3]
                print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
                return redirect('list2')
            else:
                return JsonResponse({'error': '사용자명 또는 비밀번호가 잘못되었습니다.'}, status=400)
        except Exception as e:
            # 예외 처리
            logger.error(f"Error connecting to RDS: {str(e)}")
            return JsonResponse({'error': '서버 오류가 발생했습니다.'}, status=500)
        finally:
            # 연결 종료
            conn.close()
    return render(request, 'login/login.html')

