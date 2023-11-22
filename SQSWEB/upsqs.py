import boto3
import uuid

def send_message_to_sqs(queue_url):
    # AWS SQS 클라이언트 생성
    sqs = boto3.client('sqs')

    try:
        # 사용자로부터 메시지 내용 입력 받기 현재는 input으로 한 줄 만 입력 받지만 추후 적절하게 수정
        message_body = input("Enter the message body: ")

        # Message Group&Deduplication ID 생성 (임의의 UUID 사용)
        deduplication_id = str(uuid.uuid4())
        Group_id = str(uuid.uuid4())

        # SQS 큐에 메시지 보내기
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
            MessageDeduplicationId=deduplication_id,
            MessageGroupId=Group_id
        )

        # 보낸 메시지에 대한 응답 출력
        print("MessageId: {}".format(response['MessageId']))
    except Exception as e:
        print("Error sending message: {}".format(e))

# 큐 URL을 직접 입력하거나, 환경 변수 등을 통해 동적으로 설정할 수 있습니다.
queue_url = 'https://sqs.ap-northeast-2.amazonaws.com/031717690025/CodeQueue.fifo'

# send_message_to_sqs 함수 호출
send_message_to_sqs(queue_url)

