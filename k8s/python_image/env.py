import os
import base64

# 특정 환경변수의 값을 가져오기
encoded_code = os.environ.get('PYCODE')

# 값 디코딩
decoded_code = base64.b64decode(encoded_code).decode()

# 디코딩된 코드를 파일에 쓰기
with open("/app/test.py", "w+") as fw:
    fw.write(decoded_code)