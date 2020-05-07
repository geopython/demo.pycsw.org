FROM alpine:3.11

MAINTAINER Tom Kralidis <tomkralidis@gmail.com>

RUN apk add py3-gunicorn

COPY deploy_webhook.py /
WORKDIR /

EXPOSE 8000

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8001", "deploy_webhook:application"]
