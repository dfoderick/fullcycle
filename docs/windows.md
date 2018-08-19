# Installing Full Cycle on Windows 10
## Step 1: Install Ubuntu for Windows subsystem for Linux (WSL)
Install if from Microsoft Store using these instructions. https://docs.microsoft.com/en-us/windows/wsl/install-win10

## Step 2: Install redis on windows
Go to Ubuntu command prompt and run the following commands.
	sudo apt-get install redis-server
	redis-server  
    Installation overview is here: https://dzone.com/articles/redis-on-windows-what-are-your-options

## Step 3: Install erlang
	http://www.erlang.org/downloads/20.3
	Download the exe and run it as administrator.

## Step 4: Install rabbitmq
    Download and run the exe from
	https://www.rabbitmq.com/install-windows.html
    You will probably get Windows Defender firewall security alerts
	Start the rabbitmq service from windows menu	
	Add users using script

## Step 5: Install Maria DB
    https://downloads.mariadb.org/mariadb/10.3.9/#os_group=windows
    Run HeidiSQL for the database management tool
    Run db script ~/fullcycle/os/linux/fullcycle.sql

## Step 6: Start full cycle
    fullcycle/os/windows/fcmstart.cmd

## If not working then run diagnostics

    python3 fullcycle/fullcyclepy/backend/diagnotics.py
