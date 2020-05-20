"""The tests for the Beward component sensor platform."""
import logging

from homeassistant.const import (
    CONF_SENSORS,
    DEVICE_CLASS_TIMESTAMP,
    STATE_UNKNOWN,
)

from custom_components.beward.sensor import (
    SENSOR_LAST_ACTIVITY,
    SENSOR_LAST_MOTION,
    SENSOR_LAST_DING,
)
from tests.custom_components.beward.common import (
    setup_platform,
    TEST_TIMESTAMP_STR,
    TEST_DEVICE_ID,
)

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)


async def test_sensor(hass, requests_mock):
    """Test the sensors."""
    await setup_platform(
        hass,
        {CONF_SENSORS: [SENSOR_LAST_ACTIVITY, SENSOR_LAST_MOTION, SENSOR_LAST_DING]},
        requests_mock,
    )

    activity_state = hass.states.get("sensor.front_door_last_activity")
    assert activity_state is not None
    assert activity_state.state == TEST_TIMESTAMP_STR
    assert activity_state.attributes["device_class"] == DEVICE_CLASS_TIMESTAMP
    assert activity_state.attributes["device_id"] == TEST_DEVICE_ID
    assert activity_state.attributes["friendly_name"] == "Front Door Last Activity"

    motion_state = hass.states.get("sensor.front_door_last_motion")
    assert motion_state is not None
    assert motion_state.state == TEST_TIMESTAMP_STR
    assert motion_state.attributes["device_class"] == DEVICE_CLASS_TIMESTAMP
    assert motion_state.attributes["device_id"] == TEST_DEVICE_ID
    assert motion_state.attributes["friendly_name"] == "Front Door Last Motion"

    ding_state = hass.states.get("sensor.front_door_last_ding")
    assert ding_state is not None
    assert ding_state.state == STATE_UNKNOWN
    assert ding_state.attributes["device_class"] == DEVICE_CLASS_TIMESTAMP
    assert ding_state.attributes["device_id"] == TEST_DEVICE_ID
    assert ding_state.attributes["friendly_name"] == "Front Door Last Ding"
