import asyncio
import os
import pickle
from datetime import datetime

import cv2
import cvzone
import face_recognition
import firebase_admin
import numpy as np
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': "#place your database URL",
    'storageBucket': "#place your storage bucket address"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# importing images into a list
folderPath = 'Customize_dashboard/bulk-image-crop'
pathList = os.listdir(folderPath)
imgModeList = []

for path in pathList:
    imgModeList.append(cv2.imread(os.path.join(folderPath, path)))

# load the encording file
file = open("EncodeFile.p", 'rb')
encodeListknownWithIds = pickle.load(file)
file.close()
encodeListknown, studentsIds = encodeListknownWithIds

print("Encode File Loaded")


async def fetch_student_info_from_db(id):
    # Fetching student details from the database
    studentInfo = db.reference(f'Students/{id}').get()
    return studentInfo


async def download_student_image_from_storage(id):
    # Image download from the database
    blob = bucket.get_blob(f'Images/{id}.png')
    array = np.frombuffer(blob.download_as_string(), np.uint8)
    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
    return imgStudent


def draw(imgBackground, studentInfo):
    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (1020, 659),
                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(imgBackground, str(studentInfo['major']), (1020, 538),
                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(imgBackground, str(studentInfo['year']), (1013, 392),
                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(imgBackground, str(studentInfo['student_no']), (1020, 478),
                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(imgBackground, str(studentInfo['last_attendance_time']), (1020, 602),
                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
    offset = (414 - w) // 2

    cv2.putText(imgBackground, str(studentInfo['name']), (810 + offset, 337),
                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)


async def main():
    id = -1
    counter = 0
    modeType = 0
    imgStudent = []
    imgBackground = cv2.imread('Customize_dashboard/main.png')

    while True:
        success, img = cap.read()

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        imgBackground[140:140 + 480, 70:70 + 640] = img
        imgBackground[0:0 + 707, 770:770 + 503] = imgModeList[modeType]

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListknown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListknown, encodeFace)

                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, (x2 - x1), (y2 - y1)
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    id = studentsIds[matchIndex]

                    if counter == 0:
                        cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                        cv2.imshow("Display", imgBackground)
                        cv2.waitKey(2)
                        counter = 1
                        modeType = 1

            if counter != 0:
                if counter == 1:
                    # Asynchronously fetch student info from the database
                    studentInfo = await fetch_student_info_from_db(id)

                    # Asynchronously download the student image
                    imgStudent = await download_student_image_from_storage(id)

                    # update the datetime
                    dateTimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - dateTimeObject).total_seconds()

                    if secondsElapsed > 30:

                        # Update the attendance
                        ref = db.reference(f'Students/{id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[0:0 + 707, 770:770 + 503] = imgModeList[modeType]

                if modeType != 3:

                    if 10 < counter < 20:
                        modeType = 2
                        imgBackground[0:0 + 707, 770:770 + 503] = imgModeList[modeType]

                    if counter <= 10:
                        draw(imgBackground, studentInfo)
                        imgBackground[67:67 + 216, 913:913 + 216] = imgStudent

                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[0:0 + 707, 770:770 + 503] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0

        cv2.imshow("Display", imgBackground)
        key = cv2.waitKey(1)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    asyncio.run(main())
