import threading

from ruuvitag import RuuviTag


def _scan_delegate(btle):
    """Build the bluepy delegate once bluepy has been imported."""

    class ScanDelegate(btle.DefaultDelegate):
        """
        Custom delegate to receive btle scan results,
        used internally to notify RuuviDaemon.
        """

        def __init__(self, daemon, *args, **kwargs):
            self.daemon = daemon
            # Use old style class to initialize,
            # as that's required by btle ":D"
            btle.DefaultDelegate.__init__(self, *args, **kwargs)

        def handleDiscovery(self, device, is_new_device, is_new_data):
            """Call update_tag method from RuuviDaemon."""
            self.daemon.update_tag(device)

    return ScanDelegate


class RuuviDaemon(threading.Thread):
    """A threaded scanner for RuuviTags."""

    def __init__(self, interface_index=0, callback=None, *args, **kwargs):
        self.__stop = threading.Event()
        self.interface_index = interface_index
        self.callback_function = callback
        self.tags = {}
        self.__new_devices_found = threading.Event()
        super(RuuviDaemon, self).__init__(*args, **kwargs)

    def run(self):
        """Main-loop of the daemon, started via daemon.start()."""
        # Imported here so importing the package does not need bluepy.
        from bluepy import btle

        scanner = btle.Scanner().withDelegate(_scan_delegate(btle)(self))
        scanner.start(passive=True)

        while not self.__stop.is_set():
            scanner.process(timeout=0.1)

        scanner.stop()

    def stop(self):
        """Used to stop the (running) daemon."""
        self.__stop.set()

    def update_tag(self, device):
        """Updates the RuuviTag, based on the information received from
        ScanDelegate.handleDiscovery."""
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
        """Callback to run when a broadcast from a RuuviTag has been
        received."""
        if self.callback_function:
            self.callback_function(tag, is_new=is_new)
