import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import db, Student, Volunteer, Application,Subjects,StudentSubject,Attendance,TestMarks,PortionStatus
from mysql.connector import Error

# Initialize the Flask app
app = Flask(__name__)

# Set the secret key for session management
app.config['SECRET_KEY'] = os.urandom(24)  # Change this to a random string

# Configure the database URI (use correct credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:2025@localhost/student_access_portal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)

# Route for the index page (Home)
@app.route('/')
def index():
    return render_template('index.html')

# Admission page
@app.route('/admission')
def admission():
    return render_template('admission.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Login page for students and volunteers
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')  # 'student' or 'volunteer'
        volunteers_kkid = request.form.get('kkid')  # Retrieve volunteers_kkid input

        if user_type == 'student':
            student = Student.query.filter_by(kkid=volunteers_kkid).first()
            if student:
                flash('Student login successful!', 'success')
                return redirect(url_for('student_access', kkid=volunteers_kkid))
            else:
                flash('Invalid KKID for student!', 'danger')
                return redirect(url_for('login'))

        elif user_type == 'volunteer':
            volunteer_type = request.form.get('volunteer_type')  # Retrieve volunteer type
            volunteer = Volunteer.query.filter_by(volunteers_kkid=volunteers_kkid, volunteer_type=volunteer_type).first()
            if volunteer:
                if volunteer_type == 'test-conducting-team':
                    return redirect(url_for('test', kkid=volunteers_kkid))
                elif volunteer_type == 'assignment':
                    return redirect(url_for('assignment', kkid=volunteers_kkid))
                elif volunteer_type == 'tutor':
                    return redirect(url_for('tutor', kkid=volunteers_kkid))
                elif volunteer_type == 'others':
                    return redirect(url_for('others', kkid=volunteers_kkid))
            else:
                flash('Invalid KKID or Volunteer Type!', 'danger')
                return redirect(url_for('login'))
           
    return render_template('login.html')

# Route for handling Sign In
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    subjects = Subjects.query.all()  # Get all available subjects

    if request.method == 'POST':
        user_type = request.form.get('user_type')  # 'student' or 'volunteer'

        if user_type == 'student':
            kkid = request.form.get('kkid')  # Keep kkid as string
            district = request.form.get('district')
            school = request.form.get('school')
            selected_subject_id = request.form.get('subject')  # Get the selected subject ID for students (single value)

            # Ensure subject_id is an integer for students
            try:
                subject_id = int(selected_subject_id)  # Convert the selected subject ID to an integer
            except ValueError:
                flash('Invalid subject selected for student', 'error')
                return render_template('signin.html', subjects=subjects)

            # Create a new student
            student = Student(
                name=request.form.get('name'),
                kkid=kkid,  # Keep kkid as string
                dob=request.form.get('dob'),
                district=district,
                school=school,
                subject_id=selected_subject_id,
                email=request.form.get('email'),
                contact_number=request.form.get('contact_number'),
                zone=request.form.get('zone'),
                medium=request.form.get('medium')
            )

            db.session.add(student)
            db.session.commit()

            # Associate student with the selected subject
            student_subject = StudentSubject(student_id=student.id, subject_id=subject_id)
            db.session.add(student_subject)
            db.session.commit()

            flash('Sign in successful! You have been registered as a student.', 'success')

            # Optional: Render a success message on the same page or show a confirmation message
            return render_template('signin.html', subjects=subjects, success_message="Student registration successful!")

        elif user_type == 'volunteer':
            kkid = request.form.get('kkid')  # Keep volunteer kkid as string
            selected_subject_id = request.form.get('subject')  # Get the selected subject for volunteers (single value)

            # Ensure subject_id is an integer for volunteers
            try:
                selected_subject_id = int(selected_subject_id)  # Ensure subject_id is an integer
            except ValueError:
                flash('Invalid subject selected for volunteer', 'error')
                return render_template('signin.html', subjects=subjects)

            # Create a new volunteer
            volunteer = Volunteer(
                name=request.form.get('name'),
                volunteers_kkid=kkid,  # Keep kkid as string
                dob=request.form.get('dob'),
                volunteer_type=request.form.get('volunteer_type'),
                subject_id=selected_subject_id,
                email=request.form.get('email'),
                contact_number=request.form.get('contact_number'),
                zone=request.form.get('zone'),
                medium=request.form.get('medium')
            )

            db.session.add(volunteer)
            db.session.commit()

            flash('Sign in successful! You have been registered as a volunteer.', 'success')

            # Optional: You can render a message here without redirecting
            return render_template('signin.html', subjects=subjects, success_message="Volunteer registration successful!")

    return render_template('signin.html', subjects=subjects)

@app.route('/admission_form', methods=['GET', 'POST'])
def admission_form():
    if request.method == 'POST':
        # Extract form data
        full_name = request.form.get('full_name')
        email_id = request.form.get('email_id')
        contact_number = request.form.get('contact_number')
        family_details = request.form.get('family_details')
        district_name = request.form.get('district_name')
        school_name = request.form.get('school_name')

        # Input validation
        if not (full_name and email_id and contact_number and family_details and district_name and school_name):
            flash("All fields are required. Please fill out the form completely.", "warning")
            return redirect(url_for('admission_form'))

        # Create a new Application entry
        new_application = Application(
            full_name=full_name,
            email_id=email_id,
            contact_number=contact_number,
            family_details=family_details,
            district_name=district_name,
            school_name=school_name
        )

        # Add the application to the database
        try:
            db.session.add(new_application)
            db.session.commit()
            flash("Application submitted successfully!", "success")
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error submitting application: {str(e)}", "danger")

    # For GET requests, render the form
    return render_template('admission_form.html')

# Route to access student page based on KKID
@app.route('/student_access')
def student_access():
    kkid = request.args.get('kkid')
    if kkid:
        student = Student.query.filter_by(kkid=kkid).first()
        if student:
            return render_template('student_access.html', student=student)
        else:
            flash('Student not found!', 'danger')
            return redirect(url_for('login'))
    else:
        flash('KKID is missing!', 'danger')
        return redirect(url_for('login'))

# Route for other volunteer types (e.g., test-conducting-team, assignment)
@app.route('/others')
def others():
    return render_template('others.html')

# Route for profile view for students
@app.route('/profile/<string:student_id>')
def student_profile(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student_profile.html', student=student)

# Route for tutors, expecting kkid as a URL parameter
@app.route('/tutor/<kkid>')
def tutor(kkid):
    volunteer = Volunteer.query.filter_by(volunteers_kkid=kkid, volunteer_type='tutor').first()
    if volunteer:
        return render_template('tutor.html', volunteer=volunteer)
    else:
        flash('Invalid KKID for tutor!', 'danger')
        return redirect(url_for('login'))
    
# Route for assignment page
@app.route('/assignment/<kkid>')
def assignment(kkid):
    volunteer = Volunteer.query.filter_by(volunteers_kkid=kkid, volunteer_type='assignment').first()
    if volunteer:
        return render_template('assignment.html', volunteer=volunteer)
    else:
        flash('Invalid KKID for assignment volunteer!', 'danger')
        return redirect(url_for('login'))

def get_volunteer_data(volunteer_type, volunteers_kkid):
    """
    Fetches volunteer data from the database based on volunteer type and KKID.
    """
    volunteer = Volunteer.query.filter_by(volunteer_type=volunteer_type, volunteers_kkid=volunteers_kkid).first()
    return volunteer


@app.route('/volunteer_profile/<volunteer_type>/<volunteers_kkid>')
def volunteer_profile(volunteer_type, volunteers_kkid):
    # Fetch the volunteer data
    volunteer = get_volunteer_data(volunteer_type, volunteers_kkid)
    
    if not volunteer:
        flash("Volunteer not found!", "danger")
        return redirect(url_for('login'))  # Redirect to login page if volunteer is not found
    
    return render_template('volunteer_profile.html', volunteer=volunteer)

# Route to render attendance form
@app.route('/attendance', methods=['GET'])
def attendance():
    # Get the filter criteria (zone, medium, subject)
    zone = request.args.get('zone')
    medium = request.args.get('medium')
    subject_id = request.args.get('subject_id')
    
    students = []
    if zone and medium and subject_id:
        students = db.session.query(Student).filter(
            Student.zone == zone,
            Student.medium == medium,
            Student.subject_id == subject_id
        ).all()
    
    return render_template('attendance.html', students=students, zone=zone, medium=medium, subject_id=subject_id)



# Route to save attendance
@app.route('/add_attendance', methods=['POST'])
def add_attendance():
    zone = request.form['zone']
    medium = request.form['medium']
    subject_id = request.form['subject_id']
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    kkid = request.form['kkid']

    students = db.session.query(Student).filter(
        Student.zone == zone,
        Student.medium == medium,
        Student.subject_id == subject_id
    ).all()

    if not students:
        flash("No students found for the selected criteria.", "warning")

    for student in students:
        attendance_status = 'attended' if f'attendance_{student.kkid}' in request.form else 'missed'
        attendance_entry = Attendance(
            kkid=student.kkid,
            date=date,
            status=attendance_status,
            subject_id=subject_id,
            volunteers_kkid=kkid
        )
        db.session.add(attendance_entry)

    db.session.commit()

    flash("Attendance successfully saved.", "success")
    return redirect(url_for('attendance'))

@app.route('/test/<kkid>')
def test(kkid):
    volunteer = Volunteer.query.filter_by(volunteers_kkid=kkid, volunteer_type='test-conducting-team').first()
    if volunteer:
        return render_template('test.html', volunteer=volunteer)
    else:
        flash('Invalid KKID for test-conducting team!', 'danger')
        return redirect(url_for('login'))

# Route to fetch and render attendance data
@app.route('/attendance_data/<kkid>', methods=['GET'])
def attendance_stu(kkid):
    # Query attendance records for the given KKID
    attendance_records = Attendance.query.filter_by(kkid=kkid).all()
    
    # Check if no records are found
    if not attendance_records:
        return render_template('attendance_stu.html', attendance=None)
    
    # Pass the attendance records excluding 'volunteers_kkid' to the template
    filtered_records = [
        {
            "attendance_id": record.attendance_id,
            "kkid": record.kkid,
            "date": record.date,
            "status": record.status,
            "subject_id": record.subject_id
        }
        for record in attendance_records
    ]
    return render_template('attendance_stu.html', attendance=filtered_records)

@app.route('/submit_test_marks', methods=['POST'])
def submit_test_marks():
    data = request.get_json()
    marks = data.get('marks')

    for entry in marks:
        kkid = entry.get('kkid')
        subject_id = entry.get('subject_id')
        test_marks = entry.get('test_marks')
        test_date = entry.get('test_date')
        test_type = entry.get('test_type')

        # Query to fetch the student from the database using KKID
        student = Student.query.filter_by(kkid=kkid).first()
        if student:
            # Save or update the test marks, date, and type (this assumes you have a TestMarks table/model)
            test_record = TestMarks(
                kkid=kkid,
                subject_id=subject_id,
                test_marks=test_marks,
                test_date=test_date,
                test_type=test_type
            )

            db.session.add(test_record)
        else:
            print(f"Student with KKID {kkid} not found.")

    db.session.commit()

    return jsonify({'message': 'Test marks submitted successfully!'})


# Route to handle AJAX requests for fetching students
@app.route('/fetch_students', methods=['POST'])
def fetch_students():
    data = request.json
    zone = data.get('zone')
    medium = data.get('medium')
    subject_id = data.get('subject_id')

    students = db.session.query(Student).filter(
        Student.zone == zone,
        Student.medium == medium,
        Student.subject_id == subject_id
    ).all()

    # Return student data as JSON
    return jsonify([{"kkid": student.kkid, "name": student.name} for student in students])

# Route to render the Test Marks Update page
@app.route('/test_marks_update')
def test_marks_update():
    return render_template('test_marks_update.html')  # Render the HTML page

@app.route('/test_marks/<string:kkid>')
def test_marks(kkid):
    # Debugging: Print kkid to make sure it is being passed correctly
    print(f"Fetching data for KKID: {kkid}")

    # Query the 'test_marks' table to fetch details based on the kkid
    student_marks = TestMarks.query.filter_by(kkid=kkid).all()

    # Debugging: Print the fetched data to see what is returned
    print(f"Fetched {len(student_marks)} records for KKID: {kkid}")

    # Return the data to the template
    return render_template('test_marks.html', student_marks=student_marks, kkid=kkid)

# Route for updating the portion status
@app.route('/portion_update', methods=['GET', 'POST'])
def update_status():
    if request.method == 'POST':
        # Fetch form data
        subject_id = request.form['subject_id']
        medium = request.form['medium']
        volunteers_kkid = request.form['volunteers_kkid']
        zone = int(request.form['zone'])  # Convert zone to integer
        completion_status = request.form['completion_status']

        # Insert the new portion status into the table
        new_status = PortionStatus(
            subject_id=subject_id,
            medium=medium,
            volunteers_kkid=volunteers_kkid,
            zone=zone,
            completionStatus=completion_status
        )
        db.session.add(new_status)
        db.session.commit()

        # After successful insertion, redirect to the same page to show updated status list
        return redirect(url_for('update_status'))

    # Fetch all portion statuses to display
    updates = PortionStatus.query.all()
    
    return render_template('portion_update.html', updates=updates)

# Subject mapping
subject_mapping = {
    1: "Mathematics",
    2: "Physics",
    3: "Chemistry",
    4: "Commerce",
    5: "Accountancy"
}

@app.route('/portion_status')
def portion_status():
    # Query the database to get all records from the PortionStatus table
    portions = PortionStatus.query.all()

    # Map subject_id to subject name
    for portion in portions:
        portion.subject_name = subject_mapping.get(portion.subject_id, "Unknown Subject")

    return render_template('portion_status.html', portions=portions)

@app.route('/tutor_marks', methods=['GET', 'POST'])
def tutor_marks():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        medium = request.form['medium']
        zone = request.form['zone']
        
        # Query data based on the form selection
        students = Student.query.filter_by(subject_id=subject_id, medium=medium, zone=zone).all()
        student_kkids = [student.kkid for student in students]
        marks_data = TestMarks.query.filter(TestMarks.kkid.in_(student_kkids)).all()
        
        # Dynamically fetch subject name based on subject_id
        subject = Subjects.query.filter_by(subject_id=subject_id).first()
        subject_name = subject.subject_name if subject else "Unknown Subject"

       
        return render_template('tutor_marks.html', marks_data=marks_data, student_names=student_names, marks=marks, subject_name=subject_name)

    return render_template('tutor_marks.html')
if __name__ == '__main__':
    app.run(debug=True)
