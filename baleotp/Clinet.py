# import aiohttp
# import asyncio
# from datetime import datetime, timedelta
# import logging
# import re
#
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
#
#
# class OTPClient:
#     def __init__(self,
#                  UserName: str,
#                  PassWord: str,
#                  base_url: str = "https://safir.bale.ai"
#                  ):
#         """
#         ساخت کلاینت برای ارسال OTP
#         """
#         self.client_id = UserName
#         self.client_secret = PassWord
#         self.base_url = base_url.rstrip("/")
#         self.token = None
#         self.token_expiry = None
#         self._token_fetched = False
#
#     async def _fetch_token(self):
#         """
#         دریافت توکن از سرویس دهنده
#         """
#         url = f"{self.base_url}/api/v2/auth/token"
#         data = {
#             "grant_type": "client_credentials",
#             "client_id": self.client_id,
#             "client_secret": self.client_secret,
#             "scope": "read"
#         }
#
#         logger.info("Requesting access token...")
#         async with aiohttp.ClientSession() as session:
#             async with session.post(url, data=data) as resp:
#                 json_data = await resp.json()
#                 if resp.status == 200:
#                     self.token = json_data.get("access_token")
#                     expires_in = json_data.get("expires_in", 3600)
#                     self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 30)
#                     self._token_fetched = True
#                     logger.info("Token acquired, expires at %s", self.token_expiry)
#                 else:
#                     logger.error("Failed to get token: %s", json_data)
#                     raise Exception(f"Token fetch failed: {json_data}")
#
#     async def _ensure_token_valid(self):
#         """
#         بررسی میکنه که آیا توکن منقضی شده؟
#         در صورت انقضاء توکن جدید جایگزین میشه
#         """
#         if not self._token_fetched or not self.token or datetime.now() >= self.token_expiry:
#             logger.info("Token expired or not found. Refreshing token...")
#             await self._fetch_token()
#
#     def _normalize_phone(self,
#                          phone: str) -> str:
#         """
#         شماره تلفن ورودی را به فرمت استاندارد +98XXXXXXXXXX تبدیل می‌کند.
#         فرض می‌کنیم شماره موبایل ایران است.
#         """
#         phone = phone.strip()
#
#         # حذف هر کاراکتر غیر رقمی به جز +
#         phone = re.sub(r"[^\d+]", "", phone)
#
#         # اگر شماره با 98 شروع شده، قبول کن
#         if phone.startswith("98") and len(phone) == 12:
#             return phone
#
#         # اگر شماره با ۰ شروع شده، ۰ را به ۹۸ تبدیل کن
#         if phone.startswith("0") and len(phone) == 11:
#             return "98" + phone[1:]
#
#         # اگر شماره با ۹۸ شروع شده و طولش 12 است، همان را بازگردان
#         if phone.startswith("98") and len(phone) == 12:
#             return phone
#
#         # اگر فقط شماره ۱۰ رقمی بدون ۰ و کد کشور است، فرض کنیم شماره موبایل است و +98 اضافه کنیم
#         if len(phone) == 10:
#             return "98" + phone
#
#         # در غیر این صورت همان شماره را بازگردان (برای شماره‌های غیر استاندارد)
#         return phone
#
#     async def _send_otp_async(self,
#                               phone: str,
#                               otp: int
#                               ):
#         await self._ensure_token_valid()
#
#         url = f"{self.base_url}/api/v2/send_otp"
#         phone = self._normalize_phone(phone)
#
#         headers = {
#             "Authorization": f"Bearer {self.token}",
#             "Content-Type": "application/json"
#         }
#         json_data = {
#             "phone": phone,
#             "otp": otp
#         }
#
#         logger.info("Sending OTP to %s", phone)
#
#         async with aiohttp.ClientSession() as session:
#             async with session.post(url, headers=headers, json=json_data) as resp:
#                 try:
#                     response = await resp.json()
#                     if resp.status == 200:
#                         logger.info("OTP sent successfully")
#                     else:
#                         logger.warning("OTP send failed: %s", response)
#                     return response
#                 except Exception:
#                     msg = await resp.text()
#                     logger.error("Unexpected error: %s", msg)
#                     return {"error": f"HTTP {resp.status}", "message": msg}
#
#     def send_otp(self,
#                  phone: str,
#                  otp: int | str
#                  ):
#         """
#         ارسال کننده کد OTP
#         """
#         if isinstance(otp, str):
#             otp = int(otp)
#         try:
#             loop = asyncio.get_running_loop()
#             return asyncio.ensure_future(self._send_otp_async(phone, otp))
#         except RuntimeError:
#             return asyncio.run(self._send_otp_async(phone, otp))
import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# خطا های مربوط به درخواست توکن
class TokenError(Exception):
    pass


