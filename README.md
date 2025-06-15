# BaleOTP

<div align="center">
    <img src="https://img.shields.io/pypi/v/baleotp.svg" alt="PyPI version">
    <img src="https://img.shields.io/pypi/l/baleotp.svg" alt="License">
    <img src="https://img.shields.io/pypi/pyversions/baleotp.svg" alt="Python Versions">
</div>


**BaleOTP** is a Python asynchronous client for sending OTPs (One-Time Passwords) through the Bale AI OTP API.

### Features

* Fetches and refreshes access tokens automatically
* Sends OTPs to Iranian mobile numbers
* Fully asynchronous using `aiohttp`
* Handles all documented error responses
* Accepts various phone number formats (e.g., 0912..., 98912..., +98912...)
* Supports both `int` and `str` format OTPs
* Customizable base URL for different environments (e.g., test/staging)

### Installation

```bash
pip install baleotp
```

### Usage

```python
from baleotp import OTPClient

client = OTPClient("your_client_id", "your_client_secret")
response = client.send_otp("09123456789", 123456)
print(response)
```

Or with `await` (inside async code):

```python
import asyncio
from baleotp import OTPClient

async def main():
    client = OTPClient("your_client_id", "your_client_secret")
    result = await client.send_otp("09123456789", 123456)
    print(result)

asyncio.run(main())
```

### License

MIT

---


**BaleOTP** یک کلاینت پایتونی غیرهمزمان برای ارسال رمزهای یکبار مصرف (OTP) از طریق API بله است.

### قابلیت‌ها

* دریافت و تمدید خودکار توکن احراز هویت
* ارسال OTP به شماره‌های موبایل ایران
* طراحی کامل با استفاده از `aiohttp`
* مدیریت تمام خطاهای اعلام‌شده در مستندات
* تشخیص و اصلاح فرمت شماره‌ها (۰۹، ۹۸، +۹۸ و...)
* پشتیبانی از OTP به صورت عدد (`int`) یا رشته (`str`)
* امکان تعیین آدرس دلخواه (base URL) برای تست یا محیط‌های دیگر

### نصب

```bash
pip install baleotp
```

### مثال استفاده

```python
from baleotp import OTPClient

client = OTPClient("UserName", "PassWord")
response = client.send_otp("09123456789", 123456)
print(response)
```

یا به صورت `async`:

```python
import asyncio
from baleotp import OTPClient

async def main():
    client = OTPClient("UserName", "PassWord")
    result = await client.send_otp("09123456789", 123456)
    print(result)

asyncio.run(main())
```

### مجوز

MIT
