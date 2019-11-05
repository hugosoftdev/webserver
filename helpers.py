import boto3
import json
from pymongo import MongoClient

def getStrategiesNames():
  s3 = boto3.resource('s3')

  ## Bucket to use
  bucket = s3.Bucket('dell-artifacts')
  prefix = 'strategies/'

  names = []
  ## List objects within a given prefix
  for obj in bucket.objects.filter(Delimiter='/', Prefix=prefix):
    names.append(obj.key.split(prefix)[1].split(".")[0])
  return names

def getModelsNames():
  bucket = 'dell-artifacts'
  #Make sure you provide / in the end
  prefix = 'models/'

  client = boto3.client('s3')
  result = client.list_objects(Bucket=bucket, Prefix=prefix, Delimiter='/')
  names = []
  for o in result.get('CommonPrefixes'):
    names.append(o.get('Prefix').split(prefix)[1].split('/')[0])
  return names

def getModelVersions(modelName):
  s3 = boto3.resource('s3')

  ## Bucket to use
  bucket = s3.Bucket('dell-artifacts')
  prefix = 'models/{0}/'.format(modelName)

  versions = []
  ## List objects within a given prefix
  for obj in bucket.objects.filter(Delimiter='/', Prefix=prefix):
    if(obj.key.split(prefix)[1].split(".")[1] == "pkl"):
      fullNameSplited = obj.key.split(prefix)[1].split(".")[0].split('-')
      versions.append(fullNameSplited[len(fullNameSplited)-1])
  return versions


def insert_simulation(data):
  client = MongoClient('mongodb://admin:pasword@52.15.139.99:27017/')

  database = client["admin"]
  collection = database["simulation"]

  document = data

  _id = collection.insert(document)
  client.close()
  return _id

def insert_results(data):
  client = MongoClient('mongodb://admin:pasword@52.15.139.99:27017/')

  database = client["admin"]
  collection = database["simulation_results"]

  document = data

  _id = collection.insert(document)
  client.close()
  return _id

def get_results(simulationId):
  client = MongoClient('mongodb://admin:pasword@52.15.139.99:27017/')

  database = client["admin"]
  collection = database["simulation_results"]

  print("Simulation Id: ", simulationId)
  result = collection.find_one({"simulation_id": simulationId})
  print(result)
  client.close()
  if result != None:
    result['_id'] = str(result['_id'])
    return result
  return {}


def get_simulation(simulationId):
  client = MongoClient('mongodb://admin:pasword@52.15.139.99:27017/')

  database = client["admin"]
  collection = database["simulation"]


  result = collection.find_one({"_id": simulationId})
  client.close()
  result['_id'] = str(result['_id'])
  return result

def get_simulations():
  client = MongoClient('mongodb://admin:pasword@52.15.139.99:27017/')

  database = client["admin"]
  collection = database["simulation"]


  result = collection.find()
  result = [doc for doc in result]
  client.close()
  for res in result:
    res['_id'] = str(res['_id'])
  return result


