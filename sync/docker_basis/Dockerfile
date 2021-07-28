
FROM ubuntu:trusty
RUN apt-get update && apt-get --assume-yes -qq install build-essential automake libpcap-dev iptables


COPY ./data /root/environment

ENV RTE_SDK "/root/environment/dpdk"
ENV RTE_TARGET "x86_64-native-linuxapp-gcc"
ENV DPDK_DIR "/root/environment/dpdk"
ENV DPDK_BUILD "x86_64-native-linuxapp-gcc"

WORKDIR /root/environment

RUN tar xf dpdk.tar
RUN rm dpdk.tar


CMD ["/bin/bash"]