# import couchdb
# from dotenv import load_dotenv, find_dotenv
# import os

# ## Load Dotenv
# load_dotenv(find_dotenv())


# db_uri = os.getenv("db_uri")
# db_username = os.getenv("db_username")
# db_password = os.getenv("db_password")

# couch = couchdb.Server(f"https://{db_username}:{db_password}@{db_uri}")
# print(type(couch))

# db =  couch["PlannerItems"]
# #doc = {}
# #db.save(doc)
# #doc
