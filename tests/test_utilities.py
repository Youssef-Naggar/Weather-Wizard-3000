from unittest.mock import patch, MagicMock
import pytest
import requests
from utilities import (
    convert_kelvin_to_celsius_fahrenheit,
    make_api_request,
    get_auto_location,
    DEFAULT_COORDINATES
)

# --- convert_kelvin_to_celsius_fahrenheit Tests ---

@pytest.mark.parametrize(
    "kelvin, expected_celsius, expected_fahrenheit",
    [
        (273.15, 0.0, 32.0),
        (373.15, 100.0, 212.0),
        (0.0, -273.15, -459.67),
    ]
)
def test_convert_kelvin_to_celsius_fahrenheit(kelvin, expected_celsius, expected_fahrenheit):
    c, f = convert_kelvin_to_celsius_fahrenheit(kelvin)
    assert pytest.approx(c) == expected_celsius
    assert pytest.approx(f) == expected_fahrenheit


# --- make_api_request Tests ---

@patch("utilities.requests.get")
def test_make_api_request_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"key": "value"}
    mock_get.return_value = mock_response

    result = make_api_request("https://fake-url.com", {"p": 1})

    mock_get.assert_called_once_with("https://fake-url.com", params={"p": 1}, timeout=10.0)
    assert result == {"key": "value"}


@patch("utilities.requests.get")
def test_make_api_request_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with pytest.raises(Exception) as excinfo:
        make_api_request("https://fake-url.com")
    
    assert "API request failed with status code 404" in str(excinfo.value)


# --- get_auto_location Tests ---

@patch("utilities.requests.get")
def test_get_auto_location_ipapi_success(mock_get):
    # Mock first provider ipapi.co succeeding
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"latitude": 10.0, "longitude": 20.0}
    mock_get.return_value = mock_response

    coords = get_auto_location()
    
    assert coords == [10.0, 20.0]


@patch("utilities.requests.get")
def test_get_auto_location_fallback_when_all_fail(mock_get):
    # Mock all HTTP calls throwing connection errors
    mock_get.side_effect = requests.RequestException("Connection failed")

    coords = get_auto_location()
    
    assert coords == DEFAULT_COORDINATES


@patch("utilities.requests.get")
def test_get_auto_location_provider_fail_over(mock_get):
    # Mock first provider returning 500, second succeeding (ip-api.com)
    response_fail = MagicMock()
    response_fail.status_code = 500

    response_success = MagicMock()
    response_success.status_code = 200
    response_success.json.return_value = {"status": "success", "lat": 30.0, "lon": 40.0}

    mock_get.side_effect = [response_fail, response_success]

    coords = get_auto_location()
    
    assert coords == [30.0, 40.0]


@patch("utilities.requests.get")
def test_get_auto_location_ipapi_fail_message(mock_get):
    # Test ip-api.com failure with "status": "fail"
    response_success_fail = MagicMock()
    response_success_fail.status_code = 200
    response_success_fail.json.return_value = {"status": "fail", "message": "query limit reached"}

    # ipapi.co fails, ip-api.com returns fail status, ipinfo.io succeeds
    response_ipapi = MagicMock()
    response_ipapi.status_code = 500

    response_ipinfo = MagicMock()
    response_ipinfo.status_code = 200
    response_ipinfo.json.return_value = {"loc": "50.0,60.0"}

    mock_get.side_effect = [response_ipapi, response_success_fail, response_ipinfo]

    coords = get_auto_location()
    
    assert coords == [50.0, 60.0]
