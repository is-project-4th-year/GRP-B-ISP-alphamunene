# Initialize sample database with tables and sample data
from . import db_models, sql_exec
import os

db_models.init_db()

# create sample business DB for query execution
sql_exec.init_sample_db()
print('Database initialized.')
