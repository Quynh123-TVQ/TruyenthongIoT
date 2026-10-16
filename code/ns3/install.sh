#!/usr/bin/env bash
set -eu
# Run as regular user on Debian/Ubuntu; sudo only for apt.
sudo apt update
sudo apt install -y git g++ cmake ninja-build python3 pkg-config libxml2-dev qtbase5-dev qt5-qmake libqt5svg5-dev
cd "$HOME"
if [ ! -d ns-3-tvq ]; then git clone --depth 1 --branch ns-3.43 https://gitlab.com/nsnam/ns-3-dev.git ns-3-tvq; fi
cd ns-3-tvq
./ns3 configure --enable-examples --enable-tests
./ns3 build -j 2
./ns3 run hello-simulator
# GUI alternative: sudo apt install netanim, if available in your distribution.
