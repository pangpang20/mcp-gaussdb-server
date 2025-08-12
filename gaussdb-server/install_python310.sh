sudo yum groupinstall "Development Tools" -y
sudo yum install openssl-devel -y
sudo yum install gcc -y  
sudo yum install gcc-c++ -y  
sudo yum install bzip2-devel -y  
sudo yum install libffi-devel -y  
sudo yum install zlib-devel -y  
sudo yum install wget -y  
sudo yum install make -y  
sudo yum install glibc-devel -y  
sudo yum install libgcc -y  
sudo yum install tar -y  
sudo yum install bzip2 -y  
sudo yum install zlib -y  
sudo yum install xz -y  
sudo yum install readline-devel -y  
sudo yum install sqlite-devel -y  
sudo yum install sqlite-libs -y  

cd /usr/src

if [ ! -f /lib64/libgcc_s.so.1 ]; then
    sudo ln -sf /usr/lib64/libgcc_s.so.1 /lib64/libgcc_s.so.1
    sudo ldconfig
fi

sudo wget https://mirrors.huaweicloud.com/python/3.10.14/Python-3.10.14.tgz
sudo tar xzf Python-3.10.14.tgz
cd Python-3.10.14
OPENSSL_PREFIX=/usr
sudo ./configure --enable-optimizations --with-ensurepip=install \
    --with-openssl=$OPENSSL_PREFIX
sudo make -j$(nproc)
sudo make altinstall
python3.10 -m ssl
python3.10 --version
