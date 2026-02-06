import os

from peewee import TextField
from playhouse.db_url import connect
from playhouse.migrate import PostgresqlMigrator, migrate

database = connect(os.environ['DATABASE_URL'])
migrator = PostgresqlMigrator(database)

with database.atomic():
    migrate(
        migrator.add_column('ctf_mn--user', "discord_user_id", TextField(null=True, unique=True)),
    )
