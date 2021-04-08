# Bluetooth tooling
## Notes
The `pybluez` library leverages the fact that every bluetooth connection is generalized as simply socket programming. There are two underlying socket implementations that can be used with the Python library `pybluez`: `RFCOMM` and `L2CAP`. The main superficial difference between the two protocols is the port selection and the datagram length, where `L2CAP` forces a maximum size (default is 672 bytes but the MTU can be negotiated by the parties up to 65535 bytes).

## Known issues
### Linux
If the installation of the `PyBluez` dependency fails to find the `Python.h` or `bluetooth.h` headers. Please install `$ sudo apt install libbluetooth-dev python3.9-dev`. If `apt` fails to resolve the `python3.9` related packages, please follow this [guide](https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/).
