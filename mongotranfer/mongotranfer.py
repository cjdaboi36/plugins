import discord
from discord.ext import commands
import motor.motor_asyncio
import pymongo

class MongoTransfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='transfermongo')
    async def transfer_mongo(self, ctx, source_uri, source_collection, target_uri, target_collection, delete_after='false'):
        """Transfers documents between MongoDB databases.
        
        Example:
        !transfermongo <source_uri> <source_collection> <target_uri> <target_collection> [delete_after]
        """
        await ctx.send('Starting transfer...')

        try:
            # Connect to source
            source_client = motor.motor_asyncio.AsyncIOMotorClient(source_uri)
            source_db = source_client.get_default_database()
            source_col = source_db[source_collection]

            # Fetch documents
            docs_cursor = source_col.find({})
            docs = await docs_cursor.to_list(length=None)
            total_docs = len(docs)
            await ctx.send(f'Fetched {total_docs} documents from source.')

            if total_docs == 0:
                await ctx.send('No documents to transfer. Exiting.')
                return

            # Connect to target
            target_client = motor.motor_asyncio.AsyncIOMotorClient(target_uri)
            target_db = target_client.get_default_database()
            target_col = target_db[target_collection]

            # Insert documents using pymongo for proper ObjectId handling
            pymongo_target = pymongo.MongoClient(target_uri)
            pymongo_db = pymongo_target.get_default_database()
            pymongo_col = pymongo_db[target_collection]
            pymongo_col.insert_many(docs)
            await ctx.send(f'Successfully inserted {total_docs} documents into target.')

            # Optional delete after transfer
            if delete_after.lower() == 'true':
                delete_result = await source_col.delete_many({})
                await ctx.send(f'Deleted {delete_result.deleted_count} documents from source after transfer.')

            # Close clients
            source_client.close()
            target_client.close()
            pymongo_target.close()

            await ctx.send('✅ Transfer completed successfully.')

        except Exception as e:
            await ctx.send(f'❌ Error: {str(e)}')

# ✅ Required setup function for the cog loader
async def setup(bot):
    await bot.add_cog(MongoTransfer(bot))
