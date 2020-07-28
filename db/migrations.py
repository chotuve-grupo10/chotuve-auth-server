from auth_server.db_functions import create_app_servers_table_command
from auth_server.db_functions import create_reset_password_table_command

create_table_users = """CREATE TABLE Users (
						email VARCHAR(255) PRIMARY KEY ,
						full_name VARCHAR(255) NOT NULL,
						phone_number VARCHAR(255),
						profile_picture VARCHAR(255),
						hash VARCHAR(255) NOT NULL,
						salt VARCHAR(255) NOT NULL,
						firebase_user VARCHAR(1) NOT NULL,
						admin_user VARCHAR(1) NOT NULL,
						blocked_user VARCHAR(1) NOT NULL);"""


def all_migrations():
  migration_list = []
  migration_list.append(create_table_users)
  migration_list.append(create_app_servers_table_command)
  migration_list.append(create_reset_password_table_command)
  return migration_list