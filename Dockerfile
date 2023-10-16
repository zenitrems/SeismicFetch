
FROM python:3.11.4-alpine


RUN addgroup seismic && adduser -S -G seismic seismic

RUN mkdir -p /app && chown seismic:seismic /app


RUN mkdir -p /home/app/ && chown seismic:seismic /home/app
WORKDIR /app
RUN python3 -m venv .venv && . .venv/bin/activate

COPY --chown=seismic:seismic . .

USER seismic

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3", "main.py" ]
