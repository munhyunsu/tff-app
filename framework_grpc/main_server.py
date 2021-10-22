import concurrent

import grpc

import federated_pb2
import federated_pb2_grpc


class Server(federated_pb2_grpc.Manager):
    def GetModel(self, request, context):
        print(f'Information: {request.information}')
        if request.information == federated_pb2.ModelRequest.Information.VERSION:
            
            print('VERSION')
        elif request.information == federated_pb2.ModelRequest.Information.PARAMETER:
            print('PARAMETER')
        elif request.information == federated_pb2.ModelRequest.Information.ARCHITECTURE:
            print('ARCHITECTURE')
        value = '1.3.2'
        return federated_pb2.ModelReply(version=value)


def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    federated_pb2_grpc.add_ManagerServicer_to_server(Server(), server)
    server.add_insecure_port('[::]:50051')
    print(f'Run server')
    server.start()
    print(f'Start server')
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print('End server')
        server.wait_for_termination(1)
    print(f'Terminate server')


if __name__ == '__main__':
    serve()

