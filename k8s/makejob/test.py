import json
import base64
import subprocess
import threading
from k8s import get_job_logs, plzcleanup
from jinja2 import Template

iden= "test"

image = "031717690025.dkr.ecr.ap-northeast-2.amazonaws.com/python:latest"

code = '''
def main(value, num):
    val = str(value) + str(num)
    print(val)
    return val*2
'''

def get_job_pod_names(job_name):
    try:
        # kubectl 명령어 실행하고 표준 출력 캡처
        cmd = f'kubectl get pods --selector=job-name={job_name} --output=name'
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True)

        # 결과 반환
        return result.stdout.strip().split('\n')

    except subprocess.CalledProcessError as e:
        # 명령어 실행 중 오류가 발생한 경우 처리
        print(f"Error: {e}")
        return []

def get_job_logs2(iden):
    pods = get_job_pod_names(iden)
    logs = []
    for num, pod in enumerate(pods):
            cmd = ["kubectl", "logs", pod, "-c", f"my-container-{num+1}"]
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)
            logs.append(result.stdout)
    return logs
    #return subprocess.check_output(["kubectl", "logs", f"job/{iden}"], text=True)

# 예시로 주어진 환경변수 리스트
GAVE_ENV = '[["value","1"],["value","2"],["value","3"],["value", "4"]]'
ENV = '["value1", "value2", "value3", "value4"]'  # 나와야하는 답
encoded_code = base64.b64encode(code.encode()).decode()
GAVE_JSON = json.loads(GAVE_ENV)
ENV_JSON = json.loads(ENV)

with open("./01.j2", "r") as fr :
    job_template = fr.read()

template = Template(job_template)

tmp = template.render(iden=iden,num_pods=len(ENV_JSON))

with open("./02.j2", "r") as fr :
    pod_template = fr.read()

with open("./03.j2", "r") as fr :
    env_template = fr.read()

template = Template(pod_template)
template2 = Template(env_template)

for idx, env in enumerate(GAVE_JSON) :
    tmp += "\n" + template.render(idx=idx, image=image)
    tmp += "\n" + template2.render(args_name = "PYCODE", env_var=encoded_code)
    tmp += "\n" + template2.render(args_name = "ARGS_COUNT", env_var=len(env))
    tmp += "\n" + template2.render(args_name= "ARGS", env_var=env)

print(tmp)  # 생성된 YAML 출력 (이 부분은 실제로 K8s에 제출할 YAML을 대신합니다.)

with open(f"./{iden}_job.yaml", "w+") as fw:
    fw.write(tmp)

subprocess.run(["kubectl", "apply", "-f", f"{iden}_job.yaml"])

subprocess.run(["kubectl", "wait", "--for=condition=complete", f"job/{iden}"])

#text = get_job_logs(iden)

logs = get_job_logs2(iden)
print(logs)
thread = threading.Thread(target=plzcleanup, args=(iden,))
thread.start()

#send_json_message_to_sqs(text, iden)