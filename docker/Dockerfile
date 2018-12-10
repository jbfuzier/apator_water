from python:2.7-stretch 
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
    
CMD cd && \
    rm -rf .\apator_water && \
    git clone https://github.com/jbfuzier/apator_water.git && \
    cd apator_water && \
    pip install -r requirements.txt && \
    /usr/local/bin/python water_consumption.py
