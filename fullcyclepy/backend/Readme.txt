
Steps to get everything running:

run startfcm.cmd

It will run the following processing

	python schedule.py
	python discover_commandlistener.py
	python provision_commandlistener.py
	python monitor_commandlistener.py
	python rules_listener.py
	python alert_listener.py
	python mydevices_listener.py
	python cloud_listener.py

Then monitor queues using http://raspberrypi.local:15672/#/queues