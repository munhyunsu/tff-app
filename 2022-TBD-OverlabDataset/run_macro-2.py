import subprocess

python3 = '/home/dnlab/tff-app/framework_grpc/venv/bin/python3'

cmd = f'{python3} main_insert_model.py --debug --input model_Expandable-FashionMNIST2-2.py'
subprocess.run(cmd, shell=True, capture_output=True)

i = 0
while True:
    cmd = f'''{python3} main_client_cli_savemodel.py --debug --name Expandable-FashionMNIST2-2 --version v0.0.{i} --output models/scenario2/v0.0.{i}
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario2/v0.0.{i} --data datasets/mnist_fashion_train/client0 --output models/scenario2/r{i}/c1
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario2/v0.0.{i} --data datasets/mnist_fashion_train/client0 --output models/scenario2/r{i}/c2
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario2/v0.0.{i} --data datasets/mnist_fashion_train/client1 --output models/scenario2/r{i}/c3
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario2/v0.0.{i} --data datasets/mnist_fashion_train/client1 --output models/scenario2/r{i}/c4
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-2 --version v0.0.{i} --model models/scenario2/r{i}/c1
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-2 --version v0.0.{i} --model models/scenario2/r{i}/c2
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-2 --version v0.0.{i} --model models/scenario2/r{i}/c3
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-2 --version v0.0.{i} --model models/scenario2/r{i}/c4
{python3} main_client_cli_Control.py --debug --name Expandable-FashionMNIST2-2 --version v0.0.{i} --job_aggregation
'''
    subprocess.run(cmd, shell=True, capture_output=True)
    cmd = f'''{python3} main_client_cli_testmodel_image.py --debug --model models/scenario2/v0.0.{i} --data datasets/mnist_fashion_test/client1'''
    p = subprocess.run(cmd, shell=True, capture_output=True)
    acc = eval(p.stdout.decode('utf-8').split('\n')[1])[1]
    print(f'{i},{acc}')
    if i%10 == 9 and acc >= 0.80:
        break
    else:
        i = i + 1
