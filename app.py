#!/usr/bin/env python

from flask import Flask, flash,request, render_template, redirect, after_this_request
from werkzeug.utils import secure_filename
#import faceModule#
import faceRecognition
import os
from io import BytesIO
from PIL import Image
import base64
import threading
from multiprocessing import Pool
import time
from collections import Counter
import operator
import requests
import json

# Create the application.
APP = Flask(__name__)
APP.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
API = os.environ['API']
_pool = None
Allowed_extension = {'png', 'jpeg'}
APP.config['Upload_Image_folder'] = "./uploaded_Image"

@APP.route('/')
def home():
    return render_template('home.html')

API_registration_Link = os.environ['Reg_URL']
signIn = os.environ['Sign_URL']

@APP.route('/RegistarLive', methods=['POST', 'GET'])
def RegistarLive():

    if request.method == 'POST':

        data = {}

        #during testing purposes 
        email = 'email'
        gender= 'gender'


        if 'fileImg' in request.form:
            print('The user has taken a live image for registration instead of uploaded an old image.')

            file  = request.form['fileImg']
            print(f'The file recived has the following type: [{type(file)}]')
            #extract image data from the received POST request. 
            starter = file.find(',')
            image_Base64_format = file[starter+1:]
            image_Base64_format = bytes(image_Base64_format, encoding="ascii")
            image_viewableFormat = Image.open(BytesIO(base64.b64decode(image_Base64_format)))

            #use the perosn name from the from, in saving the image in the local storage - for testign purposes.
            personName = request.form['humanName']
            NewPath    = os.path.join(APP.config['Upload_Image_folder'], personName+'.png')
            image_viewableFormat.save(NewPath)

            data = {'name':personName,'email':email, 'gender': gender, 'img64b':image_Base64_format, 'api':API}


        elif 'file1' in request.files:  
            print('The user have uploaded an image instead of taking a live picture')

            #extract image data from the received the request and save it.  
            personName   = request.form['humanName2']
            fileReceived = request.files['file1']
            filename     = secure_filename(fileReceived.filename)
            extension = filename.split(".")[1]
            print(filename)

            #use the perosn name from the from, in saving the image in the local storage - for testign purposes.
            NewPath= os.path.join(APP.config['Upload_Image_folder'], personName+"."+extension)
            fileReceived.save(NewPath)

            image_Base64_format=''
            with open(NewPath, "rb") as img_file:
                image_Base64_format = base64.b64encode(img_file.read())
                os.remove(NewPath)

            data = {'name':personName,'email':email, 'gender':gender, 'img64b':image_Base64_format, 'api':API}

        
        error_message = ''
        call_response = requests.post(url= API_registration_Link , data=data)
    
        if call_response.status_code == 200:
            resText = json.loads(call_response.text)
            print("The process of added new user is successfull")
            error_message =f"[{resText['PERSON_NAME']}] was added successfully!"
        
        elif call_response.status_code == 201:
            resText = json.loads(call_response.text)
            print("person already exists!!!")
            error_message = f"User Already Exists, ID: {resText['ID']} - {resText['PERSON_NAME']}"


        else: #call_response.status_code == 400:
            resText = json.loads(call_response.text)
            error_message = resText['message']
            print(f"Error[400]: [{error_message}]") 
                        
        flash(error_message)

        return render_template('RegistarNormal.html')
    else:
        return render_template('RegistarNormal.html')




