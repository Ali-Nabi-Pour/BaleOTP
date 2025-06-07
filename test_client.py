# import asyncio
# from baleotp import OTPClient
#
# async def main():
#     otp = OTPClient("GFrZtHCyvyqsoHWrSQSLbDgXTreaqeDe", "hCqdSuhsUFwrgshPNTURdHDgnnSxYSwU")
#     await otp.send_otp("989118373115", 123456)
#
# if __name__ == "__main__":
#     asyncio.run(main())
from balethon import Client
from baleotp import OTPClient

bot = Client("1393027745:7ZT51Wt2hzuPlciCGn3U22GW42kUB2A5Hs9rmM2J")
otp = OTPClient("GFrZtHCyvyqsoHWrSQSLbDgXTreaqeDe", "hCqdSuhsUFwrgshPNTURdHDgnnSxYSwU")
#
# @bot.on_command()
# async def start(*, message):
#     await message.reply("سلام! کد را وارد کن")
result = otp.send_otp("989118373115", 12345)
print(result)  # اینجا نتیجه‌ی ارسال OTP رو می‌گیری

# bot.run()