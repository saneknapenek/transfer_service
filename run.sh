#!/bin/bash

#main service
cd ./main_service
poetry export -f requirements.txt --output requirements.txt

#yandex service
cd ../yandex_service
poetry export -f requirements.txt --output requirements.txt

#worker
cd ../worker
poetry export -f requirements.txt --output requirements.txt
mkdir ./utils ./utils/yrequests ./tasks
cp ../yandex_service/src/tasks/tasks.py ./tasks/
cp ../yandex_service/src/utils/yrequests/sync_requests.py ./utils/yrequests/sync_requests.py
cp ../yandex_service/src/utils/schemes.py ./utils/
cp ../yandex_service/src/utils/hashing.py ./utils/
touch ./utils/yrequests/__init__.py

#transfer service
cd ..
docker network create tr_net
docker compose up

# rm ./yandex_service/requirements.txt
# rm ./main_service/requirements.txt
# rm ./worker/requirements.txt
# rm -r ./worker/tasks & echo y
# rm -r ./worker/utils & echo y
sudo ./clear.sh

#make migrations
# ./main_service/make_migrations.sh