import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OTPClient:
    def __init__(self, UserName: str, PassWord: str):
        self.client_id = UserName
        self.client_secret = PassWord
        self.token = None
        self.token_expiry = None
        self._token_fetched = False

    async def _fetch_token(self):
        url = "https://safir.bale.ai/api/v2/auth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "read"
        }

        logger.info("Requesting access token...")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                json_data = await resp.json()
                if resp.status == 200:
                    self.token = json_data.get("access_token")
                    expires_in = json_data.get("expires_in", 3600)
                    self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 30)
                    self._token_fetched = True
                    logger.info("Token acquired, expires at %s", self.token_expiry)
                else:
                    logger.error("Failed to get token: %s", json_data)
                    raise Exception(f"Token fetch failed: {json_data}")

    async def _ensure_token_valid(self):
        if not self._token_fetched or not self.token or datetime.now() >= self.token_expiry:
            logger.info("Token expired or not found. Refreshing token...")
            await self._fetch_token()

    async def _send_otp_async(self, phone: str, otp: int):
        await self._ensure_token_valid()

        url = "https://safir.bale.ai/api/v2/send_otp"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        json_data = {
            "phone": phone,
            "otp": otp
        }

        logger.info("Sending OTP to %s", phone)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=json_data) as resp:
                try:
                    response = await resp.json()
                    if resp.status == 200:
                        logger.info("OTP sent successfully")
                    else:
                        logger.warning("OTP send failed: %s", response)
                    return response
                except Exception:
                    msg = await resp.text()
                    logger.error("Unexpected error: %s", msg)
                    return {"error": f"HTTP {resp.status}", "message": msg}

    def send_otp(self, phone: str, otp: int):
        try:
            loop = asyncio.get_running_loop()
            return asyncio.ensure_future(self._send_otp_async(phone, otp))
        except RuntimeError:
            return asyncio.run(self._send_otp_async(phone, otp))
