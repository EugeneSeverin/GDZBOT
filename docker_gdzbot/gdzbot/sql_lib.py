create_accounts_bot = """create table accounts_bot (gdz_id SERIAL primary KEY,
							name VARCHAR(255) default NULL,
							surname VARCHAR(255) default NULL,
							telegram_id VARCHAR(255) not NULL,
							chat_id VARCHAR(255) not NULL,
							requests_today INT DEFAULT 0,
							request_limit INT DEFAULT 3,
							access_level INT default 0)
"""