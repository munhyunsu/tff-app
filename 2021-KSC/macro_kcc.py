print('#!/bin/bash')
major = 0
minor = 0
roundn = 0
for micro in range(0, 100):
    roundn = roundn + 1
    rounds = f'r{roundn}'
    version = f'v{major}.{minor}.{micro}'

    com_save = f'/home/harny/Github/tff-app/framework_grpc/venv/bin/python3 main_client_cli_savemodel.py --debug --name SIMPLE-CNN-32-32-3 --version {version} --output kcc/{version}'
    print(com_save)
    com_test = f'/home/harny/Github/tff-app/framework_grpc/venv/bin/python3 main_client_cli_testmodel_image.py --debug --model kcc/{version} --data kcc_test'
    print(com_test)

    for clientn in range(1, 11):
        if clientn <= 5:
            dataset = 'mnist_fashion_train'
        else:
            dataset = 'cifar10_train'
        clients = f'c{clientn}'
        com_train = f'/home/harny/Github/tff-app/framework_grpc/venv/bin/python3 main_client_cli_trainmodel_image.py --debug --model kcc/{version} --batch_size 32 --steps_per_epoch 200 --data {dataset} --output kcc/{rounds}/{clients}'
        print(com_train)

    for clientn in range(1, 11):
        clients = f'c{clientn}'
        com_upload = f'/home/harny/Github/tff-app/framework_grpc/venv/bin/python3 main_client_cli_uploadmodel.py --debug --name SIMPLE-CNN-32-32-3 --version {version} --model kcc/{rounds}/{clients}'
        print(com_upload)

    com_agg = f'/home/harny/Github/tff-app/framework_grpc/venv/bin/python3 main_client_cli_Control.py --debug --name SIMPLE-CNN-32-32-3 --version {version} --job_aggregation'
    print(com_agg)
        

