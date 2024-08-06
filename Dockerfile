
FROM python:3.11.9-alpine

RUN apk update && apk upgrade
RUN addgroup seismic && adduser -D -G seismic seismic
USER seismic

WORKDIR /home/seismic
RUN mkdir -p app && chown seismic:seismic app

WORKDIR /home/seismic/app
RUN python3 -m venv .venv && . .venv/bin/activate
COPY --chown=seismic:seismic . .

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3", "main.py" ]
