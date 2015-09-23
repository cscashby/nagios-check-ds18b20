# README #

Nagios plugin to read and alert on the temperature as detected by a ds18b20 probe.

### Version History ###

* Version v0.1

Initial version, not much intelligence built into this version but it is functional!

### How do I get set up? ###

Copy check_ds18b20.py into {nagios-plugins directory} and ensure it is executable.

* Dependencies

Also requires a copy of temp.py, in this repo or originally from the ['rpi-ds18b20' snippet](https://bitbucket.org/snippets/cscashby/r95ak).

Copy temp.py into the same folder or somewhere on $PYTHONPATH

### Who do I talk to? ###

* @cscashby