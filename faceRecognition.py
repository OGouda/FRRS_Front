from PIL import Image
import face_recognition
import cv2
import numpy as np
import pickle
import postgresql
import re 
import time
from imutils.video import VideoStream
import imutils
from PIL import Image
import base64
import json
import requests
#import argparse


def faceRecog (img, face_names):
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    num = 30
    print("im in the function")
    print(img)
    #image = Image.open('Dina.png')
    image = cv2.imread(img)
    db = postgresql.open('pq://bayan:toor@localhost:5432/test')

    # Resize frame of video to 1/4 size for faster face recognition processing
    #small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    #rgb_small_frame = image[:, :, ::-1]
    rgb_small_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)

    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)


    if len(face_encodings) > 0:
        for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)    
        #face_names = "Unknown"
            print("length of encodings0",len(face_encodings))
            threshold = 0.477
            
            print("length of encodings1",len(face_encodings))
            query = "SELECT  file FROM vectors WHERE sqrt(power(CUBE(array[{}]) <-> vec_low, 2)) <= {}".format(
                ','.join(str(s) for s in face_encoding[0:128]),
                threshold,
            ) + \
                        " ORDER BY sqrt(power(CUBE(array[{}]) <-> vec_low, 2)) ASC LIMIT 1".format(
                            ','.join(str(s) for s in face_encoding[0:128]),
                        )

            Answer=db.query(query)        
            name = ""     
            if(len(Answer)):
                #print(Answer) 
                for item in Answer:
                    for info in item:
                        face_names.append(info)
                        print('face_names 1') 
                        break
            else:
                face_names.append("Unknown#")
                print("Unknown# 1")

    else:
        #name = "Unknown"
        face_names.append("No_face_detected")
        print(face_names) 
        print("Unknown#2")

    print("length of encodings2",len(face_encodings))
        
    print("from function",face_names) 
    
    return face_names

def checkPersonAPI(NewPath,face_names):

    
    with open(NewPath, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())

    print('length of the iamge for check ...', len(my_string))
    data = {'img64b':my_string}
    
    res = requests.post(url='http://192.168.10.9:5000/signIn', data=data)
    
    if res.ok:
        print("response : ",res.text)

    
    resText = json.loads(res.text)

    face_names = resText["person name"]
    print("the person is :   ",face_names)
    if resText["found Person In DB"]:        
        print("person already exists!!!!!!!")
        error = "User Already Exists"
    elif resText["number of faces found"] > 1:
        print("More than one Face in Image!!!!!!!")
        error = "More than one Face in Image"  
    else:
        print("Everything is Good") 
        error ="Successful"       
    
    return face_names