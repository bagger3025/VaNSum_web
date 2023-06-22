FROM ubuntu:22.04

RUN apt-get update -y && apt-get install -y sudo \
    curl \
    python3=3.10.6-1~22.04 \
    python3-pip \
    python3.10-venv \
    g++ \
    openjdk-8-jdk \
    python3-dev \
    git

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

RUN apt-get update -y && apt-get install -y software-properties-common && apt-add-repository -y ppa:maveonair/helix-editor
RUN apt-get update -y && apt-get install -y helix


RUN echo "root:root" | chpasswd 

RUN adduser vansum
RUN echo "vansum ALL=(ALL:ALL) ALL" >> /etc/sudoers
RUN echo "vansum:vansum" | chpasswd 

USER vansum
COPY --chown=vansum:vansum . /home/vansum/SummaRuNNer
COPY --chown=vansum:vansum .config /home/vansum/.config

USER vansum
WORKDIR /home/vansum/SummaRuNNer

# RUN source .venv/bin/activate

# RUN bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)

# RUN python3 -m pip install --upgrade pip
