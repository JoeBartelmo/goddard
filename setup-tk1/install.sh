# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#install git and base repositories
apt-add-repository universe
apt-add-repository multiverse
apt-get update

#install essentials
apt-get install feh git vlc build-essential checkinstall curl libssl-dev tightvncserver python-pip python-dev python-imaging-tk libvlc-dev libvlc5 libgtk2.0 gnome-devel


#install vlc and node
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.0/install.sh | bash
source ~/.bashrc
source /home/ubuntu/.bashrc
nvm install 4.4.3

#install dtrx -- few of us prefer this package, not required
wget http://brettcsmith.org/2007/dtrx/dtrx-7.1.tar.gz
tar -xvf dtrx-7.1.tar.gz 
cd dtrx-7.1
python setup.py install --prefix=/usr/local
cd ..
rm -rf dtrx-7.1
rm dtrx-7.1.tar.gz

#VNC config
mkdir -p /etc/lightdm/lightdm.conf.d
cp vnc_config /etc/lightdm/lightdm.conf.d/vnc.conf

#disable usb 3.0 autosuspend
echo "Disabling usb autosuspend..."
echo -1 > /sys/module/usbcore/parameters/autosuspend

#enable usb 3.0
echo "Enabling usb 3.0..."
python enableUSB.py | grep usb_port_owner_info=

#install arduino ide
echo "Downloading Arduino IDE"
wget https://downloads.arduino.cc/arduino-1.6.9-linuxarm.tar.xz
echo "extracting tarball..."
tar -xf arduino-1.6.9-linuxarm.tar.xz -C /etc/
/etc/arduino-1.6.9/install.sh
ln -s /etc/arduino-1.6.9/arduino /usr/bin/arduino
rm arduino-1.6.9-linuxarm.tar.xz
source ~/.bashrc

#performance mode
echo "Enabling Performance mode.."
cp startup_config /etc/rc.local
chmod +x /etc/rc.local
/etc/rc.local

#pip, and other dependencies
pip install numpy
pip install matplotlib

#don't prompt on shutdown
gsettings set com.canonical.indicator.session suppress-logout-restart-shutdown true

#setup for ximea
wget http://www.ximea.com/downloads/recent/XIMEA_Linux_SP.tgz
tar -xf XIMEA_Linux_SP.tgz 
cd package
./install -cam_usb30
tee /sys/module/usbcore/parameters/usbfs_memory_mb >/dev/null <<<0
gpasswd -a ubuntu plugdev

