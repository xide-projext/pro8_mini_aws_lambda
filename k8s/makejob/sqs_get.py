import boto3, time
import json
import os
import threading
from k8s import run_k8s

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
    if response['Messages']:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        print(message['Body'])

        # m = message['Body'].replace("\n","")

        # jo = json.loads(m)
        iden = message['MessageAttributes']['client_id']['StringValue']
        code = message['Body']

        # #이후 코드의 언어에 따라 Image 변경, 현재는 Python Image
        image = "031717690025.dkr.ecr.ap-northeast-2.amazonaws.com/python:latest"

        thread = threading.Thread(target=run_k8s, args=(iden, code, image,))
        thread.start()

        # 메시지 삭제
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

if __name__ == "__main__":
    # AWS SQS 클라이언트 생성
    queue_url = os.environ.get('SQS_QUEUE')
    sqs = boto3.client('sqs')

    while True:
        receive_message_from_sqs(sqs, queue_url)
        time.sleep(1)