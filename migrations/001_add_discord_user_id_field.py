import os
from playhouse.db_url import connect
from playhouse.migrate import migrate, PostgresqlMigrator
from peewee import TextField

database = connect(os.environ['DATABASE_URL'])
migrator = PostgresqlMigrator(database)

with database.atomic():
    migrate(
        migrator.add_column('ctf_mn--user', "discord_user_id", TextField(null=True, unique=True)),
    )
