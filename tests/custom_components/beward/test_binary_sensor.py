"""The tests for the Beward component binary sensor platform."""
import logging

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    DEVICE_CLASS_MOTION,
)
from homeassistant.const import CONF_BINARY_SENSORS, STATE_ON, STATE_OFF

from custom_components.beward.const import EVENT_DING, EVENT_MOTION, EVENT_ONLINE
from tests.custom_components.beward.common import setup_platform, TEST_DEVICE_ID

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)


async def test_binary_sensor(hass, requests_mock):
    """Test the binary sensors."""
    await setup_platform(
        hass,
        {CONF_BINARY_SENSORS: [EVENT_ONLINE, EVENT_DING, EVENT_MOTION]},
        requests_mock,
    )

    online_state = hass.states.get("binary_sensor.front_door_online")
    assert online_state is not None
    assert online_state.state == STATE_ON
    assert online_state.attributes["device_class"] == DEVICE_CLASS_CONNECTIVITY
    assert online_state.attributes["device_id"] == TEST_DEVICE_ID
    assert online_state.attributes["friendly_name"] == "Front Door Online"

    motion_state = hass.states.get("binary_sensor.front_door_motion")
    assert motion_state is not None
    assert motion_state.state == STATE_ON
    assert motion_state.attributes["device_class"] == DEVICE_CLASS_MOTION
    assert motion_state.attributes["device_id"] == TEST_DEVICE_ID
    assert motion_state.attributes["friendly_name"] == "Front Door Motion"

    ding_state = hass.states.get("binary_sensor.front_door_ding")
    assert ding_state is not None
    assert ding_state.state == STATE_OFF
    assert ding_state.attributes["device_id"] == TEST_DEVICE_ID
    assert ding_state.attributes["friendly_name"] == "Front Door Ding"
