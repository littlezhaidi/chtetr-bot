import os, asyncio, discord
from discord.ext import commands


bot = commands.Bot(command_prefix="^", intents = discord.Intents.all())
MY_GUILD = discord.Object(id=1325105067787026473)

# 當機器人完成啟動時
@bot.event
async def on_ready():
    #slash_commands = await bot.tree.sync()
    slash_commands = await bot.tree.sync(guild=MY_GUILD)
    print("\n".join([f"已註冊: {sc.name}"for sc in slash_commands]))
    print(f"{bot.user} logged in!")

# 載入指令程式檔案
@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await bot.tree.sync(guild=MY_GUILD)
    await ctx.send(f"Loaded {extension} done.")

# 卸載指令檔案
@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await bot.tree.sync(guild=MY_GUILD)
    await ctx.send(f"UnLoaded {extension} done.")

# 重新載入程式檔案
@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await bot.tree.sync(guild=MY_GUILD)
    await ctx.send(f"ReLoaded {extension} done.")

# 一開始bot開機需載入全部程式檔案
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("._"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start("YOUR_BOT_TOKEN")

# 確定執行此py檔才會執行
if __name__ == "__main__":
    asyncio.run(main())
