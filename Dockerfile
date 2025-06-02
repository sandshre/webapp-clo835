FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip mysql-client && \
    apt-get clean
COPY . /app
WORKDIR /app
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python3"]
CMD ["app.py"]