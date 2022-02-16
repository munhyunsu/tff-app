import subprocess

python3 = '/home/dnlab/tff-app/framework_grpc/venv/bin/python3'

cmd = f'{python3} main_insert_model.py --debug --input model_Expandable-FashionMNIST2-5.py'
subprocess.run(cmd, shell=True, capture_output=True)

i = 0
while True:
    cmd = f'''{python3} main_client_cli_savemodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --output models/scenario5/v0.0.{i}
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client0 --output models/scenario5/r{i}/c1
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client0 --output models/scenario5/r{i}/c2
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client1 --output models/scenario5/r{i}/c3
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client1 --output models/scenario5/r{i}/c4
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client2 --output models/scenario5/r{i}/c5
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client2 --output models/scenario5/r{i}/c6
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client3 --output models/scenario5/r{i}/c7
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client3 --output models/scenario5/r{i}/c8
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client4 --output models/scenario5/r{i}/c9
{python3} main_client_cli_trainmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_train/client4 --output models/scenario5/r{i}/c10
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c1
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c2
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c3
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c4
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c5
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c6
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c7
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c8
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c9
{python3} main_client_cli_uploadmodel.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --model models/scenario5/r{i}/c10
{python3} main_client_cli_Control.py --debug --name Expandable-FashionMNIST2-5 --version v0.0.{i} --job_aggregation
'''
    subprocess.run(cmd, shell=True, capture_output=True)
    cmd = f'''{python3} main_client_cli_testmodel_image.py --debug --model models/scenario5/v0.0.{i} --data datasets/mnist_fashion_test/client4'''
    p = subprocess.run(cmd, shell=True, capture_output=True)
    acc = eval(p.stdout.decode('utf-8').split('\n')[1])[1]
    print(f'{i},{acc}')
    # if i%10 == 9 and acc >= 0.80:
    if i%10 == 9 and acc >= 0.90:
        break
    else:
        i = i + 1
