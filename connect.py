import snowflake.coonector

conn=snowflake.connector.connect(
  user='SravyaChitipotu',
  password='Chinnari@123',
  account='account_identifier',
)

cursor=conn.cursor()
cursor.execute("SELECT CURRENT_VERSION()")
results=cursor.fetchall()
print(results)
cursor.close()
conn.close()
