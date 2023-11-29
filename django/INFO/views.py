from django.shortcuts import render, redirect
from django.http import HttpResponse #추가
from django.db import connection     #추가
import pymysql  
from django.conf import settings
import logging
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse

# Create your views here.

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'INFOtemp/index.html')

def login(request):
    return render(request, 'login/login.html')

def list(request):
    return render(request, 'list/list.html')


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
        #settings 에서 값을 가져오도록 설정함
        #settings 설정 필수!!
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

