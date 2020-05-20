"""The tests for the Beward component."""
import unittest
from unittest.mock import patch

import requests_mock
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_NAME

from custom_components import beward
from custom_components.beward import DOMAIN
from tests.common import get_test_home_assistant, load_fixture
from tests.custom_components.beward.common import BewardMock, TEST_DEVICE_ID


class TestBeward(unittest.TestCase):
    """Tests the Beward component."""

    def setUp(self):
        """Initialize values for this test case class."""
        self.hass = get_test_home_assistant()

    def tearDown(self):  # pylint: disable=invalid-name
        """Stop everything that was started."""
        self.hass.stop()

    @requests_mock.Mocker()
    def test_setup(self, mock):
        """Test the setup."""
        mock.get(
            "http://192.168.0.1:80/cgi-bin/systeminfo_cgi",
            text=load_fixture("beward/systeminfo.txt"),
        )

        with patch("beward.Beward", BewardMock), patch(
            "beward.BewardCamera.live_image"
        ), patch("custom_components.beward.BewardController._cache_image"):
            response = beward.setup(
                self.hass,
                {
                    DOMAIN: [
                        {
                            CONF_HOST: "192.168.0.1",
                            CONF_USERNAME: "user",
                            CONF_PASSWORD: "password",
                        }
                    ],
                },
            )
        assert response
        assert self.hass.data[DOMAIN].get("Beward " + TEST_DEVICE_ID)

        with patch("beward.Beward", BewardMock), patch(
            "beward.BewardCamera.live_image"
        ), patch("custom_components.beward.BewardController._cache_image"):
            response = beward.setup(
                self.hass,
                {
                    DOMAIN: [
                        {
                            CONF_HOST: "192.168.0.1",
                            CONF_USERNAME: "user",
                            CONF_PASSWORD: "password",
                            CONF_NAME: "Front Door",
                        }
                    ],
                },
            )
        assert response
        assert self.hass.data[DOMAIN].get("Front Door")
