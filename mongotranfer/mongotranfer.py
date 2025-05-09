import discord
from discord.ext import commands
import motor.motor_asyncio
import pymongo

class MongoTransfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='transfermongo')
    async def transfer_mongo(self, ctx, source_uri, source_db_name, target_uri, target_db_name):
        """Transfers all collections and documents from source MongoDB to target MongoDB with progress updates.
        
        Example:
        !transfermongo <source_uri> <source_db> <target_uri> <target_db>
        """
        await ctx.send('🚀 Starting full database transfer...')

        try:
            # Connect to source
            source_client = motor.motor_asyncio.AsyncIOMotorClient(source_uri)
            source_db = source_client[source_db_name]
            collection_names = await source_db.list_collection_names()
            
            if not collection_names:
                await ctx.send('⚠️ No collections found in source database. Exiting.')
                return

            # Connect to target
            pymongo_source = pymongo.MongoClient(source_uri)
            pymongo_source_db = pymongo_source[source_db_name]
            pymongo_target = pymongo.MongoClient(target_uri)
            pymongo_target_db = pymongo_target[target_db_name]

            total_copied = 0
            total_collections = len(collection_names)
            completed_collections = 0

            for collection_name in collection_names:
                source_col = source_db[collection_name]
                docs_cursor = source_col.find({})
                docs = await docs_cursor.to_list(length=None)
                count = len(docs)

                if count == 0:
                    await ctx.send(f'⚠️ Skipped empty collection `{collection_name}`.')
                else:
                    target_col = pymongo_target_db[collection_name]
                    target_col.insert_many(docs)
                    total_copied += count
                    await ctx.send(f'✅ `{collection_name}` → {count} documents copied.')

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
