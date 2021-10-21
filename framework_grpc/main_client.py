import grpc

import federated_pb2
import federated_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = federated_pb2_grpc.ManagerStub(channel)
        response = stub.GetModel(federated_pb2.ModelRequest(information=federated_pb2.ModelRequest.Information.VERSION))
        result = response.version
        print(f'received: {result}')


if __name__ == '__main__':
    run()
