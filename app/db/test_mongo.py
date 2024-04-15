
from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://cluster0.pocr4yq.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri,
                     tls=True,
                    tlsCertificateKeyFile='app\db\X509-cert-5527943773821302944.pem',
                     server_api=ServerApi('1'))

db = client['testDB']
collection = db['testCol']
doc_count = collection.count_documents({})
print(doc_count)
