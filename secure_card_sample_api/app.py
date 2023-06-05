import json 
import os
from pymongo import MongoClient
from aes import mainloop
from dotenv import load_dotenv
from flask import Flask, flash,  request,jsonify, abort
from azure.storage.blob import ContainerClient   

app = Flask(__name__)
app.config["SECRET_KEY"] = "you-will-never-guess"

mongoClient =  MongoClient('127.0.0.1', port = 27017) 

miDb = mongoClient.data_refund
#Creacion de la coleccion
miCol = miDb.bill_card

load_dotenv() 
KEY = os.getenv('KEY')
ROUNDNUM = os.getenv('ROUNDNUM') 
AZURE_STORAGE_CONNECTIONSTRING = os.getenv('AZURE_STORAGE_CONNECTIONSTRING') 
REFUND_CONTAINER_NAME = os.getenv('REFUND_CONTAINER_NAME')


@app.route("/", methods=["GET"])
def index():
    data = request.json   
    if "nombre " not in data or "pan" not in data or "valor" not in data or "moneda" not in data: 
        raise abort(400,"Falta(n) dato(s) requeridos") 
    

    truncated_pan = data.pop("pan") 
    
    miDoc = miCol.find_one(data)   
    del miDoc["_id"] 

    tc = mainloop(miDoc["pan"], KEY, int(ROUNDNUM), True) 

    #print(tc[:4],truncated_pan[:4] , tc[-4:],truncated_pan[-4:])

    if(tc[:4]!=truncated_pan[:4] or tc[-4:]!=truncated_pan[-4:]): 
        raise abort(400,"PAN no coincide") 
   
    miDoc["pan"] = int(tc)

    json_object = json.dumps(miDoc, indent=4) 
    with open("sample.json", "w") as outfile:
        outfile.write(json_object) 

    upload(truncated_pan, AZURE_STORAGE_CONNECTIONSTRING, REFUND_CONTAINER_NAME)

    path = os.path.join(os.getcwd(), "sample.json")   
    os.remove(path)

    #print(path)
    return(jsonify({"Exitoso":True}))

def upload(truncated_pan, connection_string, container_name):  
    container_client = ContainerClient.from_connection_string(connection_string, container_name) 
    print("uploading files to blob storage...") 
    blob_client = container_client.get_blob_client(truncated_pan) 
    with open('sample.json',"rb") as data: 
        blob_client.upload_blob(data) 
            

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)