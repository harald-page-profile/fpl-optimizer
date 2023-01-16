import snowflake.connector
import pandas as pd
import os


def create_connection():
    # Connect to snowflake
    ctx = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASS"),
        account=os.getenv("SNOWFLAKE_ACCOUNT")
        )
    return ctx

def fetch_data(ctx):
    cur = ctx.cursor()
    try:
      sql = "select * from FPL_DEMO.MODELLED.FPL_MASTER"
      cur.execute(sql)
      df = cur.fetch_pandas_all()
    finally:
        cur.close()
    ctx.close()
    return df
