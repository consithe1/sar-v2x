#!/bin/bash

# install all dependencies
sudo apt-get install curl g++-11 clang cmake default-jre libboost-all-dev build-essential clang lld gdb bison flex perl python3 python3-pip qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools libqt5opengl5-dev libxml2-dev zlib1g-dev doxygen graphviz libwebkit2gtk-4.0-37 libgeographic-dev libcrypto++-dev sumo sumo-tools sumo-doc
# clone the artery repository
git clone --recurse-submodule https://github.com/riebl/artery.git
# download Omnet++ 5.6.2 release from GitHub
curl -L https://github.com/omnetpp/omnetpp/releases/download/omnetpp-5.6.2/omnetpp-5.6.2-src-linux.tgz --output omnetpp-5.6.2-src-linux.tgz

# install artery dependencies
python3 -m pip install --user --upgrade numpy pandas matplotlib scipy seaborn posix_ipc ipython jupyter

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
# build omnetpp
source setenv
./configure
make

# go back to sar-v2x folder
cd ..
# move the sar folder to the artery/scenarios folder
mv sar artery/scenarios/sar
cd artery/scenarios/
# add the sar project to the artery project list
echo "add_subdirectory(sar)" >> CMakeLists.txt
cd sar/car2car-grid
# generate sumo configurations for the project
python3 make_sumo_configurations.py --net_file ../net.net.xml
# go back to artery folder
cd ../../..
# create build directory
mkdir build
cd build
# build the projects
cmake .. -DWITH_SIMULTE=ON -DWITH_STORYBOARD=ON
cmake --build .
# go back to artery folder
cd ..

# run the project
cmake --build build --target run_sar
