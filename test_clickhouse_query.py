from clickhouse_driver import Client

client = Client('172.17.0.2')

result = client.execute("SELECT * FROM KBTable WHERE name LIKE '%Игорь%'")


for row in result:
    print(row[1])
