#!/usr/bin/env python
import snowflake.connector

# Gets the version
ctx = snowflake.connector.connect(
    user='dbt',
    password='dbtPassword123',
    account='wsqqrdg-wl98475'
    )
cs = ctx.cursor()
try:
    cs.execute("SELECT * FROM AIRBNB.RAW.RAW_LISTINGS LIMIT 3")
    rows = cs.fetchmany(3)  # Fetches 3 rows
    print(rows)
finally:
    cs.close()
ctx.close()