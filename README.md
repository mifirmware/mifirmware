# Mi Firmware

You can create flashable firmware for xiaomi devices with just a command.

## Getting Started

* You should use the latest Python 3 release.

1) Clone the [this repo](https://github.com/ardadem/xiaomi-flashable-firmware-creator) into the same folder that you have cloned this repo to.

2) Here needs to the some dependencies, you can install these via pip.

```
pip install -r requirements.txt
```

Everything is ready! You can look at the usage below and make a flashable firmware :)

## Usage

If you want to make flashable firmware just for a specific device, you can just use this command

```
python maker.py --git [DEVICE CODENAME] [MIUI VERSION]
```

or

```
python maker.py [DEVICE JSON FILE] [MIUI VERSION]
```

For example, you can create flashable firmware zip for capricorn from miui global dev version.

```
python maker.py --git capricorn global-dev
```

Also, you can use `python maker.py -h` to show arguments.

## Available Devices

You can see full list of the available devices [here](https://github.com/mifirmware/devices#available-devices).

## Available Miui Versions

```
global-stable
global-dev
china-stable
china-dev
```
