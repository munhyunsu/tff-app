# Prerequirements

- [Docker](https://docs.docker.com/engine/install/ubuntu/)

- Libraries

```bash
apt install libmariadb-dev
```

## Generate proto

```bash
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. ./helloworld.proto
```

# Prepare database

## Run MariaDB on Docker

```bash
docker pull mariadb
docker run --name fldb -p 3306:3306 -v ABSOLUTEPATH/var/lib/mysql:/var/lib/mysql -e MARIADB_ROOT_PASSWORD=my-secret-pw -d mariadb:latest
```

## Create user and database

```bash
docker exec -it fldb bash
mariadb -uroot -p
```

```sql
CREATE DATABASE fldb;
CREATE USER IF NOT EXISTS fluser@fldb IDENTIFIED BY 'user-secret-pw';
SHOW WARNINGS;
GRANT ALL PRIVILEGES ON fldb.* TO 'fluser'@'%' IDENTIFIED BY 'user-secret-pw';
FLUSH PRIVILEGES;
```

## Create secret file

```python
dbname = 'fldb'
dbhost = '127.0.0.1'
dbport = 3306
dbuser = 'fluser'
dbpassword = 'user-secret-pw'
```

# Examples

## KSC2021 example

```bash
cd ./KSC2021
```

1. Initilize database

```bash
python3 -m grpc_tools.protoc -I./ --python_out . --grpc_python_out . federated.proto
python3 main_database_init.py --debug --reset
python3 main_insert_model.py --debug --input model_simple_cnn.py
python3 main_server.py --debug
```

2. Get base model information

```bash
python3 main_client_cli_InformationRequest.py --debug
```

3. Download model from service

```bash
python3 main_client_cli_savemodel.py --debug --name SIMPLE-CNN-32-32-3 --version v0.0.0 --output kcc/v0.0.0
python3 main_client_cli_testmodel_image.py --debug --model kcc/v0.0.0 --data kcc_test
```

4. Train model and upload learning result

```bash
python3 main_client_cli_trainmodel_image.py --debug --model kcc/v0.0.0 --batch_size 32 --steps_per_epoch 200 --data mnist_fashion_train --output kcc/r1/c1
python3 main_client_cli_uploadmodel.py --debug --name SIMPLE-CNN-32-32-3 --version v0.0.0 --model kcc/r1/c1
```
