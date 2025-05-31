import discord
from discord.ext import commands
import aiohttp

WEB_SERVER_URL = 'https://files.cjscommissions.xyz/upload'

class FileUpload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="add-file")
    async def add_file(self, ctx: commands.Context):
        # Check for attachment
        if not ctx.message.attachments:
            await ctx.send(f"{ctx.author.mention}, please attach a file with the command.")
            return

        attachment = ctx.message.attachments[0]

        try:
            file_bytes = await attachment.read()
            filename = attachment.filename
            content_type = attachment.content_type or 'application/octet-stream'

            headers = {"User-Agent": "FileUploadBot/1.0"}

            async with aiohttp.ClientSession(headers=headers) as session:
                data = aiohttp.FormData()
                data.add_field('filename', filename)
                data.add_field('file', file_bytes, filename=filename, content_type=content_type)

                async with session.post(WEB_SERVER_URL, data=data) as resp:
                    if resp.status == 200:
                        link = await resp.text()
                        await ctx.send(f"✅ File uploaded! Here’s your link:\n{link}")
                    else:
                        await ctx.send(f"❌ Upload failed with status code {resp.status}.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: `{e}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(FileUpload(bot))
