Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-radio/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/radio/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://travis-ci.com/adafruit/Adafruit_CircuitPython_radio.svg?branch=master
    :target: https://travis-ci.com/adafruit/Adafruit_CircuitPython_radio
    :alt: Build Status

This library provides simple byte and string based inter-device communication
via BLE.

It works like a walkie-talkie: configure your device to use a certain channel
(numbered 0-255, default being 42) and it will broadcast on that channel and
receive any messages from other devices using that channel.

Dependencies
=============

This library depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_.

Usage Example
=============

All the functionality is exposed via the very simple ``Radio`` class::

    from adafruit_radio import Radio


    # A radio instance listens/broadcasts on a numbered channel.
    r = Radio(channel=7)

    # Update radio instance settings.
    r.configure(channel=9)

    # Broadcast a simple string message.
    r.send("Hello")
    
    # Broadcast raw bytes.
    r.send_bytes(b"Hello")

    # A loop to listen for incoming string based messages...
    while True:
        msg = r.receive()
        if msg:
            print(msg)

    # Alternatively, to get the raw bytes and other details...
    while True:
        msg = r.receive_full()
        if msg:
            msg_bytes = msg[0]
            msg_strength = msg[1]
            msg_time = msg[2]
            print("Recieved {} (strength {}, at time {})".format(
                  msg_bytes,
                  msg_strength,
                  msg_time))

Unit Tests
==========

To run the test suite you should have ``pytest`` and ``pytest-coverage``
installed (``pip install pytest pytest-coverage``).

Run the unit tests with the following command::

    $ pytest --cov-report term-missing --cov=adafruit_radio tests/

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_radio/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
