import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# download the credential details .json file and save it to the same directory which this AddDataToDatabase.py exist.

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "#place your database URL here"
})

ref = db.reference('Students')

# Rename the student .png images by the corresponding ID which you provide below
# Customize the below json as your wish

data = {
    "1":  # add ID number which can uniquely identified the student
        {
            "name": "Pawan Pinsara",
            "student_no": "CS/2020/xxx",
            "major": "computer science",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:23:40",
            "total_attendance": 0,
        },

    "2":
        {
            "name": "name 2",  # add a name here
            "major": "---",
            "student_no": "CS/2021/xxx",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:34:34",
            "total_attendance": 0,
        },

    "3":
        {
            "name": "name 2",  # add a name here
            "student_no": "CS/2020/xxx",
            "major": "---",
            "year": 2,
            "last_attendance_time": "2022-12-11 01:54:34",
            "total_attendance": 0,
        },
}

for key, value in data.items():
    ref.child(key).set(value)

print("data added to the database")
