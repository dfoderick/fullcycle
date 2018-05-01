timeout 1
start "fcm:component" python component.py

rem start "fcm:shutdown" python when_shutdown.py
timeout 1
start "fcm:discover" python when_discover.py
timeout 1
start "fcm:discovered" python when_discovered.py
timeout 1
start "fcm:provision" python when_provision.py
timeout 1
start "fcm:provision dispatch" python when_provision_dispatch.py
timeout 1
start "fcm:switch" python when_switch.py
timeout 1
start "fcm:reset" python when_reset.py
timeout 1
start "rules" python when_runrules.py
timeout 1
start "fcm:alert" python when_alert.py
timeout 1
start "fcm:offline" python when_offline.py
timeout 1
start "fcm:online" python when_online.py
timeout 1
rem start "sensor" python when_sensor_reading.py
timeout 1
rem start "cloud" python when_cloud_push.py
timeout 1
start "fcm:monitorminer" python when_monitorminer.py
timeout 1
start "fcm:monitor" python when_monitor.py

timeout 5
start "fcm:schedule" python schedule.py
