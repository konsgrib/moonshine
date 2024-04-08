dependencies:
pip install psutil
sudo apt-get install rpi.gpio
raspi-config enavle one-wire

add next to  /boot/config.txt
    dtoverlay=w1-gpio
    or
    dtoverlay=w1-gpio,gpiopin=x where x=pin number
    by default it is GPIO4 (pin7)

    sudo modprobe w1-gpio

watchdog.py running as a daemon and monitoring pin16
once pin16 is grounded, it is strarting main.py

main.py program that is executing the flow

1.run
T1 is checking temperature
once T1 >=70C is is switching cold water valve relay on
when T1 is >=97C it is switching off relay current, then switching off relay2

   ln -s /home/griban/Projects/moonshine/moonshine.service /etc/systemd/system/moonshine.service
   sudo ln -s /home/griban/Projects/moonshine/moonshine.service /etc/systemd/system/moonshine.service
   sudo systemctl daemon-reload
   sudo systemctl enable moonshine.service
   sudo systemctl start moonshine.service
