## E-KYC Verification


**Problem Statement:**<br>
In the present scenario, the process of KYC verification is a tedious, largely offline and manual process. Subsequently when it is an online process, it is a non-interactive one which cannot be understood clearly by the older generation and the people with a slightly lower level of education.<br>  
In this project, we shall be solving this problem by building an interactive website.

**Tech Stack Used:**

 1. Flask (backend)
 2. Vanilla CSS
 3. HTML
 4. SQLITE(Database)

# Project Workflow:
<img width="934" alt="Screenshot 2024-07-07 at 4 04 02 PM" src="https://github.com/ackerman29/e-KYC-verification/assets/104158912/c854d670-1e1f-47e9-815b-86c656de47c1">

 
 In this project we have used **PyMuPDF** python library to extract the image from the document.<br> 
 To compare the image extracted and the image from the live camera we have used **DeepFace** python library
 
## The steps involved in our project are: <br>	

**Step 1:** The Basic Details of the Person is captured and stored. <br>

**Step 2:** In this step, the individual wanting to complete KYC will upload the Aadhar/Pan card & Face extraction of the person from the ID Card takes place.<br>

**Step 3:** In this step, the Live Video of the Person will be captured and screenshots will be taking during the live video. This image of the person is then stored which is matched with the face of the document submitted.<br>

**Step 4:** Finally, if the Match is successful the KYC Process will be successfully completed.

## Video Demo

https://github.com/nt6095/e-KYC-verification/assets/69105829/f2a4575f-b60c-44b0-9d94-e55b4876812e

**Demo Video** - [https://drive.google.com/file/d/1lVaULSsKON_sjkBrKxPQhWEcrj1uz83L/view?usp=sharing]


