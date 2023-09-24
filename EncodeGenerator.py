import os
import pickle

import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Before you start your app you need to run this .py script to encode the faces of the students which you store in the
# Images folder. Please make sure every image is 216px x 216px size

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "#place your database URL here",
    'storageBucket': "#place your storage bucket URL here"
})

# importing images
folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
studentsIds = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentsIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


def encording(imageList):
    encodeList = []
    for image in imageList:
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encodeList.append(encode)

    return encodeList


print("Encording started...")
encodeListknown = encording(imgList)
encodeListknownWithIds = [encodeListknown, studentsIds]
print("Encording completed successfully")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListknownWithIds, file)
file.close()
print("File saved")
