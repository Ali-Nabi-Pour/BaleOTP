# import asyncio
# from baleotp import OTPClient
#
# async def main():
#     otp = OTPClient("GFrZtHCyvyqsoHWrSQSLbDgXTreaqeDe", "hCqdSuhsUFwrgshPNTURdHDgnnSxYSwU")
#     await otp.send_otp("989118373115", 123456)
#
# if __name__ == "__main__":
#     asyncio.run(main())
# from balethon import Client
# from baleotp import OTPClient, get_version
#
# bot = Client("1393027745:7ZT51Wt2hzuPlciCGn3U22GW42kUB2A5Hs9rmM2J")
# otp = OTPClient("GFrZtHCyvyqsoHWrSQSLbDgXTreaqeDe00", "hCqdSuhsUFwrgshPNTURdHDgnnSxYSwU")
# #
# # @bot.on_command()
# # async def start(*, message):
# #     await message.reply("سلام! کد را وارد کن")
# result = otp.send_otp("09118373115", 12345)
# print(result)  # اینجا نتیجه‌ی ارسال OTP رو می‌گیری

# bot.run()
# نمونه استفاده:
# async def main():
#     client = OTPClient("GFrZtHCyvyqsoHWrSQSLbDgXTreaqeDe00", "hCqdSuhsUFwrgshPNTURdHDgnnSxYSwU")
#     response = await client.send_otp("09118373115", 123456)
#     print(response)
#
# if __name__ == "__main__":
#     asyncio.run(main())
import asyncio
import logging

from baleotp import OTPClient, InvalidClientError, BadRequestError, ServerError
from baleotp import InvalidPhoneNumberError, UserNotFoundError, InsufficientBalanceError
from baleotp import RateLimitExceededError, UnexpectedResponseError

logging.basicConfig(level=logging.INFO)

# اطلاعات تست (اطلاعات واقعی خودت رو جایگزین کن)
client_id = "GFrZtHCyvyqsoHWrSQSLbDgXTreaqeDe"
client_secret = "hCqdSuhsUFwrgshPNTURdHDgnnSxYSwU"
phone = "09118373115"
otp_code = 1234  # یا مثلاً "1234"

async def main():
    client = OTPClient(client_id, client_secret)

     # تست دریافت توکن
    try:
        await client._fetch_token()
        print("✅ Token fetched successfully:", client.token)
    except InvalidClientError as e:
        print("❌ Invalid client error:", e)
    except BadRequestError as e:
        print("❌ Bad request error:", e)
    except ServerError as e:
        print("❌ Server error:", e)

    # تست ارسال OTP
    try:
        result = await client.send_otp(phone, otp_code)
        print("✅ OTP sent successfully:", result)
    except InvalidPhoneNumberError as e:
        print("❌ Invalid phone number:", e)
    except UserNotFoundError as e:
        print("❌ User not found:", e)
    except InsufficientBalanceError as e:
        print("❌ Insufficient balance:", e)
    except RateLimitExceededError as e:
        print("❌ Rate limit exceeded:", e)
    except ServerError as e:
        print("❌ Server error while sending OTP:", e)
    except UnexpectedResponseError as e:
        print("❌ Unexpected response:", e)

if __name__ == "__main__":
    asyncio.run(main())
