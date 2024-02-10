#!/bin/bash

# install curl
sudo apt-get install curl
# clone the artery repository
git clone --recurse-submodule https://github.com/riebl/artery.git
# download Omnet++ 5.6.2 release from GitHub
curl -L https://github.com/omnetpp/omnetpp/releases/download/omnetpp-5.6.2/omnetpp-5.6.2-src-linux.tgz --output omnetpp-5.6.2-src-linux.tgz

# install artery dependencies
sudo apt-get install g++-11 clang cmake default-jre libboost-all-dev
sudo apt-get install build-essential clang lld gdb bison flex perl python3 python3-pip qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools libqt5opengl5-dev libxml2-dev zlib1g-dev doxygen graphviz libwebkit2gtk-4.0-37
python3 -m pip install --user --upgrade numpy pandas matplotlib scipy seaborn posix_ipc

# extract the omnetpp archive
tar xvfz omnetpp-5.6.2-src-linux.tgz
# deleting the archive since we don't need it anymore
rm -rf omnetpp-5.6.2-src-linux.tgz

echo "export PATH=$(pwd)/omnetpp-5.6.2/bin:$PATH" >> ~/.bashrc

# omnetpp installation
cd omnetpp-5.6.2
# modify configure.user in omnetpp root folder
sed 's/WITH_OSGEARTH=yes/WITH_OSGEARTH=no/g' -i configure.user
sed 's/WITH_OSG=yes/WITH_OSG=no/g' -i configure.user
source setenv
./configure
make

# installation of Vanetza dependencies for CAM messaging
cd ..
sudo apt-get install libgeographic-dev libcrypto++-dev

# SUMO installation
sudo apt-get install sumo sumo-tools sumo-doc

# installing jupyter for the result analysis
sudo pip3 install ipython jupyter

# artery installation
cd artery
mkdir build
cd build
cmake ..
cmake --build .

# move the sar folder to the artery/scenarios folder
cd ..
mv sar artery/scenarios/sar
cd scenarios/
# add the sar project to the artery project list
echo "add_subdirectory(sar)" >> CMakeLists.txt
cd sar/car2car-grid
# generate sumo configurations for the project
python3 make_sumo_configurations.py --net_file ../net.net.xml
cd ../../../build
cmake .. -DWITH_SIMULTE=ON -DWITH_STORYBOARD=ON
cmake --build .
cd ..

# run the project
cmake --build build --target run_sar
