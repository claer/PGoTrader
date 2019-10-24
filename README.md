# PGoTrader

This script does auto-trading between two devices. 

## Requirements

*You only need to perform this steps once*

### Phone
- Enable Developper mode and Allow USB debugging

### ADB
- Install `adb`, make sure it's on your systems PATH, alternatively you can place adb in the same folder.
- Install the USB drivers for your phone if needed.
- Check adb has access to both of your phones with "adb devices"
```bash
$ adb devices
List of devices attached
f001f001f001f001        device
172.16.1.142:5555       device
```
- Tip: to enable adb access via Wifi, once you have access to USB:
```bash
$ adb -s <device name> tcpip 5555
```
- Ensure shell access is working on both phones. Exit the shell with `exit`
```bash
$ adb -s <device name> shell
```

### Program files

- Clone all the files from this repository.
- Install Python >=3.7 (older versions will not work).
- Download all the requisites: pip3 install -r requirements.txt --user

### Location configuration

- Screen capture the different trade phases. Including errors.
- Set up `config.yaml`, most of the options are documented there. What is important is taking time to get the positions right for screen locations.
- Do some screen captures and check the results with the script check_loc.py. Per eg.:
```bash
$ ./check_loc.py --loc weight_box_lucky --app app2 ../../Screens/J5_lucky.png
Checking weight_box_lucky on app2
WEIGHT
```

## How to use
- Open both apps.
- Go to Friends, and open the friend screen (in both apps).
- Run `python trade.py`.
- Synopsis:
```
usage: trade.py [-h] [--config CONFIG] [--stop-after STOP_AFTER]

Pokemon GO trader

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Config file location. Default "config.yaml"
  --stop-after STOP_AFTER
                        Stop after exchanging <number> pokemon. Default 1
```

By default the script will only trade one pokemon. If you want to trade several pokemons in a row, add the option --stop-after <number>


## Todo

- Implement error case handling
- Implement controls on traded pokemons
- Handle translation. Either with a proper translation system like gettext or may be just a dict.
- Create some unit tests
