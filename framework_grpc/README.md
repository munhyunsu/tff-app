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


