FROM python:3.7-alpine

RUN apk update && apk upgrade && apk add --no-cache bash git openssh
RUN apk add -U --no-cache gcc build-base linux-headers ca-certificates python3-dev libffi-dev libressl-dev
RUN git clone https://github.com/TheCaptainCat/polydrive-server.git server
WORKDIR server
RUN pip install -U pip && pip install -r requirements.txt
COPY env.py .

EXPOSE 5000
CMD gunicorn -b 0.0.0.0:5000 polydrive:app
