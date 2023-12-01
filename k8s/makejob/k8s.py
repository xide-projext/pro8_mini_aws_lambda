import subprocess
import os
import base64
import time
import boto3
import json
import uuid
import threading
from jinja2 import Template

# J2 템플릿 오픈
def load_template(file_path):
  with open(file_path, 'r') as file:
      return Template(file.read())

# Kubernetes Job 생성
def create_kubernetes_job(iden, code, image, env):
  template = load_template("./01.j2")
  tmp = template.render(iden=iden,num_pods=len(env))

  template = load_template("./02.j2")
  template2 = load_template("./03.j2")
  encoded_code = base64.b64encode(code.encode()).decode()
  for idx, innerenv in enumerate(env) :
    tmp += "\n" + template.render(idx=idx, image=image)
    tmp += "\n" + template2.render(args_name = "PYCODE", env_var=encoded_code)
    tmp += "\n" + template2.render(args_name = "ARGS_COUNT", env_var=len(innerenv)-1)
    tmp += "\n" + template2.render(args_name= "ARGS", env_var=innerenv[:-1])
    tmp += "\n" + template2.render(args_name= "ANSWER", env_var=innerenv[-1])

  with open(f"./{iden}_job.yaml", "w+") as fw:
      fw.write(tmp)

  subprocess.run(["kubectl", "apply", "-f", f"./{iden}_job.yaml"])

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

# 로그 따기
def get_job_logs(iden):
  pods = get_job_pod_names(iden)
  logs = []
  for num, pod in enumerate(pods):
    cmd = ["kubectl", "logs", pod, "-c", f"my-container-{num+1}"]
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)
    logs.append(result.stdout)
  return logs

# Job 삭제
def delete_kubernetes_job(iden):
  subprocess.run(["kubectl", "delete", f"job/{iden}"])

# YAML 파일 삭제
def delete_yaml(iden):
  file_name = f"./{iden}_job.yaml"
  if os.path.exists(file_name):
    os.remove(file_name)

# 삭제 전담 함수
def plzcleanup(iden):
  delete_kubernetes_job(iden)
  delete_yaml(iden)

# 결과를 SQS로 전송
def send_json_message_to_sqs(json_text, iden):
  queue_url = os.environ.get('OUT_QUEUE')
  sqs = boto3.client('sqs')

  try:
    deduplication_id = str(uuid.uuid4())
    group_id = str(uuid.uuid4())

    response = sqs.send_message(
      QueueUrl=queue_url,
      MessageBody=json_text,
      MessageAttributes={'client_id': {'StringValue': str(iden), 'DataType': 'String'}},
      MessageDeduplicationId=deduplication_id,
      MessageGroupId=group_id
    )
  except Exception as e:
    print("Error sending message: {}".format(e))

def package_json (log_list):
  log_dict = dict()
  for idx, log in enumerate(log_list):
    text = json.loads(log)
    log_dict[str(idx)] = text
  
  log_json = json.dumps(log_dict, indent=2)
  print(log_json)
  return log_json

# 사실상의 Main 함수
def run_k8s(iden, code, image, env):
  iden = str(iden)
  create_kubernetes_job(iden, code, image, env)
  subprocess.run(["kubectl", "wait", "--for=condition=complete", f"job/{iden}"])

  text = get_job_logs(iden)
  thread = threading.Thread(target=plzcleanup, args=(iden,))
  thread.start()

  send = package_json(text)

  send_json_message_to_sqs(send, iden)