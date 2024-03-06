from ruuvitag import RuuviDaemon


def callback(tag, is_new=False):
    print(tag)


if __name__ == "__main__":
    import time

    # Initialize a RuuviDaemon instance with callback, that prints out the tag information
    ruuvidaemon = RuuviDaemon(callback=callback)
    # Start the daemon
    ruuvidaemon.start()

    try:
        # Start a busy-loop
        while True:
            time.sleep(5.0)
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt (ctrl-c) for clean shutdown
        pass
    finally:
        # Stop the daemon
        ruuvidaemon.stop()
