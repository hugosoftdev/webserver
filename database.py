import pyrebase

class Database:
    def __init__(self):
        self.config = {
            "apiKey": "AIzaSyCCaTpplU4fIvAnwvwtnagro2KruoQhzyw",
            "authDomain": "cloudcomputing-bb809.firebaseapp.com",
            "databaseURL": "https://cloudcomputing-bb809.firebaseio.com",
            "projectId": "cloudcomputing-bb809",
            "storageBucket": "cloudcomputing-bb809.appspot.com",
            "messagingSenderId": "821352958655",
            "serviceAccount": "./databaseauths.json"
        }
        self.user = None
        self.db = None

    def initialize(self):
        firebase = pyrebase.initialize_app(self.config)
        auth = firebase.auth()
        #authenticate a user
        self.user = auth.sign_in_with_email_and_password("hugosilverinha@gmail.com", "Chilloutflyv16")
        self.db = firebase.database()

    def insert(self,value):
        lastId = int(self.readAll("lastId")) + 1
        self.db.child("tarefas").child(lastId).set(value)
        self.db.child("lastId").set(lastId)


    def update(self,id,newValue):
        self.db.child("tarefas").child(id).set(newValue)

    def remove(self,id):
        return self.db.child("tarefas").child(int(id)).remove()

    def readAll(self, collection):
        return self.db.child(collection).get().val()

    def read(self,id):
        return self.db.child("tarefas").child(id).get().val()
