import asyncio
import websockets
import boto3 
import uuid
import os

# SQS 초기화
sqs = boto3.client('sqs')
send_queue_url = os.environ.get('SQS_QUEUE')
receive_queue_url = os.environ.get('OUT_QUEUE')
clients = {}

async def handle_connection(websocket):
    client_id = id(websocket)
    clients[client_id] = websocket

    try:
        async for message in websocket:
            print(f"Received message from client {client_id}: {message}")
            deduplication_id = str(uuid.uuid4())
            group_id = str(uuid.uuid4())

            # 메시지를 SQS에 전송
            sqs.send_message(
                QueueUrl=send_queue_url, 
                MessageBody=message, 
                MessageAttributes={'client_id': {'StringValue': str(client_id), 'DataType': 'String'}},
                MessageDeduplicationId=deduplication_id,
                MessageGroupId=group_id
            )

    finally:
        del clients[client_id]

async def listen_to_sqs():
    while True:
        # SQS로부터 메시지 받기
        response = sqs.receive_message(
            QueueUrl=receive_queue_url,
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
        
        if 'Messages' in response:
            for message in response['Messages']:
                client_id = int(message['MessageAttributes']['client_id']['StringValue'])
                if client_id in clients:
                    websocket = clients[client_id]
                    await websocket.send((message['Body'] + "\n"))

                    # SQS에서 메시지 삭제
                    sqs.delete_message(QueueUrl=receive_queue_url, ReceiptHandle=message['ReceiptHandle'])

        await asyncio.sleep(1)

start_server = websockets.serve(handle_connection, "0.0.0.0", 8010)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().create_task(listen_to_sqs())
asyncio.get_event_loop().run_forever()
