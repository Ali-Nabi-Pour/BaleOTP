import pytest
import asyncio
from aiohttp import ClientResponseError
from unittest.mock import patch, AsyncMock, MagicMock

from baleotp import OTPClient
from baleotp.exceptions import (
    AuthenticationError, BadRequestError, NotFoundError,
    PaymentRequiredError, RateLimitExceededError, InternalServerError
)


@pytest.mark.asyncio
async def test_fetch_token_success():
    client = OTPClient("Your_UserName", "Your_PassWord")

    with patch.object(client._http_session, 'post', new_callable=AsyncMock) as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "access_token": "fake_token",
            "expires_in": 3600
        })
        mock_post.return_value.__aenter__.return_value = mock_response

        await client._fetch_token()
        assert client._token == "fake_token"
        assert client._token_expiry is not None


@pytest.mark.asyncio
async def test_send_otp_success():
    client = OTPClient("test_id", "test_secret")
    client._token = "fake_token"
    client._token_expiry = 9999999999

    with patch.object(client._http_session, 'post', new_callable=AsyncMock) as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "ok"})
        mock_post.return_value.__aenter__.return_value = mock_response

        response = await client._send_otp_async("09123456789", 1234)
        assert response["status"] == "ok"


@pytest.mark.parametrize("status, error_class", [
    (401, AuthenticationError),
    (400, BadRequestError),
    (404, NotFoundError),
    (402, PaymentRequiredError),
    (429, RateLimitExceededError),
    (500, InternalServerError),
])
@pytest.mark.asyncio
async def test_error_handling(status, error_class):
    client = OTPClient("id", "secret")

    with patch.object(client._http_session, 'post', new_callable=AsyncMock) as mock_post:
        mock_response = AsyncMock()
        mock_response.status = status
        mock_response.json = AsyncMock(return_value={"message": "Error", "error_description": "Unauthorized"})
        mock_post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(error_class):
            await client._fetch_token()


@pytest.mark.asyncio
async def test_normalize_phone():
    client = OTPClient("id", "secret")
    assert client._normalize_phone("09123456789") == "989123456789"
    assert client._normalize_phone("+989123456789") == "989123456789"
    assert client._normalize_phone("00989123456789") == "989123456789"
