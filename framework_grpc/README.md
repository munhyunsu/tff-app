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

# Run example

## KSC2021

```bash
python3 ./KSC2021/...
```
