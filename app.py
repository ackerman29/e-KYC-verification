from flask import Flask, render_template ,request, send_from_directory,Response,redirect,url_for,flash
import cv2
import os
import datetime
from flask import jsonify
import time
import requests
import fitz
import re
import warnings
from werkzeug.utils import secure_filename
import numpy as np

from deepface import DeepFace
#
#import db
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import SelectField, StringField, PasswordField, BooleanField , SubmitField , DateField
from wtforms.validators import DataRequired, InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = r"C:/Users/Rupanjan/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/"
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Rupanjan/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/user.db'
#db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
#db.create_all()
#
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    fname = db.Column(db.String(1000))
    lname = db.Column(db.String(1000))

    def is_active(self):
        # Assuming all users are active
        return True


class PersonalDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    income_range = db.Column(db.String(50), nullable=False)
    employment_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)

class PersonalDetailForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=1, max=15)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    income_range = SelectField('Income Range', choices=[
        ('1', 'Up to Rs 2,50,000'),
        ('2', 'Rs 2,50,001 - Rs 5,00,000'),
        ('3', 'Rs 5,00,001 to Rs 10,00,000'),
        ('4', 'Rs 10,00,001 and above')
    ], validators=[DataRequired()])
    employment_type = SelectField('Employment Type', choices=[
        ('full_time', 'Full-time employment'),
        ('part_time', 'Part-time employment'),
        ('contract', 'Contract employment'),
        ('casual', 'Casual employment'),
        ('apprenticeship', 'Apprenticeship'),
        ('traineeship', 'Traineeship'),
        ('commission_based', 'Commission-based employment'),
        ('probation', 'Probation')
    ], validators=[DataRequired()])
    address = StringField('Address', validators=[InputRequired(), Length(min=1, max=255)])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])
    fname = StringField('first name', validators=[InputRequired(), Length(min=4)])
    lname = StringField('last name', validators=[InputRequired(), Length(min=4)])

#=======================ROUTES=================================================================

#-------------Home Page---------------------
@app.route('/')
def index():
    return render_template('home.html')

#--------------LOGIN PAGE-------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            print("Successfully logged in user\n")
            return redirect(url_for('dashboard'))
        print("Invalid Username or Password\n")
        flash("Invalid username or password")  
        return redirect(url_for('login'))

    return render_template('login.html', form=form)

#---------------SIGNUP PAGE----------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data,
                        fname=form.fname.data, lname=form.lname.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("New user has been created!")
            print('New user has been created!\n')
            return redirect(url_for('login'))

        except Exception as e:
            print("There was an issue while adding new user:", e)
            flash("Error occurred while creating new user")

    return render_template('signup.html', form=form)
#------------------------DASHBOARD----------------------
@app.route('/dashboard')
#@login_required
def dashboard():
    return render_template('dashboard.html', fname=current_user.fname,lname=current_user.lname,uname=current_user.username,email=current_user.email)

#------------------------CREATED BY----------------------
@app.route('/created')
@login_required
def created():
    return render_template('created.html')

#------------------------PROFILE----------------------
@app.route('/profile')
@login_required
def profile():
    f=open(app.config["IMAGE_UPLOADS"]+'comparison_result.txt','r')
    st=f.read()
    stat='Not Verified'
    if st=='1':
        stat='Verified'
    print('status : ',stat)
    return render_template('profile.html',status=stat,password='******',fname=current_user.fname,lname=current_user.lname,uname=current_user.username,email=current_user.email)

#-----------Steps Routes-------------------
@app.route('/enterDetails', methods=['GET', 'POST'])
def enterDetails():
    form = PersonalDetailForm()

    if form.validate_on_submit():
        # Create a new instance of the PersonalDetail model with form data
        personal_detail = PersonalDetail(
            name=form.name.data,
            date_of_birth=form.date_of_birth.data,
            income_range=form.income_range.data,
            employment_type=form.employment_type.data,
            address=form.address.data
        )
        try:
            # Add the new personal_detail to the database session
            db.session.add(personal_detail)
            # Commit the changes to the database
            db.session.commit()
            flash("Personal details have been saved!")
            print('Personal details have been saved!\n')
            return redirect(url_for('next_route'))  # Redirect to the next route after saving

        except Exception as e:
            print("There was an issue while adding personal details:", e)
            flash("Error occurred while saving personal details")

    return render_template('enter_details.html', form=form)

                           
