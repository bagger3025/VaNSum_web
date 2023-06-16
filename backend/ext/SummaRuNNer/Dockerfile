FROM ubuntu:22.04

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install --yes --force-yes --no-install-recommends \
    sudo \
    curl \
    python3=3.10.6-1~22.04 \
    python3-pip \
    python3.10-venv

RUN echo "root:root" | chpasswd 


RUN adduser vansum
RUN echo "vansum ALL=(ALL:ALL) ALL" >> /etc/sudoers
RUN echo "vansum:vansum" | chpasswd 

USER vansum
WORKDIR /home/vansum

COPY --chown=vansum:vansum . /home/vansum/SummaRuNNer