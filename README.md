# BaleOTP

<div align="center">
    <img src="https://img.shields.io/pypi/v/baleotp.svg" alt="PyPI version">
    <img src="https://img.shields.io/pypi/l/baleotp.svg" alt="License">
    <img src="https://img.shields.io/pypi/pyversions/baleotp.svg" alt="Python Versions">
    <img src="https://img.shields.io/badge/coverage-90%25-brightgreen" alt="Test Coverage">
</div>

**BaleOTP** is a Python asynchronous client for sending OTPs (One-Time Passwords) through the Bale AI OTP API.

## ✨ New Features (0.1.0)

- **Auto OTP Generation**: Now automatically generates 6-digit OTP codes when none is provided
- **Enhanced Result Object**: Get both OTP code and full API response in a structured way
- **Improved Error Handling**: More specific exception classes for different error scenarios
- **Better Phone Number Normalization**: Supports more phone number formats
- **Full Async Support**: Works seamlessly in both synchronous and asynchronous contexts

## 📦 Installation

```bash
pip install --upgrade baleotp
```

## 🚀 Basic Usage

### Sending OTP with auto-generated code:

```python
from baleotp import OTPClient

client = OTPClient("your_client_id", "your_client_secret")
result = client.send_otp("09123456789")  # No OTP provided = auto-generate

print(f"Sent OTP code: {result.code}")
print(f"Full response: {result.response}")
```

### Sending with custom OTP:

```python
result = client.send_otp("09123456789", 123456)
print(f"Used OTP code: {result.code}")
```

## 🔧 Advanced Usage

### Async/Await Support:

```python
import asyncio
from baleotp import OTPClient

async def main():
    client = OTPClient("your_client_id", "your_client_secret")
    result = await client.send_otp("09123456789")
    print(result.code)

asyncio.run(main())
```

### Available Exceptions:

```python
from baleotp import (
    InvalidClientError,
    BadRequestError,
    InvalidPhoneNumberError,
    UserNotFoundError,
    InsufficientBalanceError,
    RateLimitExceededError
)

try:
    client.send_otp("invalid_number")
except InvalidPhoneNumberError as e:
    print(f"Phone number error: {e}")
```

## 📝 Phone Number Formats Supported

All these formats work:
- `09123456789`
- `989123456789`
- `+989123456789`
- `9123456789`
- `00989123456789` (non-standard but handled)

## 📜 License

MIT

---

**BaleOTP** یک کلاینت پایتونی غیرهمزمان برای ارسال رمزهای یکبار مصرف (OTP) از طریق API بله است.

## ✨ قابلیت‌های جدید (نسخه 0.1.0)

- **تولید خودکار کد**: در صورت عدم ارائه کد، به صورت خودکار یک کد ۶ رقمی تولید می‌کند
- **نتیجه ساختاریافته**: دریافت همزمان کد و پاسخ کامل سرور در یک شیء سازمان‌یافته
- **مدیریت خطاهای پیشرفته**: کلاس‌های خطای تخصصی برای سناریوهای مختلف
- **پشتیبانی از فرمت‌های بیشتر شماره تلفن**
- **پشتیبانی کامل از برنامه‌های ناهمزمان**

## 🛠️ مثال‌های پیشرفته

### استفاده غیرهمزمان:

```python
from baleotp import OTPClient

client = OTPClient("UserName", "PassWord")
result = client.send_otp("09123456789")  # تولید خودکار کد

print(f"کد ارسال شده: {result.code}")
print(f"پاسخ سرور: {result.response}")
```

### مدیریت خطاها:

```python
from baleotp import InvalidPhoneNumberError

try:
    client.send_otp("شماره نادرست")
except InvalidPhoneNumberError:
    print("شماره تلفن نامعتبر است")
```

## 📞 فرمت‌های شماره تلفن پشتیبانی شده

همه این فرمت‌ها قابل استفاده هستند:
- `09123456789`
- `989123456789`
- `+989123456789`
- `9123456789`
- `00989123456789` (غیراستاندارد اما پشتیبانی می‌شود)

## ⚖️ مجوز

MIT