FROM python

WORKDIR /opt/bot
RUN apt update && apt install -y ffmpeg curl nodejs npm
RUN npm install -g deno
COPY . .

RUN pip install -r requirements.txt
CMD ["/opt/bot/entrypoint.sh"]
