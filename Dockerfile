FROM python:3.7-alpine

RUN apk add -U --no-cache gcc build-base linux-headers ca-certificates python3-dev libffi-dev libressl-dev
COPY . /server
WORKDIR server
RUN pip install -U pip && pip install -r requirements.txt

EXPOSE 5000
RUN python polydrive.py init_fake_database
CMD gunicorn -b 0.0.0.0:5000 polydrive:app
