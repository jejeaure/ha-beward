"""Common methods used across tests for Beward component."""
import logging
from datetime import datetime
from unittest.mock import patch

import homeassistant.util.dt as dt_util
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_NAME
from homeassistant.setup import async_setup_component

from beward import Beward, BewardDoorbell
from beward.const import ALARM_MOTION, ALARM_ONLINE
from custom_components.beward import DOMAIN
from tests.common import load_fixture

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

# logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)

TEST_TIMESTAMP = datetime.now()
TEST_TIMESTAMP_STR = dt_util.as_local(TEST_TIMESTAMP.replace(microsecond=0)).isoformat()

TEST_DEVICE_ID = "1692"


class BewardDoorbellMock(BewardDoorbell):
    """Mock for BewardDoorbell class."""

    def listen_alarms(self, channel: int = 0, alarms=None):
        """Mock for listen_alarms method."""
        self._handle_alarm(TEST_TIMESTAMP, ALARM_ONLINE, True)
        self._handle_alarm(TEST_TIMESTAMP, ALARM_MOTION, True)


class BewardMock(Beward):
    """Mock for Beward class."""

    @staticmethod
    def factory(host_ip, username, password, **kwargs):
        """Mock for factory method."""
        return BewardDoorbellMock(host_ip, username, password, **kwargs)


async def setup_platform(hass, config, mock):
    """Set up the Beward platform."""
    default_config = {
        CONF_HOST: "192.168.0.1",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "password",
        CONF_NAME: "Front Door",
    }
    default_config.update(config)
    _LOGGER.debug(default_config)

    mock.get(
        "http://192.168.0.1:80/cgi-bin/systeminfo_cgi",
        text=load_fixture("beward/systeminfo.txt"),
    )
    mock.get(
        "http://192.168.0.1:80/cgi-bin/rtsp_cgi", text=load_fixture("beward/rtsp.txt"),
    )

    with patch("beward.Beward", BewardMock), patch(
        "beward.BewardCamera.live_image"
    ), patch("custom_components.beward.BewardController._cache_image"):
        assert await async_setup_component(hass, DOMAIN, {DOMAIN: [default_config]})
    await hass.async_block_till_done()
