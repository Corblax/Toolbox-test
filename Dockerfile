FROM ubuntu:20.04

# Installation des dépendances nécessaires
RUN apt-get update && \
    apt-get install -y wget curl make gcc perl libapr1-dev libaprutil1-dev libpcre3-dev

# Téléchargement d'Apache 2.4.50
RUN wget https://archive.apache.org/dist/httpd/httpd-2.4.50.tar.gz && \
    tar -xf httpd-2.4.50.tar.gz

# Configuration, compilation et installation d'Apache
RUN cd httpd-2.4.50 && \
    ./configure --prefix=/ && \
    make && \
    make install

# Copie du fichier de configuration d'Apache
ADD httpd.conf /conf/httpd.conf

# Création du fichier start_apache.py
RUN echo "#!/usr/bin/env python3" > /start_apache.py && \
    echo "print('Hello, world! This is start_apache.py')" >> /start_apache.py

# Commande pour démarrer Apache
CMD exec httpd -D "FOREGROUND"
                                   
