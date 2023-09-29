FROM python:3.11.5-alpine3.18

RUN apk add python3-dev gfortran
RUN apk add build-base python3-dev py3-pip
RUN apk add build-base
RUN apk add openblas openblas-dev

ENV BLAS=/usr/lib/libopenblas.so
ENV LAPACK=/usr/lib/libopenblas.so

COPY ./ /yandex_service

WORKDIR /yandex_service

RUN pip install -r requirements.txt

EXPOSE 8001
