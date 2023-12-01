WebSocket을 연결하기 위한 서버

Line 63 : start_server = websockets.serve(handle_connection, "0.0.0.0", 8010) 을 통해 8010 포트로 서비스 됨
WebSocket으로 연결하고 Web과 K8s 사이에서 값을 전달하는 역할

Require :
    AWS configure
    export SQS_QUEUE = WebSocket으로 들어온 코드를 K8s에게 전송할 SQS
    export OUT_QUEUE = K8s가 실행 결과를 전송할 SQS

How to Use :
    python websocketserver.py
    or python3 websocketserver.py
