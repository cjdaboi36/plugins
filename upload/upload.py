import discord
from discord.ext import commands
import aiohttp
import asyncio

WEB_SERVER_URL = 'https://files.cjscommissions.xyz/upload'

 class FileUpload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="add-file")
    async def add_file(self, ctx: commands.Context):
        await ctx.send(f"{ctx.author.mention}, check your DMs to upload the file!")

        user = ctx.author

        try:
            await user.send("Please upload the file you want to add:")

            def check(m):
                return (
                    m.author == user and
                    isinstance(m.channel, discord.DMChannel) and
                    m.attachments
                )

            msg = await self.bot.wait_for('message', check=check, timeout=120)
            attachment = msg.attachments[0]
            file_bytes = await attachment.read()
            filename = attachment.filename

            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('filename', filename)
                data.add_field('file', file_bytes, filename=filename, content_type=attachment.content_type)

                async with session.post(WEB_SERVER_URL, data=data) as resp:
                    if resp.status == 200:
                        link = await resp.text()
                        await user.send(f"✅ File uploaded! Here’s your link:\n{link}")
                    else:
                        await user.send(f"❌ Upload failed with status {resp.status}.")
        except discord.HTTPException:
            await ctx.send(f"{ctx.author.mention} I couldn't send you a DM. Please make sure your DMs are open.")
        except asyncio.TimeoutError:
            await user.send("⏰ You took too long to upload the file. Please try again.")
        except Exception as e:
            await user.send(f"❌ An error occurred: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(FileUpload(bot))
