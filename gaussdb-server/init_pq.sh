#!/bin/bash

echo "Step 1: Downloading GaussDB driver zip package..."
wget -O /tmp/GaussDB_driver.zip https://dbs-download.obs.cn-north-1.myhuaweicloud.com/GaussDB/1730887196055/GaussDB_driver.zip

echo "Step 2: Unzipping the driver package..."
unzip /tmp/GaussDB_driver.zip -d /tmp/
rm -rf /tmp/GaussDB_driver.zip

echo "Step 3: Extracting Python driver tarball..."
\cp /tmp/GaussDB_driver/Centralized/Hce2_arm_64/GaussDB-Kernel_505.2.0_Hce_64bit_Python.tar.gz /tmp/
rm -rf /tmp/GaussDB_driver

echo "Step 4: Extracting files from tar.gz..."
tar -zxvf /tmp/GaussDB-Kernel_505.2.0_Hce_64bit_Python.tar.gz -C /tmp/
rm -rf /tmp/GaussDB-Kernel_505.2.0_Hce_64bit_Python.tar.gz
rm -rf /tmp/psycopg2

echo "Step 5: Configuring shared library paths..."
echo /tmp/lib | sudo tee /etc/ld.so.conf.d/gauss-libpq.conf > /dev/null
sudo sed -i '1s/^/\/tmp\/lib\n/' /etc/ld.so.conf
sudo ln -s /tmp/lib/libssl.so /tmp/lib/libssl.so.3
sudo ln -s /tmp/lib/libcrypto.so /tmp/lib/libcrypto.so.3

echo "Step 6: Reloading dynamic linker cache..."
sudo ldconfig

echo "Step 7: Verifying libpq libraries..."
sudo ldconfig -p | grep pq

echo "All steps completed successfully."