@APP.route('/Registar', methods=['POST', 'GET'])
def Register():

    if request.method == 'POST':

        data = {}

        #during testing purposes 
        email = 'email'
        gender= 'gender'


        if 'fileImg' in request.form:
            print('The user has taken a live image for registration instead of uploaded an old image.')

            file  = request.form['fileImg']
            print(f'The file recived has the following type: [{type(file)}]')
            #extract image data from the received POST request. 
            starter = file.find(',')
            image_Base64_format = file[starter+1:]
            image_Base64_format = bytes(image_Base64_format, encoding="ascii")
            image_viewableFormat = Image.open(BytesIO(base64.b64decode(image_Base64_format)))

            #use the perosn name from the from, in saving the image in the local storage - for testign purposes.
            personName = request.form['humanName']
            NewPath    = os.path.join(APP.config['Upload_Image_folder'], personName+'.png')
            image_viewableFormat.save(NewPath)

            data = {'name':personName,'email':email, 'gender': gender, 'img64b':image_Base64_format, 'api':API}


        elif 'file1' in request.files:  
            print('The user have uploaded an image instead of taking a live picture')

            #extract image data from the received the request and save it.  
            personName   = request.form['humanName2']
            fileReceived = request.files['file1']
            filename     = secure_filename(fileReceived.filename)
            extension = filename.split(".")[1]
            print(filename)

            #use the perosn name from the from, in saving the image in the local storage - for testign purposes.
            NewPath= os.path.join(APP.config['Upload_Image_folder'], personName+"."+extension)
            fileReceived.save(NewPath)

            image_Base64_format=''
            with open(NewPath, "rb") as img_file:
                image_Base64_format = base64.b64encode(img_file.read())
                os.remove(NewPath)

            data = {'name':personName,'email':email, 'gender':gender, 'img64b':image_Base64_format, 'api':API}

        
        error_message = ''
        call_response = requests.post(url= API_registration_Link , data=data)

        if call_response.status_code == 200:
            resText = json.loads(call_response.text)
            print("The process of added new user is successfull")
            error_message =f"[{resText['PERSON_NAME']}] was added successfully!"
        
        elif call_response.status_code == 201:
            resText = json.loads(call_response.text)
            print("person already exists!!!")
            error_message = f"User Already Exists, ID: {resText['ID']} - {resText['PERSON_NAME']}"


        else: #call_response.status_code == 400:
            resText = json.loads(call_response.text)
            error_message = resText['message']
            print(f"Error[400]: [{error_message}]") 
                        
        flash(error_message)

        return render_template('RegistarForm.html')
    else:
        return render_template('RegistarForm.html')


@APP.route('/checkImages', methods=['POST','GET'])
def checkImages():
    name="spaceHolder"
    if request.method == 'POST':
        print("I recieved this thing!")  
        
        face_names = [] 
        processes_list =[]
        Frames_path= []
        Number_of_frames= 5
        extension       = '.jpg'

        pool = Pool(processes=Number_of_frames)
        for i in range(Number_of_frames):
            field_Name = 'upImage'+str(i) # example 'upImage0'
            #file_name = request.files[field_Name].filename
            print('Frame - [{}]'.format(field_Name))

            file_path = os.path.join(APP.config['Upload_Image_folder'], field_Name)+extension
            request.files[field_Name].save(file_path)
    
            processes_list.append(pool.apply_async(checkPersonAPI, [file_path, API]))
        
        pool.close()
        pool.join()


        face_names = []
        for i in processes_list:

            print('results')
            Arr = i.get(timeout=2)
            print(Arr)
            if Arr is not None and Arr != []:
                face_names.append(Arr[1])

 
        poolResults_highOcc_name   = max(set(face_names), key = face_names.count)       
        poolResults_OccNumber = {i:face_names.count(i) for i in face_names}       
    
        print('Most repeated name: {} has been repeated for: {}'.format(poolResults_highOcc_name, poolResults_OccNumber))
  
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        print("Im sending the name : ", poolResults_highOcc_name)

    return poolResults_highOcc_name
    

def checkPersonAPI(NewPath, API):

    my_string = ''
    with open(NewPath, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())

    print('length of the image for check ...', len(my_string))
    data = {'img64b':my_string, 'api':API}
    #print(data)

    error_message = ''
    Name_person = 'Unknown'
    call_response = requests.post(url=signIn, data=data)

    if call_response.status_code == 200:  # MATCH FOUND
        resText = json.loads(call_response.text)
        print(f"A match was found. The person's name is: [{resText['PERSON_NAME']}]")
        error_message = "MATCH_FOUND"
        Name_person   = resText['PERSON_NAME']
    
    elif call_response.status_code == 201:
        resText = json.loads(call_response.text)
        print("No match found for this frame !!!!!!!")
        error_message ="MATCH_NOT_FOUND"

    else: #call_response.status_code == 400:
        resText = json.loads(call_response.text)
        error_message = resText['message']
        print(f"Error[400]: [{error_message}]") 
                    
    flash(error_message)

    return error_message,  Name_person


@APP.route('/signIn')
def VideFeed():   
    return render_template('signIn.html')


if __name__ == '__main__':
    #global name
    #APP.debug=True
    APP.run(host= '0.0.0.0', ssl_context='adhoc', port=4000, debug=True)
