FROM python:2.7.15-alpine3.7

ARG all_proxy

RUN ["mkdir","/www"]
RUN pip install -U googlemaps

ENV api_key= \
    mode="driving" \
    language="en" \
    units="imperial" \
    traffic_model="best_guess" \
    onhour=17 \
    onmin=30 \
    offhour=20 \
    offmin=30 \
    update_interval=6 \
    HTTP_PROXY=$all_proxy \
    HTTPS_PROXY=$all_proxy 
 
RUN apk add --no-cache tzdata
ENV TZ America/New_York

COPY googletrafficscreen.py /
COPY ./www/*.js /www/
COPY ./www/default-index.html /www/
COPY ./www/default-locations.json /www/

EXPOSE 80

ENTRYPOINT [ "python","googletrafficscreen.py" ]