FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y wget curl make gcc perl libapr1-dev libaprutil1-dev libpcre3-dev && \
    wget https://archive.apache.org/dist/httpd/httpd-2.4.50.tar.gz && \
    tar -xf httpd-2.4.50.tar.gz && \
    cd httpd-2.4.50 && \
    ./configure --prefix=/ && \
    make && \
    make install

ADD httpd.conf /conf/httpd.conf

CMD ["httpd", "-D", "FOREGROUND"]
                                     
