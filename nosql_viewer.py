import pymongo

# connect with a client or create a new one
myclient = pymongo.MongoClient()#"mongodb://localhost:27017/")
myclient.list_database_names()
# look for table or create a new one
mydb = myclient["orderbook"]
mydb.list_collection_names()
# look for collection or create a new one
mycol = mydb["BTCUSDbitfinex"]

for x in mycol.find():
    print(x)

"""
To inspect NoSQL databases, in terminal:
mongo
show dbs # list and show memory usage
use orderbook # switch
db.dropDatabase() # eliminate
"""