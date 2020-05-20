"""The tests for the Beward component camera platform."""
import logging

from homeassistant.const import STATE_IDLE

from custom_components.beward.camera import (
    CAMERA_LIVE,
    CAMERA_LAST_MOTION,
    CAMERA_LAST_DING,
)
from custom_components.beward.const import CONF_CAMERAS, ATTRIBUTION
from tests.custom_components.beward.common import setup_platform, TEST_DEVICE_ID

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)


async def test_attributes(hass, requests_mock):
    """Test the camera attributes are correct."""
    await setup_platform(
        hass,
        {CONF_CAMERAS: [CAMERA_LIVE, CAMERA_LAST_MOTION, CAMERA_LAST_DING]},
        requests_mock,
    )

    live_camera = hass.states.get("camera.front_door_live")
    assert live_camera is not None
    assert live_camera.state == STATE_IDLE
    assert live_camera.attributes["attribution"] == ATTRIBUTION
    assert live_camera.attributes["device_id"] == TEST_DEVICE_ID
    assert live_camera.attributes["friendly_name"] == "Front Door Live"

    motion_camera = hass.states.get("camera.front_door_last_motion")
    assert motion_camera is not None
    assert motion_camera.state == STATE_IDLE
    assert motion_camera.attributes["friendly_name"] == "Front Door Last Motion"

    ding_camera = hass.states.get("camera.front_door_last_ding")
    assert ding_camera is not None
    assert ding_camera.state == STATE_IDLE
    assert ding_camera.attributes["friendly_name"] == "Front Door Last Ding"
