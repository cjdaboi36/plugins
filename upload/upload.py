import discord
from discord.ext import commands
import aiohttp
import logging

WEB_SERVER_URL = 'https://files.cjscommissions.xyz/upload'

logger = logging.getLogger('file_upload')
logger.setLevel(logging.INFO)
# You can customize logging handlers here if you want, e.g., console or file
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class FileUpload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="add-file")
    async def add_file(self, ctx: commands.Context):
        if not ctx.message.attachments:
            logger.info(f"{ctx.author} tried to upload a file but sent no attachment.")
            await ctx.send(f"{ctx.author.mention}, please attach a file with the command.")
            return

        attachment = ctx.message.attachments[0]
        logger.info(f"User {ctx.author} is uploading file: {attachment.filename}")

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
                        logger.info(f"File uploaded successfully: {filename} by {ctx.author}")
                        await ctx.send(f"✅ File uploaded! Here’s your link:\n{link}")
                    else:
                        logger.error(f"Upload failed for {filename} by {ctx.author} with status {resp.status}")
                        await ctx.send(f"❌ Upload failed with status code {resp.status}.")
        except Exception as e:
            logger.exception(f"Error during file upload by {ctx.author}: {e}")
            await ctx.send(f"❌ An error occurred: `{e}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(FileUpload(bot))
