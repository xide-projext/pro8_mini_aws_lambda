import boto3, time
import json

from diff_match_patch import diff_match_patch

test = '''
{
   "Identify":"hihi",
   "Code":"askqwek150%@)@%)*",
   "Type":"Python",
   "Env":{
      "aa":"bb",
      "cc":"dd"
   }
}
'''


def receive_message_from_sqs(sqs, queue_url):

    # 메시지를 받기 위한 receive_message 호출
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'All'
        ],
        MessageAttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=1,
        VisibilityTimeout=5, #타임아웃이 0 이면 삭제를 할 수 없음 주의!
        WaitTimeSeconds=1
    )

    # 받은 메시지가 있는지 확인
    # print(response)
    if response['Messages']:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        m = message['Body'].replace("\n","")

        jo = json.loads(m)
        # print(f"Identify : {jo['Identify']}")
        # print(f"Code : {jo['Code']}")
        # print(f"Type : {jo['Type']}")
        # print(f"Env : {jo['Env']}")
        # print(f"Env Num : {len(jo['Env'])}")
        
        # 메시지 삭제 (optional)
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

# 큐 URL을 직접 입력하거나, 환경 변수 등을 통해 동적으로 설정할 수 있습니다.
queue_url = 'https://sqs.ap-northeast-2.amazonaws.com/031717690025/CodeQueue.fifo'

# AWS SQS 클라이언트 생성
sqs = boto3.client('sqs')

# receive_message 함수 호출
while True:
    receive_message_from_sqs(sqs, queue_url)

    time.sleep(1)