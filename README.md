# Mi Firmware

Mi Firmware, purposes can create easily flashable xiaomi firmware.

## Getting Started

* You should use latest Python 3 release.

First, you have to clone [this repo](https://github.com/ardadem/xiaomi-flashable-firmware-creator) in same folder with maker.

Then you can run it.

```
python maker.py [DEVICE CODENAME] [MIUI VERSION]
```

Example, you can create flashable firmware zip for capricorn from miui global dev version.

```
python maker.py capricorn global-dev
```

Also, you can use `python maker.py -h` to show arguments.

### Available Devices;

You can see from [this repo.](https://github.com/mifirmware/devices)

### Available Miui Versions;

```
global-stable
global-dev
china-stable
china-dev
```
