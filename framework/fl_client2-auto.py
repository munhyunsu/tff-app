import json
import asyncio
import random
import time

import websockets

MODEL = None
URL = ''


async def main():
    global MODEL
    global URL
    print(f'자동화 클라이언트')
    URL = f'ws://{FLAGS.host}:{FLAGS.port}/'
    uri = f'{URL}modelrequest'
    async with websockets.connect(uri) as websocket:
        await websocket.send('')
        MODEL = json.loads(await websocket.recv())
    print(f'Initialize complete {MODEL}')
    while True:
        user = random.choices(['modelversion', 'modelrequest',
                               'labelupdate', 'learningresult'],
                              weights=[35, 35, 20, 10],
                              k=1)[0]
        uri = f'{URL}{user}'
        data = {}
        if user == 'exit':
            break
        elif user == 'labelupdate':
            labels = [random.randint(0, 1024)]
            data = {'NEW LABEL': labels}
        elif user == 'learningresult':
            model = random.randint(0, 1024)
            MODEL['MODEL'] = model
            data = MODEL
        async with websockets.connect(uri) as websocket:
            data = json.dumps(data)
            print(f'> {uri} {data}')
            await websocket.send(data)
            response = await websocket.recv()
            print(f'< {response}')
        time.sleep(10)
            
   

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str,
                        default='localhost')
    parser.add_argument('--port', type=int,
                        default=9090)
    FLAGS, _ = parser.parse_known_args()

    asyncio.run(main())
