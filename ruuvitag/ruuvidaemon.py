import time
import threading

from bluepy import btle
from ruuvitag import RuuviTag


class RuuviDaemon(threading.Thread):
    class ScanDelegate(btle.DefaultDelegate):
        def __init__(self, daemon, *args, **kwargs):
            self.daemon = daemon
            # Use old style class to initialize, as that's required by btle ":D"
            btle.DefaultDelegate.__init__(self, *args, **kwargs)

        def handleDiscovery(self, device, is_new_device, is_new_data):
            self.daemon.update_tag(device)

    def __init__(self, interface_index=0, callback=None, *args, **kwargs):
        self.__stop = threading.Event()
        self.interface_index = interface_index
        self.callback_function = callback
        self.tags = {}
        self.__new_devices_found = threading.Event()
        super(RuuviDaemon, self).__init__(*args, **kwargs)

    def run(self):
        scanner = btle.Scanner().withDelegate(RuuviDaemon.ScanDelegate(self))
        scanner.start(passive=True)

        while not self.__stop.is_set():
            scanner.process(timeout=0.1)

        scanner.stop()

    def stop(self):
        self.__stop.set()

    def update_tag(self, device):
        try:
            tag = RuuviTag.parse(device.addr, device.rawData)
        except:
            tag = None

        if not tag:
            return

        is_new = False
        if tag.address not in self.tags:
            self.tags[tag.address] = tag
            is_new = True

        self.tags[tag.address].update(**tag.as_dict())
        self.callback(self.tags[tag.address], is_new=is_new)

    def callback(self, tag, is_new=False):
        if self.callback_function:
            self.callback_function(tag, is_new=is_new)
