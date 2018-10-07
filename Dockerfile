FROM python:2.7.15-alpine3.7

ARG all_proxy

RUN ["mkdir","/www"]
RUN pip install -U googlemaps pyyaml

ENV HTTP_PROXY=$all_proxy \
    HTTPS_PROXY=$all_proxy 
 
RUN apk add --no-cache tzdata
ENV TZ America/New_York

COPY *.py /
COPY www/*.js /www/

EXPOSE 8901

ENTRYPOINT [ "python","trafficscreen.py" ]