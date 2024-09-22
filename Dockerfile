FROM python

WORKDIR /opt/bot
RUN apt update && apt install -y ffmpeg
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "djoneechan.py"]

