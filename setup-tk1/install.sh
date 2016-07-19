#install git and base repositories
apt-get install git
apt-add-repository universe
apt-add-repository multiverse
apt-get update

#install vlc and node
apt-get install vlc build-essential checkinstall curl libssl-dev
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
apt-get install tightvncserver
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

#configure wine 
echo "Installing Wine Dependencies..."
apt-get install flex bison xserver-xorg-dev x11proto-gl-dev
echo "\n\n\n\nAbout to install and compile wine from source, this may take a while (1hr)...\nYou can abort this if you don't care about wine, otherwise setup is complete...\n"
wget http://dl.winehq.org/wine/source/1.8/wine-1.8.3.tar.bz2
tar -xf wine-1.8.3.tar.bz2 -C /etc/
/etc/wine-1.8.3/configure
/etc/wine-1.8.3/make
#TODO: Make a symbolic link to /bin/usr once this is done compiling, waiting on it right now...

