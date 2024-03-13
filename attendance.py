from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
import tkinter.messagebox as messagebox
import mysql.connector
import cv2
import os
import numpy as np
import csv
import pandas as pd
import tkinter as tk
import threading
import pickle
import logging
import dlib
import time
import concurrent.futures


# Provide your camera source index if it's not the default (0)
camera_source_index = 0

# Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()
#  Get face landmarks
predictor = dlib.shape_predictor('data_dlib/shape_predictor_68_face_landmarks.dat')

#  Use Dlib resnet50 model to get 128D face descriptor
face_reco_model = dlib.face_recognition_model_v1("data_dlib/dlib_face_recognition_resnet_model_v1.dat")


class Attendance:
    def __init__(self,root, video_source=0):
        self.root=root
        self.root.geometry("710x410")
        self.root.title("Attendance taker")

        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)

        if not self.vid.isOpened():
            print("Error: Could not open camera.")
            self.root.destroy()
            return
    
        # Create a lock for thread-safe updates
        self.label_update_lock = threading.Lock()
        
        
        # self.load_lbph_classifier()

        # Establish MySQL connection
        self.conn = self.create_connection()

        self.var_faculty_id=StringVar()
        self.var_faculty_name=StringVar()
        self.var_faculty_code=StringVar()
        self.var_faculty_name_verify=False
        
        self.var_subjectId=StringVar()

        self.var_subject_code=[]
        self.var_subject_code.append("Select")
        self.var_subject_code_selected=StringVar()

        self.var_subject_name=StringVar()

        self.var_degree=StringVar()
        self.var_department=StringVar()
        self.var_semester=StringVar()

        self.student_name=StringVar()
        self.student_rollno=StringVar()
        self.student_department=StringVar()
        self.student_division=StringVar()

        self.var_timer=StringVar()
        
        self.csv_subject_code=[]

        self.recog_faculty_mode = False
        self.recog_student_mode = False
        
        

        self.faculty_face_recog_start=False
        self.faculty_face_recog_over=False
        self.student_attendance_started=False
        self.student_attendance_over=False
        self.restart_timer = 60 
        # self.faceCascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        self.recog_success = False
        self.font = cv2.FONT_ITALIC
        self.frame_index = int()
        #  Save the features of faces in the database
        self.face_features_known_list = []
        # / Save the name of faces in the database
        self.face_id_known_list = []

        #  List to save centroid positions of ROI in frame N-1 and N
        self.last_frame_face_centroid_list = []
        self.current_frame_face_centroid_list = []

        # List to save names of objects in frame N-1 and N
        self.last_frame_face_id_list = []
        self.current_frame_face_id_list = []

        #  cnt for faces in frame N-1 and N
        self.last_frame_face_cnt = 0
        self.current_frame_face_cnt = 0

        # Save the e-distance for faceX when recognizing
        self.current_frame_face_X_e_distance_list = []

        # Save the positions and names of current faces captured
        self.current_frame_face_position_list = []
        #  Save the features of people in current frame
        self.current_frame_face_feature_list = []

        # e distance between centroid of ROI in last and current frame
        self.last_current_frame_centroid_e_distance = 0

        #  Reclassify after 'reclassify_interval' frames
        self.reclassify_interval_cnt = 0
        self.reclassify_interval = 5




        self.student_ids = []

        #landing page image and title
        img=Image.open(r"D:\SVNIT\SEMSTER-8\Project\Project_1\Photos\background_page.jpg")
        img=img.resize((710,410))
        self.landingbgd=ImageTk.PhotoImage(img)

        self.bg_img=Label(self.root,image=self.landingbgd)
        self.bg_img.place(x=0,y=0,width=710,height=410)

        # title_lbL=Label(self.bg_img,text="Attendance Taker",font=("times new roman", 30, "bold"), bg="white",fg="red")
        # title_lbL.place(x=0,y=0,width=880,height=50)

       

        # Main frame
        self.main_frame = Frame(self.bg_img, bd=2, relief=SUNKEN)
        self.main_frame.place(x=17, y=70, width=320, height=315)


        # Add a Canvas widget for video display
        
        self.canvas = Canvas(self.bg_img, width=60, height=40)
        self.canvas.place(x=350,y=70,width=335,height=315)

        #top frame
        self.Top_frame=LabelFrame(self.main_frame,bd=2,relief=GROOVE,text="Subject Details",font=("times new roman", 12, "bold"))
        self.Top_frame.place(x=10,y=40,width=300,height=100)

        #middle frame
        self.Middle_frame=LabelFrame(self.bg_img,bd=2,relief=SUNKEN,font=("times new roman", 12, "bold"))
        self.Middle_frame.place(x=413, y=10,width=215,height=40)

        #bottom frame
        self.Bottom_frame=LabelFrame(self.main_frame,bd=2,relief=RIDGE,text="Student Details",font=("times new roman", 12, "bold"))
        self.Bottom_frame.place(x=10,y=160,width=300,height=140)

        #buttons frame
        self.Button_frame=LabelFrame(self.bg_img,bd=2,relief=RIDGE,font=("times new roman", 12, "bold"))
        self.Button_frame.place(x=47,y=10,width=254,height=44)

        
        self.init_attendance_btn=Button(self.Button_frame,text="Turn on Face Recognizer",command=self.intialize_attendance,width=20,cursor="hand2",font=("times new roman", 15, "bold"),bg="orange",fg="white")
        self.init_attendance_btn.place(x=0,y=0)



        # #bottom frame
        # self.Marked_frame=LabelFrame(self.Bottom_frame,bd=2,relief=GROOVE)
        # self.Marked_frame.place(x=10,y=150,width=200,height=30)

        #name
        name_label=Label(self.Top_frame,text="Name: ",font=("times new roman", 12, "bold"))
        name_label.grid(row=1,column=1,padx=2,pady=5,sticky=W)

        subject_code_label=Label(self.Top_frame,text="Code:",font=("times new roman", 12, "bold"))
        subject_code_label.grid(row=0,column=1,padx=2,pady=5,sticky=W)




        # self.load__faculty_encodings()
        self.face_recogition()



            

  

    #create database connection*********************
    def create_connection(self):
        return mysql.connector.connect(
            host="localhost",
            username="root",
            password="Drishey@9845",
            database="face_recognizer"
        )
    

    #******************fetch data*****************


    def fetch_faculty_details(self):
        my_cursor=self.conn.cursor()
        my_cursor.execute("SELECT Faculty_code,Name,Department FROM faculty WHERE facultyId=%s",(self.var_faculty_id.get(),))
        data=my_cursor.fetchall()

        if len(data)!=0:
            for i in data:
                self.var_faculty_code.set(i[0])
                self.var_faculty_name.set(i[1])
                self.var_department.set(i[2])

            self.conn.commit()    
             
    def fetch_student_details(self,id):
        my_cursor=self.conn.cursor()
        my_cursor.execute("SELECT Name,Roll_no,Department,Division FROM student WHERE studentId="+str(id))
        result=my_cursor.fetchone()

        if len(result)!=0: 
            self.student_name.set(result[0])
            self.student_rollno.set(result[1])
            self.student_department.set(result[2])
            self.student_division.set(result[3])

            self.conn.commit()   

    def fetch_subject_details(self):
        my_cursor=self.conn.cursor()
        my_cursor.execute("SELECT Subject_code from subject where Department=%s and Faculty_1_code=%s",(self.var_department.get(),self.var_faculty_code.get(),))
        data=my_cursor.fetchall()
        
        if len(data)!=0:
            for i in data:
                self.var_subject_code.append(i[0])
            self.conn.commit()
    
    def get_subject_details(self):

        # Check if the selected subject code is not "Select"
        if self.var_subject_code_selected.get() != "Select":
            my_cursor = self.conn.cursor()
            my_cursor.execute("SELECT Name, Degree, Semester FROM subject WHERE Subject_code=%s", (self.var_subject_code_selected.get(),))
            data = my_cursor.fetchall()

            if len(data) != 0:
                for i in data:
                    self.var_subject_name.set(i[0])
                    self.var_degree.set(i[1])
                    self.var_semester.set(i[2])
            
                
                
            

            self.conn.commit()

    def get_all_subjects(self):

        # Check if the selected subject code is not "Select"
        if self.var_subject_code_selected.get() != "Select":
            my_cursor = self.conn.cursor()
            details=(self.var_degree.get(),
                     self.var_department.get(),
                     self.var_semester.get(),)
            my_cursor.execute("SELECT Subject_code FROM subject WHERE Degree=%s and Department=%s and Semester=%s", details)
            data = my_cursor.fetchall()

            if len(data) != 0:
                for i in data:
                    self.csv_subject_code.append(i[0])
            
                
                

            self.conn.commit()

    def on_subject_code_selected(self, event):
        self.get_subject_details()
        if self.fetch_name_label:
            self.fetch_name_label.destroy()

        self.fetch_name_label=Label(self.Top_frame,text=self.var_subject_name.get(),font=("times new roman", 12, "bold"))
        self.fetch_name_label.grid(row=1,column=2)
        # Update the displayed subject name
        


    
    #*************Attendance managing functions********************

    def intialize_attendance(self):
        self.recog_faculty_mode=True
        self.recog_student_mode = False

        self.faculty_face_recog_start=True
        self.faculty_face_recog_over=False
        self.student_attendance_started=False
        self.load__faculty_encodings()

        
        

    def take_attendance(self):

        self.recog_student_mode = True
        self.recog_faculty_mode = False

        self.student_attendance_over=False

        
        self.get_all_subjects()
        self.load__student_encodings()

        
        self.reclassify_interval_cnt = 5
        self.last_frame_face_cnt == 0
        
        
        self.update_timer(self.restart_timer)

        if self.attendance_btn:
            self.attendance_btn.destroy()

        self.end_attendance_btn=Button(self.Button_frame,text="End Attendance",command=self.end_attendance,width=20,cursor="hand2",font=("times new roman", 15, "bold"),bg="red",fg="white")
        self.end_attendance_btn.place(x=0,y=0)
        # self.face_recog_student()
        # Start the 10-minute timer
          # 600 seconds = 10 minutes

    def end_attendance(self):
        self.student_attendance_over=True


    #***********timer and reset function***************************          

    def update_timer(self, remaining_time):
        minutes, seconds = divmod(remaining_time, 60)
        timer_text = f"Time Left: {minutes:02d}:{seconds:02d}"
        self.var_timer.set(timer_text)

        self.timer_label = Label(self.Middle_frame, text=self.var_timer.get(), font=("times new roman", 20, "bold"),fg="red")
        self.timer_label.grid(row=0,column=0,padx=5)

        # if self.student_attendance_over:
        #     remaining_time=0

        self.restart_timer=remaining_time
        
        if remaining_time > 0 :
            
            if self.student_attendance_over:
                Ended=messagebox.askyesno("Attendance Completed","Do you want to end attendance",parent=self.root)
                if Ended>0:
                    messagebox.showinfo("Verification", "Show faculty face to end the attendance")
                    self.var_faculty_name_verify=True
                    self.recog_faculty_mode = True
                    self.recog_student_mode = False
                    self.load__faculty_encodings()
                    return
                else:
                    if not Ended:
                        self.take_attendance()
                        return
       
            self.root.after(1000, self.update_timer, remaining_time - 1)
        else:
            messagebox.showinfo("Attendance Completed", "Attendance session has ended.")
            self.end_attendance()
            self.reset()
            # self.face_recogition()

            
        

        root.update_idletasks()
        root.update()
        
        
    def reset(self):
        self.mark_attendance()

        
        self.reclassify_interval_cnt = 5
        self.last_frame_face_cnt  == 0

        # Clear faculty details
        self.var_faculty_id.set("")
        self.var_faculty_code.set("")
        self.var_faculty_name.set("")
        self.var_department.set("")
        self.var_subject_code_selected.set("")
        self.var_subject_name.set("")
        self.var_degree.set("")
        self.var_semester.set("")
        self.csv_subject_code=[]

        self.var_subject_code=[]
        self.var_subject_code.append("Select")

        # Clear student details
        self.student_name.set("")
        self.student_rollno.set("")
        self.student_department.set("")
        self.student_division.set("")

        # Clear timer
        self.var_timer.set("")
        self.restart_timer = 60

        self.current_frame_face_cnt = 0

        # Reset flags
        self.recog_faculty_mode = False
        self.recog_student_mode = False

        
        self.student_attendance_over = False
        self.var_faculty_name_verify=False

        # Clear canvas
        self.canvas.delete("all")

        # Clear labels

        if self.fetch_name_label:
            self.fetch_name_label.destroy()
        
        if self.faculty_name_label:
            self.faculty_name_label.destroy()


        if self.subject_code_combo:
            self.subject_code_combo.destroy()

        # if self.attendance_btn:
        #     self.attendance_btn.destroy()

        if self.end_attendance_btn:
            self.end_attendance_btn.destroy()
        
        for widget in self.Bottom_frame.winfo_children():
            widget.destroy()

        for widget in self.Middle_frame.winfo_children():
            widget.destroy()
        
        self.init_attendance_btn=Button(self.Button_frame,text="Turn on Face Recognizer",command=self.intialize_attendance,width=20,cursor="hand2",font=("times new roman", 15, "bold"),bg="orange",fg="white")
        self.init_attendance_btn.place(x=0,y=0)


    #*************Displaying content******************************

    def display_faculty_info_label(self):
        # self.fetch_faculty_details()
        self.fetch_subject_details()
        welcome_text = "Welcome, " + self.var_faculty_name.get() + "."

        if self.init_attendance_btn:
            self.init_attendance_btn.destroy()


        self.faculty_name_label=Label(self.main_frame,text=welcome_text,font=("times new roman", 12, "bold"))
        self.faculty_name_label.place(x=10,y=10)

        self.subject_code_combo=ttk.Combobox(self.Top_frame,textvariable=self.var_subject_code_selected,font=("times new roman", 12, "bold"),state="readonly",width=7)
        self.subject_code_combo["values"]=tuple(self.var_subject_code)
        self.subject_code_combo.current(0)
        self.subject_code_combo.grid(row=0,column=2,padx=2,pady=5,sticky=W)

        self.subject_code_combo.bind("<<ComboboxSelected>>", self.on_subject_code_selected)

        self.fetch_name_label=Label(self.Top_frame,text="",font=("times new roman", 12, "bold"))
        self.fetch_name_label.grid(row=1,column=2)


        self.attendance_btn=Button(self.Button_frame,text="Take Attendance",command=self.take_attendance,width=20,cursor="hand2",font=("times new roman", 15, "bold"),bg="darkgreen",fg="white")
        self.attendance_btn.place(x=0,y=0)

        self.student_fetch_name_label=Label(self.Bottom_frame,text="",font=("times new roman", 12, "bold"))
        self.student_fetch_name_label.grid(row=0,column=2,padx=2,pady=5,sticky=W)

        self.student_fetch_rollno_label=Label(self.Bottom_frame,text="",font=("times new roman", 12, "bold"))
        self.student_fetch_rollno_label.grid(row=1,column=2,padx=2,pady=5,sticky=W)

        self.student_fetch_department_label=Label(self.Bottom_frame,text="",font=("times new roman", 12, "bold"))
        self.student_fetch_department_label.grid(row=2,column=2,padx=2,pady=5,sticky=W)


    def update_student_info_label(self):
        # Create labels to display student information 
        student_name_label = Label(self.Bottom_frame, text="Name:", font=("times new roman", 12, "bold"))
        student_name_label.grid(row=0,column=1,padx=2,pady=5,sticky=W)

        student_rollno_label = Label(self.Bottom_frame, text="Roll no:", font=("times new roman", 12, "bold"))
        student_rollno_label.grid(row=1,column=1,padx=2,pady=5,sticky=W)

        student_department_label = Label(self.Bottom_frame, text="Department:", font=("times new roman", 12, "bold"))
        student_department_label.grid(row=2,column=1,padx=2,pady=5,sticky=W)

        if self.student_fetch_name_label:
            self.student_fetch_name_label.destroy()

        if self.student_fetch_rollno_label:
            self.student_fetch_rollno_label.destroy()

        if self.student_fetch_department_label:
            self.student_fetch_department_label.destroy()


        self.student_fetch_name_label=Label(self.Bottom_frame,text=self.student_name.get(),font=("times new roman", 12, "bold"))
        self.student_fetch_name_label.grid(row=0,column=2,padx=2,pady=5,sticky=W)

        self.student_fetch_rollno_label=Label(self.Bottom_frame,text=self.student_rollno.get(),font=("times new roman", 12, "bold"))
        self.student_fetch_rollno_label.grid(row=1,column=2,padx=2,pady=5,sticky=W)

        self.student_fetch_department_label=Label(self.Bottom_frame,text=self.student_department.get(),font=("times new roman", 12, "bold"))
        self.student_fetch_department_label.grid(row=2,column=2,padx=2,pady=5,sticky=W)

        # marked_text = "Marked attendance " + "✔️"


        # self.marked_label=Label(self.main_frame,text=marked_text,font=("times new roman", 12, "bold"))
        # self.marked_label.grid(row=3,column=2)



    #*****************Recognizer function******************  
    def return_euclidean_distance(self,feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        # dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        dist = np.linalg.norm(feature_1 - feature_2)
        return dist

    
    def face_recog(self,img_rd): 

        # 2.  Detect faces for frame X
        faces = detector(img_rd, 0)

        # 3.  Update cnt for faces in frames
        self.last_frame_face_cnt = self.current_frame_face_cnt
        self.current_frame_face_cnt = len(faces)

        for face in faces:
            # Get the coordinates of the bounding box
            left, top, right, bottom = face.left(), face.top(), face.right(), face.bottom()

            if (self.current_frame_face_cnt == self.last_frame_face_cnt):
                    logging.debug("No face cnt changes in this frame")
                    # print("not")
            else:
                # Extract face features
                print("predicting") 
                shape = predictor(img_rd, face)
                face_encodings = face_reco_model.compute_face_descriptor(img_rd, shape)
                        
                predicted_label = self.classifier.predict([face_encodings])[0]

                known_face_encodings = self.encodings[predicted_label]
                        
                euclidean_distance = self.return_euclidean_distance(face_encodings, known_face_encodings)
                        
                min_distance = np.min(euclidean_distance)   
                print(min_distance)

                # If the minimum distance is below threshold, classify as known, else unknown
                if min_distance < 0.5:

                    if self.recog_faculty_mode:
                        self.label_text = self.faculty_operation(predicted_label)
                        self.current_frame_face_cnt = 0
                    elif self.recog_student_mode:
                        self.label_text = self.student_operation(predicted_label)
                    else:
                        print("none")

                else:
                    self.label_text = "Unknown"

                print(self.label_text)
                time.sleep(0.5)
            
            

            # Draw the face boundary
            cv2.rectangle(img_rd, (left, top), (right, bottom), (255, 255, 255), 2)

            # Display the predicted label
            cv2.putText(img_rd, self.label_text, (left, bottom + 20), self.font, 0.8, (0, 255, 255), 1, cv2.LINE_AA)
            

        return img_rd


    def face_recogition(self):
         
        video_cap = self.vid
        executor = concurrent.futures.ThreadPoolExecutor()
        futures = []
        self.frame_count = 0

        while True:      
            ret,img=video_cap.read()
            if not ret or img is None:
                break
            
            img = cv2.resize(img, (335, 315))
            
            if self.recog_faculty_mode or self.recog_student_mode:
                self.frame_count+=1
                # print(self.frame_count)
                img=self.face_recog(img)

            
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            # Display the image on the Tkinter canvas
            img_tk = ImageTk.PhotoImage(img)

            # Delete previous image from canvas
            self.canvas.delete("all")

            self.canvas.config(width=img_tk.width(), height=img_tk.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)

            
            root.update_idletasks()
            root.update()


    def faculty_operation(self,id):
        self.var_faculty_id.set(id)
        self.fetch_faculty_details()


        if self.var_faculty_name_verify:
            if self.var_faculty_id.get() == str(id):
                self.reset()
                return "" 
            else:
                messagebox.showerror("Verification Failed","Resuming Attendance")
                self.take_attendance()
        else:
            self.recog_faculty_mode=False
            self.display_faculty_info_label()

        return self.var_faculty_name.get()
    
    def student_operation(self,id):
        self.fetch_student_details(id)
   
        # cv2.putText(img, f"Name:{self.student_name.get()}", self.current_frame_face_position_list[i], self.font, 0.8, (0, 255, 255), 1, cv2.LINE_AA)
        self.update_student_info_label()
        self.mark_attendance()


        return self.student_name.get()
    



    #***********encodings loading functions************************
    def load__student_encodings(self):
        user_directory="student/"+str(self.var_degree.get())+"/"+str(self.var_department.get())+"/"+str(self.var_semester.get())
        feature_file = user_directory + "/encodings.pkl"
        classifier_file = user_directory + "/classifier.pkl"
        
        
        if os.path.exists(feature_file) and os.path.exists(classifier_file):
            with open(feature_file, "rb") as f:
                self.encodings = pickle.load(f)
            with open(classifier_file, "rb") as f:
                self.classifier = pickle.load(f)
            return 1
        else:
            logging.warning("encodings.pickle.csv not found!")
            return 0

    def load__faculty_encodings(self):
        if os.path.exists("faculty/classifier.pkl") and os.path.exists("faculty/encodings.pkl"):
            with open("faculty/encodings.pkl", "rb") as f:
                self.encodings = pickle.load(f)
            with open("faculty/classifier.pkl", "rb") as f:
                self.classifier = pickle.load(f)
            return 1
        else:
            logging.warning("encodings.pkl or classifier.pkl not found!")
            return 0


    #***************marking attendance******************************
    def mark_attendance(self):
        degree_path = os.path.join("student", self.var_degree.get())
        department_path = os.path.join(degree_path, self.var_department.get())
        semester_path = os.path.join(department_path, self.var_semester.get())

        if not os.path.exists(degree_path):
            os.makedirs(degree_path)
        if not os.path.exists(department_path):
            os.makedirs(department_path)
        if not os.path.exists(semester_path):
            os.makedirs(semester_path)

        # CSV file path
        csv_file_path = os.path.join(semester_path, f"attendance.csv")
        # CSV file path
        csv_total_file_path = os.path.join(semester_path, f"total_classes.csv")


        # Check if CSV file exists, create one if not
        if not os.path.exists(csv_file_path):
            header = ["Name"] + ["Roll_no"] + ["Division"] + ["Flag"] + self.csv_subject_code   # Add "Flag" column to header
            pd.DataFrame(columns=header).to_csv(csv_file_path, index=False)
        
        # Check if CSV file exists, create one if not
        if not os.path.exists(csv_total_file_path):
            new_header = ["Classes"] + self.csv_subject_code  # Add "Flag" column to header
            pd.DataFrame(columns=new_header).to_csv(csv_total_file_path, index=False)
            
        df = pd.read_csv(csv_file_path)
        df2 = pd.read_csv(csv_total_file_path)

        student_name = self.student_name.get()
        student_rollno = self.student_rollno.get()
        student_division = self.student_division.get()

        # Check if the student already exists in the CSV file (case-insensitive)
        student_exists = df[df['Name'].str.lower() == student_name.lower()]
        
        total_exists = df2[df2['Classes'].str.lower() == "total"]


        if self.student_attendance_over:
            df["Flag"] = False
            df.to_csv(csv_file_path, index=False)

            if total_exists.empty:
                new_row = {'Classes': 'total'}
                for code in self.csv_subject_code:
                    new_row[code] = 0
                new_row[self.var_subject_code_selected.get()] = 1
                    
                df2 = pd.concat([df2, pd.DataFrame([new_row])], ignore_index=True)
            else: 
                # Update the count for the specific subject code
                df2.loc[total_exists.index, self.var_subject_code_selected.get()] += 1

            df2.to_csv(csv_total_file_path, index=False)
            
            
            return
        else:
            # If the student is not in the CSV file, add a new row
            if student_exists.empty:
                new_row = {'Name': student_name, 'Roll_no': student_rollno, 'Division': student_division}
                
                new_row[self.var_subject_code_selected.get()] = 1
                new_row["Flag"] = True  # Set "Flag" to True
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            else:
                # Check if attendance is already marked
                if df.loc[student_exists.index, "Flag"].any():
                    return

                # Update the count for the specific subject code
                df.loc[student_exists.index, self.var_subject_code_selected.get()] += 1
                df.loc[student_exists.index, "Flag"] = True

            # Write back the updated data to CSV file
            df.to_csv(csv_file_path, index=False)



if __name__=="__main__":
    root=Tk()
    obj=Attendance(root, video_source=camera_source_index)
    root.mainloop()