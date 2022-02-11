FROM python:3.8

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 5000
EXPOSE 8050
# CMD [ "python3", "-m" , "dashboard.py"]


# CMD [ "python3", "-m" , "dashboard.py"]

CMD ./launch.sh