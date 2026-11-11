from main import api_call
import pytest

def test_api_call(mocker):
    mock_get = mocker.patch("main.requests.get")
    mock_get.return_value.json.return_value = {"key": "value"}

    result = api_call("https://example.com")
    assert result == {"data": {"key": "value"}}