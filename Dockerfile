from python:2.7-stretch as builder
RUN apt update && apt install -y \
    build-essential \
    libusb-1.0-0-dev \
    cmake \
    git && \
    cd && \
    git clone git://git.osmocom.org/rtl-sdr.git && \
    cd rtl-sdr/  && \
    mkdir build && \
    cd build && \
    cmake ../ && \
    make && \
    make install && \
    ldconfig && \
    cd && \
    git clone https://github.com/jbfuzier/rtl-wmbus.git && \
    cd rtl-wmbus/ && \
    make release && \
    apt remove --purge -y build-essential libusb-1.0-0-dev cmake
from python:2.7-stretch
WORKDIR	/root/apator_water
COPY	--from=builder /root/ /root/
COPY    ./ /root/apator_water
RUN apt update && apt install -y \
    libusb-1.0-0 && \
    pip install --no-cache-dir -r requirements.txt
CMD [ "python", "-u", "water_consumption.py" ]
