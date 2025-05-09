import discord
from discord.ext import commands
import motor.motor_asyncio
import pymongo

class MongoTransfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='transfermongo')
    async def transfer_mongo(self, ctx, source_uri, source_db_name, target_uri, target_db_name):
        """Blindly transfers all collections and documents from source MongoDB to target MongoDB.

        Example:
        !transfermongo <source_uri> <source_db> <target_uri> <target_db>
        """
        await ctx.send('🚀 Starting full database transfer...')

        try:
            # Connect to source
            source_client = motor.motor_asyncio.AsyncIOMotorClient(source_uri)
            source_db = source_client[source_db_name]
            collection_names = await source_db.list_collection_names()
            await ctx.send(f'ℹ️ Collections found: {collection_names}')

            # Connect to target
            pymongo_source = pymongo.MongoClient(source_uri)
            pymongo_source_db = pymongo_source[source_db_name]
            pymongo_target = pymongo.MongoClient(target_uri)
            pymongo_target_db = pymongo_target[target_db_name]

            total_copied = 0
            total_collections = len(collection_names)
            completed_collections = 0

            if not collection_names:
                await ctx.send('⚠️ No collections listed, but will attempt to copy any system collections.')

            # Always try to loop over collections, even if list is empty
            for collection_name in collection_names or []:
                source_col = source_db[collection_name]
                docs_cursor = source_col.find({})
                docs = await docs_cursor.to_list(length=None)
                count = len(docs)

                # Insert even if count is 0 → creates empty collection in target
                target_col = pymongo_target_db[collection_name]
                if count > 0:
                    target_col.insert_many(docs)
                    total_copied += count
                    await ctx.send(f'✅ `{collection_name}` → {count} documents copied.')
                else:
                    # Creates empty collection
                    target_col.insert_one({"_placeholder": True})
                    target_col.delete_one({"_placeholder": True})
                    await ctx.send(f'✅ `{collection_name}` → empty collection created.')

                completed_collections += 1
                await ctx.send(f'📦 Progress: {completed_collections}/{total_collections} collections completed.')

            # Close clients
            source_client.close()
            pymongo_source.close()
            pymongo_target.close()

            await ctx.send(f'🎉 Transfer completed! Total documents copied: **{total_copied}** across **{total_collections}** collections.')

        except Exception as e:
            await ctx.send(f'❌ Error: {str(e)}')

# ✅ Required setup function
async def setup(bot):
    await bot.add_cog(MongoTransfer(bot))
