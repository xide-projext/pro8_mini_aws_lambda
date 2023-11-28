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
def create_kubernetes_job(code, iden, image, env=[]):
  template = load_template('python.j2')
  encoded_code = base64.b64encode(code.encode()).decode()
  variables = {'pycode': encoded_code, 'iden': iden, 'imagename': image}
  rendered_yaml = template.render(variables)

  with open(f"./{iden}_job.yaml", "w+") as fw:
    fw.write(rendered_yaml)

  subprocess.run(["kubectl", "apply", "-f", f"{iden}_job.yaml"])

# 로그 따기
def get_job_logs(iden):
  return subprocess.check_output(["kubectl", "logs", f"job/{iden}"], text=True)

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

# 사실상의 Main 함수
def run_k8s(iden, code, image, env=[]):
  create_kubernetes_job(code, iden, image)
  subprocess.run(["kubectl", "wait", "--for=condition=complete", f"job/{iden}"])

  text = get_job_logs(iden)
  print(text)
  thread = threading.Thread(target=plzcleanup, args=(iden,))
  thread.start()

  send_json_message_to_sqs(text, iden)