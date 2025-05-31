import discord
from discord.ext import commands
import aiohttp

WEB_SERVER_URL = 'http://46.202.82.156:3002/upload'

class FileUpload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
@commands.command(name="add-file")
async def add_file(self, ctx: commands.Context):
    if not ctx.message.attachments:
        print(f"[INFO] {ctx.author} tried to upload a file but sent no attachment.")
        await ctx.send(f"{ctx.author.mention}, please attach a file with the command.")
        return

    attachment = ctx.message.attachments[0]
    print(f"[INFO] User {ctx.author} is uploading file: {attachment.filename}")

    # Send a quick "Uploading..." message so user knows the bot is working
    uploading_msg = await ctx.send(f"{ctx.author.mention} Uploading your file, please wait...")

    try:
        file_bytes = await attachment.read()
        filename = attachment.filename
        content_type = attachment.content_type or 'application/octet-stream'

        headers = {"User-Agent": "FileUploadBot/1.0"}

        async with aiohttp.ClientSession(headers=headers) as session:
            data = aiohttp.FormData()
            data.add_field('file', file_bytes, filename=filename, content_type=content_type)
            data.add_field('filename', filename)

            async with session.post(WEB_SERVER_URL, data=data) as resp:
                resp_text = await resp.text()

                if resp.status == 200:
                    content_type_resp = resp.headers.get('Content-Type', '')
                    if 'application/json' in content_type_resp:
                        try:
                            json_data = await resp.json()
                            link = json_data.get('link') or json_data.get('url') or str(json_data)
                        except Exception as e:
                            print(f"[WARN] Failed to parse JSON response: {e}")
                            link = resp_text
                    else:
                        link = resp_text

                    print(f"[SUCCESS] File uploaded successfully: {filename} by {ctx.author}")
                    await uploading_msg.edit(content=f"✅ File uploaded! Here’s your link:\n{link}")
                else:
                    print(f"[ERROR] Upload failed for {filename} by {ctx.author} with status {resp.status}")
                    print(f"[DEBUG] Response body on failure: {resp_text}")
                    await uploading_msg.edit(content=f"❌ Upload failed with status code {resp.status}.")
    except Exception as e:
        print(f"[EXCEPTION] Error during file upload by {ctx.author}: {e}")
        await uploading_msg.edit(content=f"❌ An error occurred: `{e}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(FileUpload(bot))
