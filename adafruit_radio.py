# The MIT License (MIT)
#
# Copyright (c) 2019 Nicholas H.Tollervey for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_radio`
================================================================================

Simple byte and string based inter-device communication via BLE.


* Author(s): Nicholas H.Tollervey for Adafruit Industries

Implementation Notes
--------------------

**Hardware:**

   Adafruit Feather nRF52840 Express <https://www.adafruit.com/product/4062>
   Adafruit Circuit Playground Bluefruit <https://www.adafruit.com/product/4333>

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import time
import struct
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitRadio


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_radio.git"


#: Maximum length of a message (in bytes).
MAX_LENGTH = 22


class Radio:
    """
    Represents a connection through which one can send or receive strings
    and bytes. The radio can be tuned to a specific channel upon initialisation
    or via the `configure` method.
    """

    def __init__(self, **args):
        """
        Takes the same configuration arguments as the `configure` method.
        """
        self.ble = BLERadio()
        self.configure(**args)

    def configure(self, channel=7):
        """
        Set configuration values for the radio.

        :param int channel: The channel (0-255) the radio is listening /
            broadcasting on.
        """
        if 0 <= channel < 256:
            self.channel = channel
        else:
            raise ValueError("Channel must be in range 0-255")

    def send(self, message):
        """
        Send a message string on the channel to which the radio is
        broadcasting.

        :param str message: The message string to broadcast.
        """
        return self.send_bytes(message.encode("utf-8"))

    def send_bytes(self, message):
        """
        Send bytes on the channel to which the radio is broadcasting.

        :param bytes message: The bytes to broadcast.
        """
        if len(message) > MAX_LENGTH:
            raise ValueError(
                "Message too long (max length = {})".format(MAX_LENGTH)
            )
        advertisement = AdafruitRadio()
        advertisement.msg = struct.pack("<B", self.channel) + message 
        self.ble.start_advertising(advertisement)
        time.sleep(0.5)  # Hmm... blocking..??
        self.ble.stop_advertising()

    def receive(self):
        """
        Returns a message received on the channel on which the radio is
        listening.

        :return: A string representation of the received message.
        """
        msg = self.receive_full()
        if msg:
            return msg[0].decode("utf-8")
        else:
            return None

    def receive_full(self):
        """
        Returns a tuple containing three values representing a message received
        on the channel on which the radio is listening. If no message was
        received then `None` is returned.

        The three values in the tuple represent:

        * the bytes received.
        * the RSSI (signal strength: 0 = max, -255 = min).
        * a microsecond timestamp: the value returned by time.ticks_us() when
          the message was received.

        :return: A tuple representation of the received message, or else None.
        """
        try:
            for entry in self.ble.start_scan(
                    AdafruitRadio, minimum_rssi=-255, timeout=1
                ):
                channel = struct.unpack("<B", entry.msg[:1])[0]
                msg = entry.msg[1:]
                if channel == self.channel:
                    now = time.monotonic()
                    return (msg, entry.rssi, now)
        finally:
            self.ble.stop_scan()
        return None
