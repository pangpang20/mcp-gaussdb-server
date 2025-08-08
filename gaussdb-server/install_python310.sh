sudo yum groupinstall "Development Tools" -y
sudo dnf install -y gcc gcc-c++ openssl-devel bzip2-devel libffi-devel zlib-devel wget make glibc-devel libgcc tar bzip2 zlib xz zx-devel readline-devel sqlite-devel sqlite-libs
cd /usr/src
sudo wget https://mirrors.huaweicloud.com/python/3.10.14/Python-3.10.14.tgz
sudo tar xzf Python-3.10.14.tgz
cd Python-3.10.14
sudo ./configure --enable-optimizations
sudo make -j$(nproc)
sudo make altinstall
python3.10 --version