# خطای احراز هویت نامعتبر
class InvalidClientError(TokenError):
    pass


# خطای پارامترهای ناقص یا اشتباه
class BadRequestError(TokenError):
    pass


# خطای سرور
class ServerError(TokenError):
    pass


# خطا های مربوط به ارسال OTP
class OTPError(Exception):
    pass


# خطای شماره تلفن نامعتبر
class InvalidPhoneNumberError(OTPError):
    pass


# خطای کاربر پیدا نشد
class UserNotFoundError(OTPError):
    pass


# خطای عدم موجودی کافی
class InsufficientBalanceError(OTPError):
    pass


# خطای داخلی سرور
class RateLimitExceededError(OTPError):
    pass


# خطا های غیر منتظره
class UnexpectedResponseError(OTPError):
    pass


class OTPClient:
    def __init__(self,
                 UserName: str,
                 PassWord: str,
                 base_url: str = "https://safir.bale.ai"):
        self.client_id = UserName
        self.client_secret = PassWord
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.token_expiry = None
        self._token_fetched = False

    def _normalize_phone(self,
                         phone: str) -> str:
        """
        شماره تلفن ورودی را به فرمت استاندارد +98XXXXXXXXXX تبدیل می‌کند.
        فرض می‌کنیم شماره موبایل ایران است.
        """
        phone = phone.strip()

        # حذف هر کاراکتر غیر رقمی به جز +
        phone = re.sub(r"[^\d+]", "", phone)

        # اگر شماره با 98 شروع شده، قبول کن
        if phone.startswith("98") and len(phone) == 12:
            return phone

        # اگر شماره با ۰ شروع شده، ۰ را به ۹۸ تبدیل کن
        if phone.startswith("0") and len(phone) == 11:
            return "98" + phone[1:]

        # اگر شماره با ۹۸ شروع شده و طولش 12 است، همان را بازگردان
        if phone.startswith("98") and len(phone) == 12:
            return phone

        # اگر فقط شماره ۱۰ رقمی بدون ۰ و کد کشور است، فرض کنیم شماره موبایل است و +98 اضافه کنیم
        if len(phone) == 10:
            return "98" + phone

        # در غیر این صورت همان شماره را بازگردان (برای شماره‌های غیر استاندارد)
        return phone

    async def _fetch_token(self):
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
                        self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 30)
                        self._token_fetched = True
                        logger.info("Token acquired, expires at %s", self.token_expiry)
                        return

                    if resp.status == 401:
                        raise InvalidClientError(
                            json_data.get("error_description") if isinstance(json_data, dict) else str(json_data)
                        )
                    if resp.status == 400:
                        raise BadRequestError(str(json_data))
                    if resp.status == 500:
                        raise ServerError(
                            json_data.get("message") if isinstance(json_data, dict) else "Internal server error"
                        )

                    raise TokenError(f"Unexpected status {resp.status}: {json_data}")

                except TokenError:
                    raise  # همونطور که هست
                except Exception as e:
                    raise TokenError(f"Token fetch failed: {e}")
                except aiohttp.ContentTypeError:
                    msg = await resp.text()
                    raise TokenError(f"Invalid response format (non-JSON): {msg}")

    async def _ensure_token_valid(self):
        if not self._token_fetched or not self.token or datetime.now() >= self.token_expiry:
            await self._fetch_token()

    async def _send_otp_async(self,
                              phone: str,
                              otp: int):
        await self._ensure_token_valid()
        phone = self._normalize_phone(phone)
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
                        return response
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
                        raise ServerError(response.get("message", "Internal server error occurred"))
                    else:
                        raise UnexpectedResponseError(f"Unexpected status code: {resp.status}, message: {response}")
                except aiohttp.ContentTypeError:
                    msg = await resp.text()
                    raise UnexpectedResponseError(f"Non-JSON response: {msg}")

    def send_otp(self,
                 phone: str,
                 otp: int | str):
        """
        ارسال کننده کد OTP
        """
        if isinstance(otp, str):
            otp = int(otp)
        try:
            loop = asyncio.get_running_loop()
            return asyncio.ensure_future(self._send_otp_async(phone, otp))
        except RuntimeError:
            return asyncio.run(self._send_otp_async(phone, otp))
