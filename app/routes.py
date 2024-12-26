from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import openai
import os
import psycopg2
# Storage for questions, student certified results and additional information/hints.
questions = []
additional_information_store = []

#Database connection for SQL functions.
#conn = psycopg2.connect("dbname= ********** user=********** password=**********") This is the connection for reference, the updated version with method below.
def get_connection():
    conn = psycopg2.connect("dbname= ***** user=***** password=*****")#Fill
    return conn

UPLOAD_FOLDER = r'path/to/upload/folder/in/static' #Route to upload folder to be filled on PC running system.
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}#Checks that file uploaded is in one of the given formats.

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS #Returns true if extension is in list, by splitting once at '.' and checking this side of the split, which is [1].



def register_routes(app): #Standard HTML homepage route for Flask apps.
    @app.route('/')
    def index():
        return render_template('index.html')

    #@app.route('/mock_log_in_teacher')  Original mock log in pages, they are kept here for reference and to show how implementation progressed.
    #def mockloginteacher():
        #if request.method == 'POST':
            #return redirect(url_for('teacher'))
        #return render_template('mock_log_in_teacher.html')

    #@app.route('/mock_log_in_student')
    #def mockloginstudent():
        #if request.method == 'POST':
            #return redirect(url_for('student'))
        #return render_template('mock_log_in_student.html')

    #Routes make use of GET or POST HTTP methods, for either requesting or sending data. This is set in the route declaration.

    @app.route('/login', methods=['GET', 'POST']) #New log in route with SQL link.
    def login():
        if request.method == 'POST': #When data is submitted via the HTML form.
            username = request.form['username_submitted']
            password = request.form['password_submitted']
            conn = get_connection() #Opens up a database connection, using the method at the beginning of the file.
            cur = conn.cursor() #Cursor allows queries to be made.
            cur.execute("SELECT userid, username, password, role FROM users WHERE username = %s", (username,)) #%s is a placeholder for security, username is written as tuple as psycopg2 expects this.
            user = cur.fetchone() #Fetches only the first row, as apposed to fetchall().
            cur.close() #Closes the cursor.
            conn.close() #Closes the connection so that inteference is less likely. This is good practice.

            if user and user[2] == password: #user[2] is the index holding the password retrieved in line 45 and stored in user in line 46.
                session['userid'] = user[0]
                session['username'] = user[1]
                session['role'] = user[3]
                if user[3]== 'teacher': #Depending on the role, the relevant redirect is used.
                    return redirect(url_for('teacher'))
                elif user[3] == 'student':
                    return redirect(url_for('student'))
            else:
                flash('Invalid username or password.')
        return render_template('login.html') #Otherwise, refresh the page.

    @app.route('/teacher')
    def teacher():
        if 'userid' in session and session['role'] == 'teacher': #Session keeps users logged in for the duration of their time on the site. This allows data, such as userids, to be recorded in SQL.
            return render_template('teacher.html')

    @app.route('/student')
    def student():
        if 'userid' in session and session['role'] == 'student':
            return render_template('student.html')

    @app.route('/set_questions', methods=['GET', 'POST']) #HTTP methods that means the method can transmit and receive
    def setquestions():

        if request.method == 'POST':
            materialid = request.form['materialid_submitted'] #Relevant fields are retrieved from the user form submission and stored in these variables, so they can be inserted into SQL.
            question_text = request.form['question_submitted']
            hidden_prompt = request.form['hidden_prompt_submitted']
            created_by = session.get('userid')#This is held for the duration of the user's time on the system while in session.

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO questions(materialid, text,created_by) VALUES(%s, %s, %s)",(materialid, question_text, created_by))#Note that userid is serial, so is automatically incremented and inserted so does not need to be specified here or in other queries working with serial primary keys.
            conn.commit() #Saves the insertions and changes. The query inserted the retrieved information from the form, and used %s as placeholders, which ensures data is inserted correctly.
            cur.close()
            questions.append({'question': question_text, 'hidden_prompt': hidden_prompt}) #Saves question and prompt together in their own dictionary within questions[].

            additional_info = request.form['additional_info_submitted']
            additional_information_store.append({'question': question_text, 'additional_info': additional_info}) #Key:value
            #Stores info in its own dictionary in list of dictionaries, {key 'question' value question text, key 'additional_info value additional_info} This was set up to keep hints and questions together, however this was not finished on time.
            flash('Question added successfully!')
            return redirect(url_for('setquestions'))
        conn = get_connection()
        cur = conn.cursor() #This is the GET request.
        cur.execute("SELECT materialid, title FROM materials")
        materials = cur.fetchall() #This assigns the information retrieved as a varialbe, which is then passed into the template when rendered.
        cur.close()
        conn.close()

        return render_template('set_questions.html', questions=questions, materials=materials) #Questions and materials allows them to be displayed in the HTML template.



    @app.route('/answerquestions', methods=['GET', 'POST'])#Submits and receives.
    def answerquestions(): #This is where ChatGPT is actually used.
        additional_info = additional_information_store[0]['additional_info'] #Accesses first element in list (only element) and the value associated with its key.
        if request.method == 'POST':
            question_text = request.form['question_submitted']
            answer = request.form['answer_submitted']

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT questionid FROM questions WHERE text = %s", (question_text,))
            question_id = cur.fetchone()#Gets question id and stores it here.

            submitted_by = session.get('userid')
            cur = conn.cursor()
            cur.execute("INSERT INTO answers(text, question_id, submitted_by) VALUES(%s, %s, %s)", (answer, question_id, submitted_by))
            conn.commit() #Updates answers table.
            cur.close()
            conn.close()
            question = next(q for q in questions if q['question'] == question_text) #Find the correct dictionary from questions[]
            hidden_prompt = question['hidden_prompt'] #Finds the value of the hidden prompt key within that dictionary.
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "A teacher has set hidden prompt as guideline so you can give feedback to a student's answer, which should be detailed and where you MUST advise 'pass' or 'need to review.' Hidden prompt: " + hidden_prompt}, #This back-end prompt helps to give the AI context and support the teacher's own prompt.
                    {"role": "user", "content": "Question: " + question_text + " Student's answer: " + answer}
                ]
            )
            feedback = response['choices'][0]['message']['content']
            
            return render_template('answer_questions.html', questions=questions, selected_question=question_text, answer=answer, feedback=feedback, additional_info = additional_info)
        return render_template('answer_questions.html', questions=questions, additional_info = additional_info)

    @app.route('/markquestion', methods=['POST'])
    def markquestion():
        if request.method == 'POST':
            question = request.form['mark_question_submitted'] #Assigns form submissions to variables.
            mark = request.form['mark_submitted'] #Variable assigned from form.
            self_certified = True if mark == 'pass' else False #This converts to a bool because SQL table stores this as a boolean.
            #Database connection and data insertion.
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT questionid FROM questions WHERE text = %s", (question,))
            question_id = cur.fetchone()[0]
            cur.execute("SELECT materialid FROM questions WHERE text = %s", (question,))
            material_id = cur.fetchone()[0]
            cur.execute("SELECT answerid FROM answers WHERE question_id = %s ORDER BY answerid DESC LIMIT 1", (question_id,)) #Issues with updating results table, "ORDER BY answerid DESC LIMIT 1" ensures that most recently added row is added.
            answer_id = cur.fetchone()[0]
            feedback = request.form['feedback_submitted']
            cur.execute("INSERT INTO results(question_id, materialid, answer_id, feedback, self_certified) VALUES(%s, %s, %s, %s, %s)", (question_id, material_id, answer_id, feedback, self_certified))
            conn.commit()
            cur.close()
            conn.close()

            return redirect(url_for('answerquestions'))
        return render_template('answer_questions.html', questions=questions)



    @app.route('/upload_material')
    def uploadmaterial(): #Renders template, functionality was added afterward.
        return render_template('upload_material.html')
    
    @app.route('/upload', methods=['POST'])
    def upload_file(): #Method for uploading materials.
        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(file.filename)#From werkzeug, checks that file is safe.
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            title = request.form['title_submitted']
            description = request.form['description_submitted']
            uploaded_by = session.get('userid')
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO materials(title, description, file_path, uploaded_by) VALUES(%s, %s, %s, %s)", (title, description, file_path, uploaded_by))
            conn.commit()
            cur.close()
            conn.close()

            return 'File uploaded successfully'
        return 'No file uploaded'

    @app.route('/view_material')
    def viewmaterial(): #Fetches the necessary information from SQL and assigns it to 'materials', which is then passed through to the template.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT title, description, file_path FROM materials")
        materials = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('view_material.html', materials=materials)
    
    @app.route('/viewresults')
    def viewresults(): #First view results page that was originally for all users, the SQL query was changed, and the HTML route edited, so that only teachers can see this page.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT r.*, u.username FROM results r JOIN answers a ON r.answer_id = a.answerid JOIN users u ON a.submitted_by = u.userid;") #Ensures relevant information is displayed. Join statement is used to combine tables on shared values, inner join by default.
        results = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('view_results.html', results=results)

    @app.route('/viewresultsstudent')
    def viewresultsstudent():
        conn = get_connection()
        username = session.get('username')
        cur = conn.cursor()
        cur.execute("SELECT userid FROM users WHERE username = %s;", (username,)) #This block checks the userid to make sure a student only sees their own results.
        user_id_found = cur.fetchone()
        user_id = user_id_found[0]


        cur.execute( #This query ensures that a student can only see their own results by using a join statement, crucially, where the userid matches,
            """SELECT r.resultid, q.text AS question_text, a.text AS answer_text, a.submitted_by AS userid, r.feedback, r.self_certified FROM results r JOIN questions q ON r.question_id=q.questionid JOIN answers a ON r.answer_id = a.answerid JOIN users u ON a.submitted_by = u.userid WHERE a.submitted_by =%s;""", (user_id,))
        results = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('view_results_student.html', results=results)