
# Installing Full Cycle Mining on Raspberry Pi  
## Reference Hardware
	1. Raspberry Pi 3b+ (2018, 1.4 GHz) or newer
	2. Power adapter
	3. High Quality 64GB SD card or larger
	3. (Optional) Touchscreen 7"
	4. USB keyboard and mouse may be necessary

## Install Guide
If there are any problems installing from this guide then consult
the following site for updated instructions.  
https://www.raspberrypi.org/documentation/installation/installing-images/README.md

1. Download latest Raspbian Desktop OS and Etcher utility program. 
	https://www.raspberrypi.org/downloads/raspbian/  
	Etcher  
    https://etcher.io/

2. Write the image to SD card on a Windows PC
	Create ssh file on boot partition so the Pi will work headless.
    https://www.raspberrypi.org/documentation/remote-access/ssh/

3. Connect power and network cable to the Raspberry Pi

4. Boot the Pi
	If Desktop GUI does not show then
	ping raspberrypi.local to find ip address on the Pi.
	[It didnt show gui display the first time. But after I put ssh file on boot then
	it booted to gui next time I ran it. Go figure.]

5. Connect to the Pi using ssh.
    Default ssh login  
    username: pi  
    password: raspberry

6. Update your OS.
	sudo apt-get update  
	sudo apt-get dist-upgrade  

7. Additional setup, if desired
	Calibrate screen if needed  
	sudo apt-get install matchbox-keyboard  

8. If you have a camera and temperature sensor then enable them.
	sudo raspi-config

Do a final boot using `sudo reboot`
You are now ready to install Full Cycle Mining
