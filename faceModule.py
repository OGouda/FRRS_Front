import face_recognition
import os
import pickle
import postgresql
import sys
import dlib
import cv2
import re
import time
import base64
import json
import requests
from io import BytesIO


def addPerson(PersonName , filepath):
    
    #Connect to DB
    db = postgresql.open('pq://bayan:toor@localhost:5432/test')
   
    known_image = face_recognition.load_image_file(filepath)
    encodings = face_recognition.face_encodings(known_image)
    print(known_image)
    if len(encodings) > 0:
        query = "INSERT INTO vectors (file, vec_low) VALUES ('{}', CUBE(array[{}]) )".format(
            PersonName,
            ','.join(str(s) for s in encodings[0][0:128]),                    
        )
       
    print(PersonName + ' has been added')
    db.execute(query)    

    print("Added : ", PersonName)

def addPersonAPI(name , NewPath):
    email = " "
    with open(NewPath, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
     
    data = {'name':name,'email':email,'img64b':my_string}
    
    res = requests.post(url='http://192.168.10.9:5000/', data=data)
    
    if res.ok:
        print("response : ",res.text)

    resText = json.loads(res.text)

    if resText["found Person In DB"]:        
        print("person already exists!!!!!!!")
        error = "User Already Exists"
    elif resText["number of faces found"] > 1:
        print("More than one Face in Image!!!!!!!")
        error = "More than one Face in Image"
    elif not(resText["Good Image"]):
        print("Image is Bad!!!!!!!!!")
        error = "Image quality is too low"
    else:
        print("Everything is Good") 
        error ="Successful"
        
    
    return error





'''
    #print(face_encoding)
    entry = {'name': PersonName, 'embeddings': face_encoding}
    if not os.path.isfile(DATA_FILENAME):
        with open(DATA_FILENAME, 'wb') as outfile:
            pickle.dump(entry, outfile)

    else:
        with open(DATA_FILENAME, 'ab') as f:
            pickle.dump(entry, f, pickle.HIGHEST_PROTOCOL)
            #json.dump(entry, f)
            #f.write(os.linesep)
'''
   
