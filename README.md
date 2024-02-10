# sar-v2x

## Creation of a VM with VirtualBox
| **Operating system** 	| **Storage (GiB)** 	| **Memory (GiB)** 	| **CPU** 	| **3D acceleration** 	|
|----------------------	|-------------------	|------------------	|---------	|---------------------	|
|     Ubuntu 22.04     	|         50        	|         4        	|    2    	|       enabled       	|


In the VM, after the installation of Ubuntu, execute the following commands
```bash
# add yourself to the sudoers if it's not already the case
su -
sudo usermod -a -G sudo <replace_with_username>
# restart your machine to make the changes applied

# install git
sudo apt-get install git

# download this project
git clone https://github.com/consithe1/sar-v2x.git
cd sar-v2x

# install project and resources
source install.sh
```
