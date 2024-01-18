import psycopg2
import asyncio
import asyncpg
from creds import gdz_bot_token, gdz_gpt_token, DBConnectParams

create_accounts_bot = """create table accounts_bot (gdz_id SERIAL primary KEY,
							name VARCHAR(255) default NULL,
							surname VARCHAR(255) default NULL,
							username VARCHAR(255) default NULL,
							telegram_id INT8 not NULL,
							chat_id VARCHAR(255) not NULL,
							requests_today INT DEFAULT 0,
							request_limit INT DEFAULT 3,
							access_level INT default 0,
							credit INT8 DEFAULT 30 NOT NULL);"""

async def create_table(query):
    async with asyncpg.create_pool(**DBConnectParams) as pool:
        async with pool.acquire() as connection:
            await connection.execute(query)

async def main():
	await create_table(query=create_accounts_bot)

def create_table_sync(query):
	with psycopg2.connect(**DBConnectParams) as connection:
		connection.autocommit = True
		with connection.cursor() as cursor:
			cursor.execute(query)

if __name__ == "__main__":
	#create_table_sync(create_accounts_bot)
	asyncio.run(create_table(query=create_accounts_bot))