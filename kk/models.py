from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the database object
db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-increment primary key
    name = db.Column(db.String(255), nullable=False)
    kkid = db.Column(db.String(50), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)  # Date of birth
    district = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(255), nullable=False)
    zone = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for record creation
    medium = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)  # Email can be nullable
    contact_number = db.Column(db.String(20), nullable=True)  # Contact number can be nullable
    subject_id = db.Column(db.Integer, nullable=False)  # Assuming subject_id is a foreign key to a subject table

    # You can add a relationship if you have a Subject model
    # subject = db.relationship('Subject', backref='students', lazy=True)

    def __repr__(self):
        return f'<Student {self.name}, {self.kkid}, {self.dob}>'
        
# Application model (if needed)
class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email_id = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    family_details = db.Column(db.String(255), nullable=False)
    district_name = db.Column(db.String(100), nullable=False)
    school_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Application {self.full_name}>'

# Subjects table
class Subjects(db.Model):
    __tablename__ = 'subjects'  # Explicitly set table name as 'subjects'
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Subject {self.subject_name}>'

   # Volunteer model with correct ForeignKey reference
class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    volunteer_type = db.Column(db.String(100), nullable=False)
    volunteers_kkid = db.Column(db.String(50), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    
    medium = db.Column(db.String(100), nullable=False)
    zone = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))  # Corrected

    # Define relationship to Subjects
    subject_relation = db.relationship('Subjects', backref=db.backref('volunteers', lazy=True))

    def __repr__(self):
        return f'<Volunteer {self.name}>'
    
class PortionStatus(db.Model):
    __tablename__ = 'PortionStatus'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, nullable=False)
    medium = db.Column(db.String(50), nullable=False)
    volunteers_kkid = db.Column(db.String(50), nullable=False)
    zone = db.Column(db.Integer, nullable=False)
    completionStatus = db.Column(db.String(100), nullable=False)


# Attendance model
class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kkid = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('attended', 'missed', name='status_enum'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)  # ForeignKey to subjects table
    volunteers_kkid = db.Column(db.String(100), nullable=False)

    # Relationship to the Subjects table
    subject = db.relationship('Subjects', backref=db.backref('attendance', lazy=True))

    def __repr__(self):
        return f'<Attendance {self.kkid} - {self.date}>'
    
class StudentSubject(db.Model):
    __tablename__ = 'student_subjects'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))

    student = db.relationship('Student', backref='student_subjects')
    subject = db.relationship('Subjects', backref='student_subjects')

    def __repr__(self):
        return f'<StudentSubject {self.student_id} - {self.subject_id}>'

# TestMarks Model (Stores test marks for each student for a specific subject)
class TestMarks(db.Model):
    __tablename__ = 'test_marks'

    kkid = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, nullable=False)
    test_marks = db.Column(db.Integer, nullable=False)
    test_date = db.Column(db.String(10), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)  # Added field for test type

    # Define the relationship or any additional properties as needed
    def __repr__(self):
        return f'<TestMarks {self.test_marks}, Test Type: {self.test_type}>'
