## Arrancar Mongo local
mongod --dbpath local_mongo/db1 --port 27017 --bind_ip 127.0.0.1 --fork --logpath local_mongo/db1.log

mongod --dbpath local_mongo/db2 --port 27018 --bind_ip 127.0.0.1 --fork --logpath local_mongo/db2.log

mongod --dbpath local_mongo/db3 --port 27019 --bind_ip 127.0.0.1 --fork --logpath local_mongo/db3.log
