import subprocess
import sys, os
import base64
import time
import boto3
import json
import uuid
import threading
from jinja2 import Template

def create_kubernetes_job(code, iden, image, env=[]):
  # 템플릿 로드
  with open('python.j2', 'r') as file:
    template_content = file.read()

  template = Template(template_content)
  
  encoded_code = base64.b64encode(code.encode()).decode()
  variables = {'pycode': encoded_code, 'iden': iden, 'imagename':image}
  # 변수를 적용하여 YAML 생성
  rendered_yaml = template.render(variables)

  # 생성된 YAML 출력 또는 파일에 저장
  with open(f"./{iden}_job.yaml", "w+") as fw :
    fw.write(rendered_yaml)

  # Kubernetes Job 생성
  subprocess.run(["kubectl", "apply", "-f", iden+"_job.yaml"])

def get_job_logs(iden):
  # Job 로그 가져오기
  job_logs = subprocess.check_output(["kubectl", "logs", f"job/{iden}"], text=True)
  return job_logs

def delete_kubernetes_job(iden):
  # Kubernetes Job 삭제
  subprocess.run(["kubectl", "delete", f"job/{iden}"])

def delete_yaml(iden) :
  file_name = f"./{iden}_job.yaml"
  if os.path.exists(file_name):
    os.remove(file_name)

def plzcleanup(iden):
  # Kubernetes Job 삭제
  delete_kubernetes_job(iden)

  # Yaml 삭제
  delete_yaml(iden)

def send_json_message_to_sqs(json_text, iden):
  queue_url = os.environ.get('OUT_QUEUE')
  # AWS SQS 클라이언트 생성
  sqs = boto3.client('sqs')

  try:
    # Message Group & Deduplication ID 생성 (임의의 UUID 사용)
    deduplication_id = str(uuid.uuid4())
    group_id = str(uuid.uuid4())

    # SQS 큐에 JSON 형식의 메시지 보내기
    response = sqs.send_message(
      QueueUrl=queue_url,
      MessageBody=json_text,
      MessageAttributes={'client_id': {'StringValue': str(iden), 'DataType': 'String'}},
      MessageDeduplicationId=deduplication_id,
      MessageGroupId=group_id
    )
  except Exception as e:
    print("Error sending message: {}".format(e))

def run_k8s(iden, code, image, env=[]):
  # start = time.time()

  # Kubernetes Job 생성
  create_kubernetes_job(code, iden, image)

  # Job이 완료될 때까지 대기
  subprocess.run(["kubectl", "wait", "--for=condition=complete", f"job/{iden}"])

  # Job 로그 출력
  text = get_job_logs(iden)

  thread = threading.Thread(target=plzcleanup, args=(iden,))
  thread.start()

  send_json_message_to_sqs(text, iden)

  # end = time.time() - start
  # print(f"Time : {end:5f}\n")