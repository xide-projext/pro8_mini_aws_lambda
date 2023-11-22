import boto3, time

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
        WaitTimeSeconds=0
    )

    print(response)

    # 받은 메시지가 있는지 확인
    if response['Messages']:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        # 메시지 출력 body 이외는 일단 주석처리 필요에 따라 사용
        print(f"Body: {message['Body']}")

        # 메시지 삭제 (optional)
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
    else:
        print("No messages in the queue.") # 새 메시지가 없으면 출력되는 텍스트

# 큐 URL을 직접 입력하거나, 환경 변수 등을 통해 동적으로 설정할 수 있습니다.
queue_url = 'https://sqs.ap-northeast-2.amazonaws.com/031717690025/CodeQueue.fifo'

# AWS SQS 클라이언트 생성
sqs = boto3.client('sqs')

# receive_message 함수 호출
while True:
    receive_message_from_sqs(sqs, queue_url)
    time.sleep(1)