#-----------Steps Routes------------------
@app.route('/stp1' , methods=['GET' , 'POST'])
def stp1():
    return render_template('stp1.html')

@app.route('/stp2', methods=['GET'])
def stp2():
    return render_template('stp2.html')

@app.route('/stp3', methods=['GET'])
def stp3():
    f=open(app.config["IMAGE_UPLOADS"]+'comparison_result.txt','r')
    res=f.read()
    print(res)
    print(type(res))
    if res=='0':
        return render_template('stp3.html',result=False,fname=current_user.fname,lname=current_user.lname)
    else:
        return render_template('stp3.html',result=True,fname=current_user.fname,lname=current_user.lname)



#--------------------------End Page------------------------------
@app.route('/end')
def end():
    return render_template('end.html')

#------------------LOGOUT--------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('home2.html')

#------------Make New Dir DatTime.Now ----------------------------------   
@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    dirname=''
    if request.method == "POST":
        if request.files:
            print("REQUEST FILES")
            image = request.files["image"]
            print("IMAGE")
            image.save(os.path.join(app.config["IMAGE_UPLOADS"]+'Uploads\\', image.filename))
            dirname=str(datetime.datetime.now())
            dirname=dirname.replace(':','')
            dirname=dirname.replace('-','')
            dirname=dirname.replace(' ','')
            newpath = r'C:\Users\NIKHIL\Desktop\Setup\Folders\Development\Hackathon\STANDARD CHARTERED\website\kyc-verification\\imgdatabase'+str(dirname) +'\\Dataset'
            print(image.filename)
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            if allowed_pdf(image.filename):
                formImg(image.filename,dirname)     
            else:
                print(image.filename) 
                formDirectImg(image.filename,dirname)  
    return render_template('stp2.html',dirname=dirname)

