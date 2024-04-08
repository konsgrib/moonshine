The moonshine project.

Aim is to automate analcoho machine

there will be two cycles(procedures) of distilliation
1. User press Start button
2. Boiler is switched on
3. Termo snsor constantly checking temperature
    If it id more than 74C then cooler is switching on
    When temperature is more than 97,
        boiler is switching off
        2 minutes countdown starts till the cooler stop


There is a watchdog.py which must be registered as system service, it listens for the buttons 
and launchint cycles.


Display shows different info such as status of the boiler and cooler, both termo sensors temperature, water level and if the valve is on or of
