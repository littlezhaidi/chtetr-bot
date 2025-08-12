import discord, typing
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timezone
from utils.fetchdata import fetchdata # 自製模組

class ChannelTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> discord.TextChannel:
        guild = interaction.guild
        channel = discord.utils.get(guild.text_channels, name=value)
        if channel is None:
            await interaction.response.send_message(f"找不到名為 {value} 的頻道", ephemeral=True)
            print(f"找不到名為 {value} 的頻道")
            return None
        return channel
    
    async def autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=channel.name, value=channel.name)
            for channel in interaction.guild.text_channels 
            if current.lower() in channel.name.lower()
        ][:5]

class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_tasks = {}  # {channel_id: tasks.Loop}
        #self.task_flags = {}  # {channel_id: bool}，用於追蹤任務是否應該停止 

    @app_commands.command(name="tasks", description="之後的輸出會換成embed，長得跟getpb差不多")
    @app_commands.guilds(discord.Object(id=1325105067787026473))
    @app_commands.guild_only()

    async def tasks(self, 
        interaction: discord.Interaction, 
        username: str, 
        gamemode: typing.Literal["40l", "blitz", "zenith", "zenithex"], 
        channel: app_commands.Transform[discord.TextChannel, ChannelTransformer],
        hours: typing.Literal[1, 2, 3, 6, 12, 24],
        ispb: bool = False
    ):
        replayid = ""
        start_time = datetime.now(timezone.utc)
        #self.task_flags[channel.id] = False

        if channel.id in self.active_tasks:
            await interaction.response.send_message("目前無法在一個文字頻道同時執行兩個以上的任務。\n請先取消運行中的任務，或者更換文字頻道後再試一次", ephemeral=True)
            return
        #@tasks.loop(hours=hours)
        @tasks.loop(seconds=10) #測試用
        async def fetch_records():
            nonlocal replayid
            try:
                #if self.task_flags[channel.id]:  # 如果任務被標記為停止，則退出
                #    print("任務已被標記為停止，退出迴圈")
                #    return
                if ispb: record_url = f"https://ch.tetr.io/api/users/{username}/records/{gamemode}/top?limit=1"
                else: record_url = f"https://ch.tetr.io/api/users/{username}/records/{gamemode}/recent?limit=1"

                record_data = await fetchdata(record_url)
                entries = record_data.get("data").get("entries")
                ts = entries[0].get("ts")
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))

                if record_data is None:
                    await channel.send(f"我猜你把 {username} 打錯了")
                    return
                if replayid != entries[0].get("replayid") and dt > start_time:
                    replayid = entries[0].get("replayid")
                    await channel.send(f"{username} 在 {ts} 玩了一場 {gamemode} \nlink: https://tetr.io/#R:{replayid}")
            except Exception as e:
                print(e)
        fetch_records.start()
        self.active_tasks[channel.id] = fetch_records
        print(f"{interaction.user} 在頻道 {channel.name} 開始了任務: 每 {hours} 小時爬取 {username} 的 {gamemode} 遊戲紀錄")
        await interaction.response.send_message(f"現在開始每 {hours} 小時爬取 {username} 的 {gamemode} 遊戲紀錄，並發送到 {channel.mention}", ephemeral=True)

    @app_commands.command(name="cancel_tasks", description="之後的輸出會換成embed，長得跟getpb差不多")
    @app_commands.guilds(discord.Object(id=1325105067787026473))
    @app_commands.guild_only()
    async def cancel_tasks(self, interaction: discord.Interaction):
    #取消目前頻道運行的任務
        channel_id = interaction.channel.id
        if channel_id not in self.active_tasks:
            await interaction.response.send_message("當前頻道沒有運行中的任務", ephemeral=True)
            return
        task = self.active_tasks[channel_id]
        task.stop()
        #await task.wait()
        del self.active_tasks[channel_id]
        print(f"{interaction.user} 取消了頻道 {interaction.channel.name} 的任務")
        await interaction.response.send_message("當前頻道運行中的任務已取消", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tasks(bot))