#------------If the file is PDF----------------------------------------------------
def allowed_pdf(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() =='pdf'

count1=0
#-------------- Get Images from PDF & extracting Faces---------------------------------------
def formImg(fileName,dirname):
    doc = fitz.open(app.config["IMAGE_UPLOADS"] + 'Uploads\\' + fileName)
    if len(doc) != 0:
        print(len(doc))
    counter = 0
    for i in range(len(doc)):
        for img in doc.getPageImageList(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:       # this is GRAY or RGB
                pix.writePNG(r"C:\Users\NIKHIL\Desktop\Setup\Folders\Development\Hackathon\STANDARD CHARTERED\website\kyc-verification\imgdatabase{dirname}\Dataset\img%s.png" % i)
                counter += 1
            else:               # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)  
                pix.writePNG(r"C:\Users\NIKHIL\Desktop\Setup\Folders\Development\Hackathon\STANDARD CHARTERED\website\kyc-verification\imgdatabase{dirname}\Dataset\img%s.png" % i)
                pix1 = None
                counter += 1
            pix = None

    global count1
    count1 = 0
    for i in range(0, counter):
        imagePath = r"C:\Users\NIKHIL\Desktop\Setup\Folders\Development\Hackathon\STANDARD CHARTERED\website\kyc-verification\pdf" + str(i) + ".png"
        print(imagePath)
        image = cv2.imread(imagePath)
        print(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print(gray)
        # create the haar cascade
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        # Detect faces in image
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(30, 30)
        )

        print("[INFO] Found {0} Faces.".format(len(faces)))
        padding = 30
        # drawing the rectangles in the image
        for (x, y, w, h) in faces:
            image = cv2.rectangle(image, (x - padding, y - padding), (x + w + padding, y + h + padding), (0, 255, 0), 2)
            roi_color = image[y - 30:y + h + 30, x - 30:x + w + 30]
            print("[INFO] Object found. Saving locally.")
            cv2.imwrite(r'C:\Users\NIKHIL\Desktop\Setup\Folders\Development\Hackathon\STANDARD CHARTERED\website\kyc-verification\imgdatabase{dirname}\Dataset\face' + str(count1) + '.jpg', roi_color)
            count1 = count1 + 1
        status = cv2.imwrite(r'C:\Users\NIKHIL\Desktop\Setup\Folders\Development\Hackathon\STANDARD CHARTERED\website\kyc-verification\faces_detected.jpg', image)
        print('count: ', count1)
        print("[INFO] Image faces_detected.jpg written to filesystem: ", status)
    return ''


#-------------------Getting faces from Image directly---------------------------------
def formDirectImg(filename,dirname):
    print("OK NO PDF ONLY IMAGE")
    global count1
    count1=0
    image = cv2.imread(app.config["IMAGE_UPLOADS"] +'Uploads\\'+ filename)
    cv2.imwrite("C:/Users/NIKHIL/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/imgdatabase{dirname}/Dataset/img0.png", image)
    print(filename,dirname)
    print("Image : ")
    #print(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(gray)
    #create the haar cascade
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    #Detect faces in image
    faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=3,
            minSize=(30, 30)
    )
    print("[INFO] Found {0} Faces.".format(len(faces)))
    padding = 30
    #drawing the rectangles in the image
    for (x, y, w, h) in faces:
        image = cv2.rectangle(image, (x-padding, y-padding),(x + w+padding, y + h+padding), (0, 255, 0), 2)
        roi_color = image[y-30:y + h+30, x-30:x + w+30]
        print("[INFO] Object found. Saving locally.")
        #if(count1==0):
        cv2.imwrite(f'C:/Users/NIKHIL/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/imgdatabase{dirname}/Dataset/face{count1}.jpg', roi_color)
        count1=count1+1
    status = cv2.imwrite('C:/Users/NIKHIL/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/faces_detected.jpg', image)
    print("[INFO] Image faces_detected.jpg written to filesystem: ", status)
    return ''



#-----------Live Video Image Picker ----------------------------------------------------
@app.route('/opencamera',methods=['GET','POST'])    
#-------------------------------CAM SCREENSHOT CODE------------------------------------
def camera():
    dirname=request.form['dirname']
    t=int(1500)
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Test")
    count = 0
    while True and t:
        ret,img=cam.read()
        cv2.imshow("Test", img)
        cv2.waitKey(1)
        
        #cv2.imshow("Test",img)
        mins,secs=divmod(t,60)
		#timer='{:02d}:{02d}'.format(mins,secs)
        if(t==500 or t==1000):
            print("Image "+str(count)+" saved")
            cv2.imwrite(f'C:/Users/NIKHIL/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/imgdatabase{dirname}/Dataset/cam{count}.jpeg', img)
            count +=1
            #time.sleep(1)
            
        time.sleep(0.01)
            
        t-=1
        #cv2.imshow("Test",img)
        if(t==0 and cv2.waitKey(1)):
            print("Close")
            break
    cam.release()
    cv2.destroyAllWindows() 
    compare(dirname)
    # scanqr(dirname)
    return redirect(url_for('stp3'))

#------------- Compare Images ------------------------
def compare(dirname):
    print('Compare')
    global count1
    print('Count1 : ', count1)
    p = open(r'C:/Users/NIKHIL/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/dirname.txt', 'w+')
    p.write(dirname)
    for j in range(2):
        print('Path1 ' + str(j))
        path1 = f'C:/Users/NIKHIL/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/imgdatabase{dirname}/Dataset/cam{j}.jpeg'
        for i in range(0, count1):
            print('Path2 ' + str(i))
            try:
                path2 = f'C:/Users/NIKHIL/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/imgdatabase{dirname}/Dataset/face{i}.jpg'
                print('Comparing image cam' + str(j) + ' & face' + str(i))
                result = DeepFace.verify(img1_path=path1, img2_path=path2, model_name="VGG-Face", distance_metric="cosine")
                threshold = 0.30  # threshold for VGG-Face and Cosine Similarity
                print("Is verified: ", result["verified"])
                f = open(r'C:/Users/NIKHIL/Desktop/Setup/Folders/Development/Hackathon/STANDARD CHARTERED/website/kyc-verification/comparison_result.txt', 'w+')
                
                if result["verified"] == True:
                    f.write('1')
                    return ''
                else:
                    f.write('0')
            except:
                print("There was an issue")
    return ''

#Main
if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()
