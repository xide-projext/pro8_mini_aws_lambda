import subprocess
import sys
import os
import base64
import time
from jinja2 import Template

def create_kubernetes_job(code, iden, image):
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
  print(f"{iden}Job Logs: \n{job_logs}")

def delete_kubernetes_job(iden):
  # Kubernetes Job 삭제
  subprocess.run(["kubectl", "delete", f"job/{iden}"])

def delete_yaml(iden) :
  file_name = f"./{iden}_job.yaml"
  if os.path.exists(file_name):
    os.remove(file_name)

if __name__ == "__main__":
  # start = time.time()
  # test용 ARGV 1=식별자 2=파일 경로 
  iden = sys.argv[1]
  path = sys.argv[2]
  image = "031717690025.dkr.ecr.ap-northeast-2.amazonaws.com/python:latest"
  # 상기한 테스트는 이후 삭제 예정

  with open( path, "r+" ) as fr :
    env_code = fr.read()

  # Kubernetes Job 생성
  create_kubernetes_job(env_code, iden, image)

  # Job이 완료될 때까지 대기
  subprocess.run(["kubectl", "wait", "--for=condition=complete", f"job/{iden}"])

  # Job 로그 출력
  get_job_logs(iden)

  # Kubernetes Job 삭제
  delete_kubernetes_job(iden)

  # Yaml 삭제
  delete_yaml(iden)

  # end = time.time() - start

  # print(f"Time : {end:5f}\n")