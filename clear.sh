#!/bin/bash

rm ./yandex_service/requirements.txt
rm ./main_service/requirements.txt
rm ./worker/requirements.txt
echo y | rm -r ./worker/tasks
echo y | rm -r ./worker/utils