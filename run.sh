#!/bin/bash

#main service
cd ./main_service
poetry export -f requirements.txt --output requirements.txt

#yandex service
cd ..
cd ./yandex_service
poetry export -f requirements.txt --output requirements.txt

docker network create tr_net
docker-compose up

#yandex service
rm requirements.txt

# docker exec main_s pip install -r requirements.txt

#main service
cd ..
cd ./main_service
rm requirements.txt

# docker exec yandex_s pip install -r requirements.txt

#make migrations
./make_migrations.sh