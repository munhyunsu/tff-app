import os
import json
import asyncio

import websockets

MODEL = None
URL = ''




async def main():
    global MODEL
    global URL
    URL = f'ws://{FLAGS.host}:{FLAGS.port}/'
    uri = f'{URL}modelrequest'
    async with websockets.connect(uri) as websocket:
        await websocket.send('')
        MODEL = json.loads(await websocket.recv())
    print(f'Initialize complete {MODEL}')
    while True:
        user = input('입력: ').lower()
        uri = f'{URL}{user}'
        data = {}
        if user == 'exit':
            break
        elif user == 'labelupdate':
            labels = input('추가 라벨: ').split()
            data = {'NEW LABEL': labels}
        elif user == 'learningresult':
            model = int(input('전송 모델: '))
            MODEL['MODEL'] = model
            data = MODEL
        async with websockets.connect(uri) as websocket:
            data = json.dumps(data)
            await websocket.send(data)
            response = await websocket.recv()
            print(response)
            
   

if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str,
                        default='localhost')
    parser.add_argument('--port', type=int,
                        default=9090)
    parser.add_argument('--train' type=str,
                        default='train')
    FLAGS, _ = parser.parse_known_args()

    asyncio.run(main())
