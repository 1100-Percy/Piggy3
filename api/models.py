from mongoengine import Document, StringField, IntField, ListField, DictField, ReferenceField, DateTimeField, BooleanField
import datetime

class Student(Document):
    username = StringField(required=True, unique=True) # Links to Django User
    thinking_type = StringField(default="divergent") # divergent (Graph/Clear Soup) or convergent (Tree/Red Oil)
    carrots = IntField(default=0)
    
    meta = {'collection': 'user'} # Map to 'user' collection as requested

class Course(Document):
    name = StringField(required=True)
    icon = StringField(default="dumpling") # dumpling, ramen, etc.
    outline_text = StringField()
    owner = ReferenceField(Student)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {'collection': 'course'}

class Graph(Document):
    course = ReferenceField(Course)
    # Storing vis-network data structure directly
    nodes = ListField(DictField()) 
    edges = ListField(DictField())
    owner = ReferenceField(Student)
    
    meta = {'collection': 'graph'}

class Task(Document):
    content = StringField(required=True)
    status = StringField(default="pending") # pending, completed, skipped
    course = ReferenceField(Course)
    owner = ReferenceField(Student)
    date = DateTimeField(default=datetime.datetime.utcnow)
    is_completed = BooleanField(default=False)
    
    meta = {'collection': 'task'}

class StudyStats(Document):
    owner = ReferenceField(Student)
    date = DateTimeField() # Just the date part usually, but DateTime is fine
    completed_count = IntField(default=0)
    
    meta = {'collection': 'study_stats'}
