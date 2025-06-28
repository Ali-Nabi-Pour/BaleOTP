import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging
import re
import random
from typing import Optional, Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TokenError(Exception):
    """Base class for token related errors"""
    pass


class InvalidClientError(TokenError):
    """Invalid authentication credentials"""
    pass


class BadRequestError(TokenError):
    """Invalid or incomplete parameters"""
    pass


class ServerError(TokenError):
    """Server related errors"""
    pass


class OTPError(Exception):
    """Base class for OTP related errors"""
    pass


class InvalidPhoneNumberError(OTPError):
    """Invalid phone number format"""
    pass


class UserNotFoundError(OTPError):
    """User not found"""
    pass


class InsufficientBalanceError(OTPError):
    """Insufficient balance"""
    pass


class RateLimitExceededError(OTPError):
    """Rate limit exceeded"""
    pass


class UnexpectedResponseError(OTPError):
    """Unexpected response from server"""
    pass


class OTPResult:
    """Container for OTP result with code and response data"""

    def __init__(self, code: int, response: dict):
        self.code = code
        self.response = response

    def __repr__(self):
        return f"OTPResult(code={self.code}, response={self.response})"


class OTPClient:
    """Client for sending OTP codes via Bale.ai API"""

    def __init__(
            self,
            username: str,
            password: str,
            base_url: str = "https://safir.bale.ai"
    ):
        """
        Initialize OTP client.

        Args:
            username: API username/client_id
            password: API password/client_secret
            base_url: Base API URL (default: https://safir.bale.ai)
        """
        self.client_id = username
        self.client_secret = password
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.token_expiry = None
        self._token_fetched = False

    def _normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number to standard format (+98XXXXXXXXXX)

        Args:
            phone: Input phone number in various formats

        Returns:
            Normalized phone number in +98XXXXXXXXXX format
        """
        phone = phone.strip()

        # Remove all non-digit characters except +
        phone = re.sub(r"[^\d+]", "", phone)

        # Handle different phone number formats
        if phone.startswith("98") and len(phone) == 12:
            return phone
        if phone.startswith("0") and len(phone) == 11:
            return "98" + phone[1:]
        if phone.startswith("98") and len(phone) == 12:
            return phone
        if len(phone) == 10:
            return "98" + phone

        return phone

    async def _fetch_token(self) -> None:
        """Fetch authentication token from API"""
        url = f"{self.base_url}/api/v2/auth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "read"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                try:
                    try:
                        json_data = await resp.json()
                    except aiohttp.ContentTypeError:
                        json_data = await resp.text()

                    if resp.status == 200 and isinstance(json_data, dict):
                        self.token = json_data.get("access_token")
                        expires_in = json_data.get("expires_in", 3600)
                        self.token_expiry = datetime.now() + timedelta(
                            seconds=expires_in - 30
                        )
                        self._token_fetched = True
                        logger.info(
                            "Token acquired, expires at %s",
                            self.token_expiry
                        )
                        return

                    if resp.status == 401:
                        raise InvalidClientError(
                            json_data.get("error_description")
                            if isinstance(json_data, dict)
                            else str(json_data)
                        )
                    if resp.status == 400:
                        raise BadRequestError(str(json_data))
                    if resp.status == 500:
                        raise ServerError(
                            json_data.get("message")
                            if isinstance(json_data, dict)
                            else "Internal server error"
                        )

                    raise TokenError(
                        f"Unexpected status {resp.status}: {json_data}"
                    )

                except TokenError:
                    raise
                except Exception as e:
                    raise TokenError(f"Token fetch failed: {e}")
                except aiohttp.ContentTypeError:
                    msg = await resp.text()
                    raise TokenError(f"Invalid response format (non-JSON): {msg}")

    async def _ensure_token_valid(self) -> None:
        """Ensure we have a valid token, fetching a new one if needed"""
        if (
                not self._token_fetched
                or not self.token
                or datetime.now() >= self.token_expiry
        ):
            await self._fetch_token()

    def _generate_random_otp(self) -> int:
        """Generate a random 6-digit OTP code"""
        return random.randint(100000, 999999)

    async def _send_otp_async(
            self,
            phone: str,
            otp: Optional[Union[int, str]] = None
    ) -> OTPResult:
        """
        Send OTP code asynchronously

        Args:
            phone: Phone number to send OTP to
            otp: OTP code (optional, will generate if not provided)

        Returns:
            OTPResult object containing code and full response
        """
        await self._ensure_token_valid()
        phone = self._normalize_phone(phone)

        # Generate OTP if not provided
        if otp is None:
            otp = self._generate_random_otp()
        elif isinstance(otp, str):
            otp = int(otp)

        url = f"{self.base_url}/api/v2/send_otp"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        json_data = {
            "phone": phone,
            "otp": otp
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=json_data) as resp:
                try:
                    response = await resp.json()
                    if resp.status == 200:
                        return OTPResult(code=otp, response=response)
                    elif resp.status == 400:
                        if response.get("code") == 8:
                            raise InvalidPhoneNumberError(response.get("message"))
                        elif response.get("code") == 20:
                            raise InsufficientBalanceError(response.get("message"))
                        elif response.get("code") == 18:
                            raise RateLimitExceededError(response.get("message"))
                        else:
                            raise OTPError(response.get("message", "Bad request"))
                    elif resp.status == 404:
                        raise UserNotFoundError(response.get("message"))
                    elif resp.status == 402:
                        raise InsufficientBalanceError(response.get("message"))
                    elif resp.status == 500:
                        raise ServerError(
                            response.get("message", "Internal server error occurred")
                        )
                    else:
                        raise UnexpectedResponseError(
                            f"Unexpected status code: {resp.status}, "
                            f"message: {response}"
                        )
                except aiohttp.ContentTypeError:
                    msg = await resp.text()
                    raise UnexpectedResponseError(f"Non-JSON response: {msg}")

    def send_otp(
            self,
            phone: str,
            otp: Optional[Union[int, str]] = None
    ) -> Union[asyncio.Future, OTPResult]:
        """
        Send OTP code (synchronous wrapper)

        Args:
            phone: Phone number to send OTP to
            otp: OTP code (optional, will generate if not provided)

        Returns:
            OTPResult object containing code and full response
        """
        try:
            loop = asyncio.get_running_loop()
            return asyncio.ensure_future(self._send_otp_async(phone, otp))
        except RuntimeError:
            return asyncio.run(self._send_otp_async(phone, otp))