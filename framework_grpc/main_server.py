import concurrent

import grpc

import federated_pb2
import federated_pb2_grpc


class Server(federated_pb2_grpc.Manager):

    def SayHello(self, request, context):
        return federated_pb2.HelloReply(message=f'Hello, {request.name}')

    def SayHelloAgain(self, request, context):
        return federated_pb2.HelloReply(message=f'Hello again, {request.name}')


def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    federated_pb2_grpc.add_ManagerServicer_to_server(Server(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

