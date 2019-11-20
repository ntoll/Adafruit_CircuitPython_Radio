"""
Simple unit tests for the adafruit_radio module. Uses experimental mocking
found in the testconf.py file. See comments therein for explanation of how it
works.
"""
import adafruit_radio
import pytest
import struct
import time
from unittest import mock


@pytest.fixture
def radio():
    """
    A fixture to recreate a new Radio instance for each test that needs it.
    """
    return adafruit_radio.Radio()


def test_radio_init_default():
    """
    Ensure a Radio object is initialised in the expected way:

    * It has a BLERadio instance.
    * The self.uid counter is set to 0.
    * The self.msg_pool is initialised as an empty set.
    * The channel is set to the default 42.
    """
    r = adafruit_radio.Radio()
    assert r.ble == adafruit_radio.BLERadio()
    assert r.uid == 0
    assert r.msg_pool == set()
    assert r._channel == 42


def test_radio_init_channel():
    """
    If a channel argument is passed to initialisation, this is correctly set.
    """
    r = adafruit_radio.Radio(channel=7)
    assert r._channel == 7


def test_radio_configure_channel(radio):
    """
    If a valid channel argument is passed to the configure method, the Radio
    instance's channel is updated to reflect this.
    """
    assert radio._channel == 42
    radio.configure(channel=7)
    assert radio._channel == 7


def test_radio_configure_channel_out_of_bounds(radio):
    """
    If a channel not in the range 0-255 is passed into the configure method,
    then a ValueError exception is raised.
    """
    with pytest.raises(ValueError):
        radio.configure(channel=-1)
    with pytest.raises(ValueError):
        radio.configure(channel=256)
    # Add just-in-bounds checks too.
    radio.configure(channel=0)
    assert radio._channel == 0
    radio.configure(channel=255)
    assert radio._channel == 255


def test_radio_send(radio):
    """
    The send method merely encodes to bytes and calls send_bytes.
    """
    radio.send_bytes = mock.MagicMock()
    msg = "Testing 1, 2, 3..."
    radio.send(msg)
    radio.send_bytes.assert_called_once_with(msg.encode("utf-8"))


def test_radio_send_bytes_too_long(radio):
    """
    A ValueError is raised if the message to be sent is too long (defined by
    MAX_LENGTH).
    """
    msg = bytes(adafruit_radio.MAX_LENGTH + 1)
    with pytest.raises(ValueError):
        radio.send_bytes(msg)


def test_radio_send_bytes(radio):
    """
    Ensure the expected message is set on an instance of AdafruitRadio, and
    broadcast for AD_DURATION period of time.
    """
    radio.uid = 255  # set up for cycle back to 0.
    msg = b"Hello"
    with mock.patch("adafruit_radio.time.sleep") as mock_sleep:
        radio.send_bytes(msg)
        mock_sleep.assert_called_once_with(adafruit_radio.AD_DURATION)
    spy_advertisement = adafruit_radio.AdafruitRadio()
    chan = struct.pack("<B", radio._channel)
    uid = struct.pack("<B", 255)
    assert spy_advertisement.msg == chan + uid + msg
    radio.ble.start_advertising.assert_called_once_with(spy_advertisement)
    radio.ble.stop_advertising.assert_called_once_with()
    assert radio.uid == 0


def test_radio_receive_no_message(radio):
    """
    If no message is received from the receive_bytes method, then None is
    returned.
    """
    radio.receive_full = mock.MagicMock(return_value=None)
    assert radio.receive() is None
    radio.receive_full.assert_called_once_with()


def test_radio_receive(radio):
    """
    If bytes are received from the receive_bytes method, these are decoded
    using utf-8 and returned as a string with null characters stripped from the
    end.
    """
    # Return value contains message bytes, RSSI (signal strength), timestamp.
    msg = b"testing 1, 2, 3\x00\x00\x00\x00\x00\x00"
    radio.receive_full = mock.MagicMock(return_value=(msg, -20, 1.2))
    assert radio.receive() == "testing 1, 2, 3"


def test_radio_receive_full_no_messages(radio):
    """
    If no messages are detected by receive_full then it returns None.
    """
    radio.ble.start_scan.return_value = []
    assert radio.receive_full() is None
    radio.ble.start_scan.assert_called_once_with(adafruit_radio.AdafruitRadio,
                                                 minimum_rssi=-255, timeout=1)
    radio.ble.stop_scan.assert_called_once_with()


def test_radio_receive_full_duplicate_message(radio):
    """
    If a duplicate message is detected, then receive_full returns None
    (indicating no *new* messages received).
    """
    mock_entry = mock.MagicMock()
    mock_entry.msg = b"*\x00Hello"
    mock_entry.address.address_bytes = b"addr"
    mock_entry.rssi = -40
    radio.ble.start_scan.return_value = [mock_entry]
    radio.msg_pool.add((time.monotonic(), 42, 0, b"addr"))
    assert radio.receive_full() is None


def test_radio_receive_full_and_remove_expired_message_metadata(radio):
    """
    Return the non-duplicate message.

    Ensure that expired message metadata (used to detect duplicate messages
    within a short time window) is purged from the self.msg_pool cache.

    Ensure the metadata from the new message is now in the self.msg_pool cache.
    """
    mock_entry = mock.MagicMock()
    mock_entry.msg = b"*\x01Hello"
    mock_entry.address.address_bytes = b"adr2"
    mock_entry.rssi = -40
    radio.ble.start_scan.return_value = [mock_entry]
    radio.msg_pool.add(
        (time.monotonic() - adafruit_radio.AD_DURATION - 1, 42, 0, b"addr")
    )
    result = radio.receive_full()
    assert result[0] == b"Hello"
    assert result[1] == -40
    assert len(radio.msg_pool) == 1
    metadata = radio.msg_pool.pop()
    assert metadata[1] == 42
    assert metadata[2] == 1
    assert metadata[3] == b"adr2"
