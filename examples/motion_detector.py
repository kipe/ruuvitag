from ruuvitag import RuuviDaemon

# Subclass the RuuviDaemon to provide additional functionalities
class MotionDetector(RuuviDaemon):
    # Override callback to provide the functionality
    def callback(self, tag, is_new=False):
        # If a new tag is found
        if is_new:
            # ... print event information
            print('New tag detected!', tag)
            if tag.protocol < 5:
                print('... however, the RuuviTag needs to be updated to support ' + \
                      'protocol version 5 to function as a motion detector')
        # If movement is detected
        if tag.movement_detected.is_set():
            # ... print event information
            print('Movement detected!', tag, tag.movement_counter)
            # and clear the event, so subsequent movements are detected correctly
            tag.movement_detected.clear()


if __name__ == '__main__':
    import time

    # Initialize our custom daemon and start it
    motiondetector = MotionDetector()
    motiondetector.start()

    try:
        while True:
            time.sleep(5.0)
    except KeyboardInterrupt:
        pass
    finally:
        motiondetector.stop()
