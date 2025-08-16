import discord, typing
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timezone
from utils.fetchdata import fetchdata, create_embed, save_replay # 自製模組

class ChannelTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> discord.TextChannel:
        guild = interaction.guild
        channel = discord.utils.get(guild.text_channels, name=value)
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

    @app_commands.command(name="tasks", description="定時搜尋某人最近完成的遊戲")
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

        if channel.id in self.active_tasks:
            await interaction.response.send_message("目前無法在一個文字頻道同時執行兩個以上的任務。\n請先取消運行中的任務，或者更換文字頻道後再試一次", ephemeral=True)
            return

        user_url = f"https://ch.tetr.io/api/users/{username}"
        user_data = await fetchdata(user_url, ignorecache=False)
        @tasks.loop(hours=hours)
        #@tasks.loop(seconds=10) #測試用
        async def fetch_records():
            nonlocal replayid
            #try:
            if ispb: record_url = f"https://ch.tetr.io/api/users/{username}/records/{gamemode}/top?limit=1"
            else: record_url = f"https://ch.tetr.io/api/users/{username}/records/{gamemode}/recent?limit=1"
            record_data = await fetchdata(record_url, ignorecache=True)
            cache_status = record_data.get("cache").get("status")
            if cache_status == "hit":
                print("有快取")
                return
            entries = record_data.get("data").get("entries")
            ts = entries[0].get("ts")
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if replayid != entries[0].get("replayid") and dt > start_time:
                file = await save_replay(entries[0].get("replayid"))
                replayid = entries[0].get("replayid")
                embed, banner = await create_embed(record_data, user_data, gamemode, username)
                if gamemode == "zenith":                                   #40l和blitz的extras是空的
                    if entries[0].get("extras").get("zenith").get("mods"): #所以要套兩層否則會出錯，暫時沒想到更好的解法 
                        await channel.send(embed=embed, file=banner)
                        await channel.send(file=file)
                        return
                else:
                    await channel.send(embed=embed)
                    await channel.send(file=file)  
            #except Exception as e:
            #    print(e)

        fetch_records.start()
        self.active_tasks[channel.id] = fetch_records
        print(f"{interaction.user} 在頻道 {channel.name} 開始了任務: 每 {hours} 小時爬取 {username} 的 {gamemode} 遊戲紀錄")
        await interaction.response.send_message(f"現在開始每 {hours} 小時爬取 {username} 的 {gamemode} 遊戲紀錄，並發送到 {channel.mention}", ephemeral=True)

    @app_commands.command(name="cancel_tasks", description="取消搜尋")
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
        del self.active_tasks[channel_id]
        print(f"{interaction.user} 取消了頻道 {interaction.channel.name} 的任務")
        await interaction.response.send_message("當前頻道運行中的任務已取消", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tasks(bot))
