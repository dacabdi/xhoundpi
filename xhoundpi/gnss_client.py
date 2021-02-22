""" GNSS client """

from io import BytesIO



class GnssClient():
    """ Gnss client implementation facade """

    # TODO pass control wire
    def __init__(self, serial):
        self.serial = serial

    def read(self, size=1):
        """ Read n bytes from GNSS serial iface """
        return self.serial.read(size)

    def write(self, data):
        """ Write n bytes to GNSS serial iface """
        return self.serial.write(data)
