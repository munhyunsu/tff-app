import json
import asyncio

import websockets

FLAGS = None
_ = None

MODEL = {'MODEL VERSION': [0, 0, 0, 0],
         'LABEL LIST': [],
         'MODEL': 0}
CONNECTED = set()


async def handler_model_request():
    global MODEL
    response = MODEL
    return response


async def handler_label_update(data):
    global MODEL
    response = False
    data = json.loads(data)
    for label in data['NEW LABEL']:
        if label not in MODEL['LABEL LIST']:
            MODEL['LABEL LIST'].append(label)
            response = True
    MODEL['MODEL VERSION'][1] = MODEL['MODEL VERSION'][1] + 1

    return {'LABEL UPDATE': response}


async def handler_model_version():
    global MODEL
    response = {'MODEL VERSION': MODEL['MODEL VERSION']}
    return response


async def handler_learning_result(data):
    global MODEL
    data = json.loads(data)
    MODEL['MODEL'] = MODEL['MODEL'] + data['MODEL']
    MODEL['MODEL VERSION'][3] = MODEL['MODEL VERSION'][3] + 1

    response = {'LEARNING NUMBER': MODEL['MODEL VERSION']}
    return response


async def handler_main(websocket, path):
    global CONNECTED
    CONNECTED.add(websocket)
    print(f'Client connected: {websocket}')
    data = await websocket.recv()
    response = ''
    if path == '/modelrequest':
        response = await handler_model_request()
    elif path == '/labelupdate':
        response = await handler_label_update(data)
    elif path == '/modelversion':
        response = await handler_model_version()
    elif path == '/learningresult':
        response = await handler_learning_result(data)
    response = json.dumps(response)
    await websocket.send(response)
    print(f'{MODEL}')


async def main():
    print(f'Parsed arguments: {FLAGS}')
    print(f'Unparsed arguments: {_}')
#    ws_server = await websockets.serve(handler_main, 
#                                       FLAGS.host, FLAGS.port, 
#                                       reuse_address=True)
#    await ws_server.wait_closed()
    ws_server = websockets.serve(handler_main, 
                                 FLAGS.host, FLAGS.port, 
                                 reuse_address=True)
    async with ws_server as ws:
        print('Start Network Traffic Application Identification Federated Server')
        await ws.wait_closed()
    
    


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str,
                        default='localhost')
    parser.add_argument('--port', type=int,
                        default=9090)
    FLAGS, _ = parser.parse_known_args()
    
    asyncio.run(main())
