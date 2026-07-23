import os
import sys

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.environ["MONGODB_URI"]

client = MongoClient(uri)
try:
    client.admin.command("ping")
    print("Houston, we have liftoff!")
finally:
    client.close()
