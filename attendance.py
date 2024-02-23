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

# Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()
#  Get face landmarks
predictor = dlib.shape_predictor('data_dlib/shape_predictor_68_face_landmarks.dat')

#  Use Dlib resnet50 model to get 128D face descriptor
face_reco_model = dlib.face_recognition_model_v1("data_dlib/dlib_face_recognition_resnet_model_v1.dat")


class Attendance:
    def __init__(self,root, video_source=0):
        self.root=root
        self.root.geometry("880x590")
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
        

        self.faculty_face_recog_start=False
        self.faculty_face_recog_over=False
        self.student_attendance_started=False
        self.student_attendance_over=False
        self.restart_timer = 20 
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
        img=img.resize((880,590))
        self.landingbgd=ImageTk.PhotoImage(img)

        bg_img=Label(self.root,image=self.landingbgd)
        bg_img.place(x=0,y=0,width=880,height=590)

        # title_lbL=Label(bg_img,text="Attendance Taker",font=("times new roman", 30, "bold"), bg="white",fg="red")
        # title_lbL.place(x=0,y=0,width=880,height=50)

       

        # Main frame
        self.main_frame = Frame(bg_img, bd=2, relief=SUNKEN)
        self.main_frame.place(x=17, y=70, width=320, height=480)


        self.init_attendance_btn=Button(bg_img,text="Turn on Face Recognizer",command=self.intialize_attendance,width=20,cursor="hand2",font=("times new roman", 15, "bold"),bg="orange",fg="white")
        self.init_attendance_btn.place(x=50,y=10)

        # Add a Canvas widget for video display
        
        self.canvas = Canvas(bg_img, width=60, height=40)
        self.canvas.place(x=350,y=70,width=500,height=480)

        #top frame
        self.Top_frame=LabelFrame(self.main_frame,bd=2,relief=GROOVE,text="Subject Details",font=("times new roman", 12, "bold"))
        self.Top_frame.place(x=10,y=40,width=300,height=130)

        #middle frame
        self.Middle_frame=LabelFrame(bg_img,bd=2,relief=SUNKEN,font=("times new roman", 12, "bold"))
        self.Middle_frame.place(x=495, y=10,width=215,height=40)

        #bottom frame
        self.Bottom_frame=LabelFrame(self.main_frame,bd=2,relief=RIDGE,text="Student Details",font=("times new roman", 12, "bold"))
        self.Bottom_frame.place(x=10,y=230,width=300,height=170)

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
        self.faculty_face_recog_start=True
        self.faculty_face_recog_over=False
        self.student_attendance_started=False
        self.load__faculty_encodings()

    def take_attendance(self):
        self.faculty_face_recog_over=True
        self.student_attendance_started=True
        self.student_attendance_over=False

        
        self.get_all_subjects()
        self.load__student_encodings()
        
        
        self.update_timer(self.restart_timer)
        # self.face_recog_student()
        # Start the 10-minute timer
          # 600 seconds = 10 minutes

    def end_attendance(self):
        self.student_attendance_started=False
        self.student_attendance_over=True
        self.faculty_face_recog_over=False


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
            self.face_recogition()

            
        

        root.update_idletasks()
        root.update()
        
        
    def reset(self):
        self.mark_attendance()

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
        self.restart_timer = 20

        # Reset flags
        self.faculty_face_recog_start = False
        self.faculty_face_recog_over = False
        self.student_attendance_started = False
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

        if self.attendance_btn:
            self.attendance_btn.destroy()

        if self.end_attendance_btn:
            self.end_attendance_btn.destroy()
        
        for widget in self.Bottom_frame.winfo_children():
            widget.destroy()

        for widget in self.Middle_frame.winfo_children():
            widget.destroy()


    #*************Displaying content******************************

    def display_faculty_info_label(self):
        # self.fetch_faculty_details()
        self.fetch_subject_details()
        welcome_text = "Welcome, " + self.var_faculty_name.get() + "."


        self.faculty_name_label=Label(self.main_frame,text=welcome_text,font=("times new roman", 12, "bold"))
        self.faculty_name_label.place(x=10,y=10)

        self.subject_code_combo=ttk.Combobox(self.Top_frame,textvariable=self.var_subject_code_selected,font=("times new roman", 12, "bold"),state="readonly",width=7)
        self.subject_code_combo["values"]=tuple(self.var_subject_code)
        self.subject_code_combo.current(0)
        self.subject_code_combo.grid(row=0,column=2,padx=2,pady=5,sticky=W)

        self.subject_code_combo.bind("<<ComboboxSelected>>", self.on_subject_code_selected)

        self.fetch_name_label=Label(self.Top_frame,text="",font=("times new roman", 12, "bold"))
        self.fetch_name_label.grid(row=1,column=2)


        self.attendance_btn=Button(self.main_frame,text="Take Attendance",command=self.take_attendance,width=20,cursor="hand2",font=("times new roman", 15, "bold"),bg="darkgreen",fg="white")
        self.attendance_btn.place(x=33,y=180)

        self.end_attendance_btn=Button(self.main_frame,text="End Attendance",command=self.end_attendance,width=20,cursor="hand2",font=("times new roman", 15, "bold"),bg="red",fg="white")
        self.end_attendance_btn.place(x=33,y=420)


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
    # def face_recogition(self):
    #     def draw_boundray_faculty(img,classifier,scaleFactor,minNeighbors,color,text,clf):
    #         gray_image=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #         features=classifier.detectMultiScale(gray_image,scaleFactor,minNeighbors)

    #         coord=[]

    #         for(x,y,w,h) in features:
    #             cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
    #             id,predict=clf.predict(gray_image[y:y+h,x:x+w])
    #             confidence=int((100*(1-predict/300)))
                

    #             if confidence>77:
    #                 if self.var_faculty_name_verify:
    #                     if self.var_faculty_id.get() == str(id):
    #                         self.reset()
    #                         # self.root.after(2000, self.face_recogition)
    #                         return coord
    #                     else:
    #                         messagebox.showerror("Verification Failed","Resuming Attendance")
    #                         self.take_attendance()
    #                         return coord


    #                 self.var_faculty_id.set(id)
    #                 self.fetch_faculty_details()
                    
                    
    #                 cv2.putText(img,f"Faculty Code:{self.var_faculty_code}",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
    #                 cv2.putText(img,f"Name:{self.var_faculty_name}",(x,y-30),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
    #                 cv2.putText(img,f"Department:{self.var_department}",(x,y-55),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
    #                 # if not self.var_faculty_name_verify:

                    
    #                 self.faculty_face_recog_over=True
    #                 self.display_faculty_info_label()
    #             else:
    #                 cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),3)
    #                 cv2.putText(img,"Unknown Face",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),3)
                
    #             coord=[x,y,w,h]
    #         return coord
        
    #     def draw_boundray_student(img,classifier,scaleFactor,minNeighbors,color,text,clf):
    #         gray_image=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #         features=classifier.detectMultiScale(gray_image,scaleFactor,minNeighbors)

    #         coord=[]

    #         for(x,y,w,h) in features:
    #             cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
    #             id,predict=clf.predict(gray_image[y:y+h,x:x+w])
    #             confidence=int((100*(1-predict/300)))

                
                

    #             if confidence>80:
    #                 self.fetch_student_details(id)
    #                 print(f"{self.student_name} : {confidence}")
    #                 cv2.putText(img,f"Name:{self.student_name.get()}",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
    #                 cv2.putText(img,f"Roll No:{self.student_rollno.get()}",(x,y-30),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
    #                 cv2.putText(img,f"Department:{self.student_department.get()}",(x,y-55),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
    #                 self.update_student_info_label()
    #                 self.mark_attendance()
                    
    #             else:
    #                 cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),3)
    #                 cv2.putText(img,"Unknown Face",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),3)
                
    #             coord=[x,y,w,h]
    #         return coord
        
    #     def recognize_faculty(img,clf,faceCascade):
    #         coord=draw_boundray_faculty(img,faceCascade,1.1,15,(255,25,255),"Face",clf)
    #         return img

    #     def recognize_student(img,clf,faceCascade):
    #         coord=draw_boundray_student(img,faceCascade,1.1,20,(255,25,255),"Face",clf)
    #         return img
        
        

        
    #     video_cap = self.vid

    #     while True:      
    #         ret,img=video_cap.read()
    #         if not ret or img is None:
    #         # Break out of the loop if the frame is empty
    #             break


    #         if (self.faculty_face_recog_start and not self.faculty_face_recog_over and not self.student_attendance_started) or (self.student_attendance_over and self.var_faculty_name_verify):  
    #             img=recognize_faculty(img,self.clf1,self.faceCascade)

    #         if self.faculty_face_recog_over and self.student_attendance_started and not self.student_attendance_over:
    #             img=recognize_student(img,self.clf2,self.faceCascade)
            
    #         # cv2.imshow("Welcome to face recognition",img)

    #         # Convert the frame to PIL Image
    #         img = cv2.resize(img, (500, 480))
    #         img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    #         # Display the image on the Tkinter canvas
    #         img_tk = ImageTk.PhotoImage(img)
    #         self.canvas.config(width=img_tk.width(), height=img_tk.height())
    #         self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)

            
    #         root.update_idletasks()
    #         root.update()


                
    def return_euclidean_distance(self,feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        return dist
    
    def get_face_database(self):
        if os.path.exists("faculty/encodings.pickle"):
            with open("faculty/encodings.pickle", "rb") as f:
                id_encodings_dict = pickle.load(f)
            for id in id_encodings_dict.keys():
                self.face_id_known_list.append(id)
                self.face_features_known_list.append(id_encodings_dict[id])
            
            return 1
        else:
            logging.warning("encodings.pickle.csv not found!")
            return 0

    def centroid_tracker(self):
        for i in range(len(self.current_frame_face_centroid_list)):
            e_distance_current_frame_person_x_list = []
            #  For object 1 in current_frame, compute e-distance with object 1/2/3/4/... in last frame
            for j in range(len(self.last_frame_face_centroid_list)):
                self.last_current_frame_centroid_e_distance = self.return_euclidean_distance(
                    self.current_frame_face_centroid_list[i], self.last_frame_face_centroid_list[j])

                e_distance_current_frame_person_x_list.append(
                    self.last_current_frame_centroid_e_distance)

            last_frame_num = e_distance_current_frame_person_x_list.index(
                min(e_distance_current_frame_person_x_list))
            self.current_frame_face_id_list[i] = self.last_frame_face_id_list[last_frame_num]

    def draw_note(self, img_rd):
        #  / Add some info on windows
        cv2.putText(img_rd, "Faces:  " + str(self.current_frame_face_cnt), (20, 20), self.font, 0.8, (0, 255, 0), 1,cv2.LINE_AA)

        # for i in range(len(self.current_frame_face_id_list)):
        #     img_rd = cv2.putText(img_rd, "Face_" + str(i + 1), tuple(
        #         [int(self.current_frame_face_centroid_list[i][0]), int(self.current_frame_face_centroid_list[i][1])]),
        #                          self.font, 0.8, (255, 190, 0), 1, cv2.LINE_AA)

    def face_recog(self,img_rd):   
        
        # 2.  Detect faces for frame X
        faces = detector(img_rd, 1)
        self.recog_success = False

        # 3.  Update cnt for faces in frames
        self.last_frame_face_cnt = self.current_frame_face_cnt
        self.current_frame_face_cnt = len(faces)

        # 4.  Update the face name list in last frame
        self.last_frame_face_id_list = self.current_frame_face_id_list[:]

        # 5.  update frame centroid list
        self.last_frame_face_centroid_list = self.current_frame_face_centroid_list
        self.current_frame_face_centroid_list = []

        # 6.1  if cnt not changes
        if (self.current_frame_face_cnt == self.last_frame_face_cnt) and (self.reclassify_interval_cnt != self.reclassify_interval):
            logging.debug("scene 1:   No face cnt changes in this frame!!!")

            self.current_frame_face_position_list = []

            if "unknown" in self.current_frame_face_id_list:
                self.reclassify_interval_cnt += 1
                    
            if self.current_frame_face_cnt != 0:
                for k, d in enumerate(faces):
                    self.current_frame_face_position_list.append(tuple(
                        [faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))
                    self.current_frame_face_centroid_list.append(
                        [int(faces[k].left() + faces[k].right()) / 2,
                         int(faces[k].top() + faces[k].bottom()) / 2])

                    img_rd = cv2.rectangle(img_rd, tuple([d.left(), d.top()]),tuple([d.right(), d.bottom()]), (255, 255, 255), 2)
                    
            #  Multi-faces in current frame, use centroid-tracker to track
            if self.current_frame_face_cnt != 1:
                self.centroid_tracker()
                    
            for i in range(self.current_frame_face_cnt):
                # if str(self.current_frame_face_id_list[i]) == "unknown":
                    # 6.2 Write names under ROI
                img_rd = cv2.putText(img_rd, str(self.current_frame_face_id_list[i]), self.current_frame_face_position_list[i], self.font, 0.8, (0, 255, 255), 1, cv2.LINE_AA)
            
            

            self.draw_note(img_rd)
                
        # 6.2  If cnt of faces changes, 0->1 or 1->0 or ...
        else:
            logging.debug("scene 2: / Faces cnt changes in this frame")
            self.current_frame_face_position_list = []
            self.current_frame_face_X_e_distance_list = []
            self.current_frame_face_feature_list = []
            self.reclassify_interval_cnt = 0

            # 6.2.1  Face cnt decreases: 1->0, 2->1, ...
            if self.current_frame_face_cnt == 0:
                logging.debug("  / No faces in this frame!!!")
                # clear list of names and features
                self.current_frame_face_id_list = []

            # 6.2.2 / Face cnt increase: 0->1, 0->2, ..., 1->2, ...
            else:
                logging.debug("  scene 2.2  Get faces in this frame and do face recognition")
                self.current_frame_face_id_list = []
                for i in range(len(faces)):
                    shape = predictor(img_rd, faces[i])
                    self.current_frame_face_feature_list.append(
                        face_reco_model.compute_face_descriptor(img_rd, shape))
                    self.current_frame_face_id_list.append("unknown")

                # 6.2.2.1 Traversal all the faces in the database
                for k in range(len(faces)):
                    logging.debug("  For face %d in current frame:", k + 1)
                    self.current_frame_face_centroid_list.append(
                        [int(faces[k].left() + faces[k].right()) / 2,
                         int(faces[k].top() + faces[k].bottom()) / 2])

                    self.current_frame_face_X_e_distance_list = []

                    # 6.2.2.2  Positions of faces captured
                    self.current_frame_face_position_list.append(tuple(
                        [faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))

                    # 6.2.2.3 
                    # For every faces detected, compare the faces in the database
                    for i in range(len(self.face_features_known_list)):
                                 
                        if str(self.face_features_known_list[i][0]) != '0.0':
                            e_distance_tmp = self.return_euclidean_distance(
                                self.current_frame_face_feature_list[k],
                                self.face_features_known_list[i])
                            logging.debug("      with person %d, the e-distance: %f", i + 1, e_distance_tmp)
                            self.current_frame_face_X_e_distance_list.append(e_distance_tmp)
                        else:
                            #  person_X
                            self.current_frame_face_X_e_distance_list.append(999999999)

                    # 6.2.2.4 / Find the one with minimum e distance
                    similar_person_num = self.current_frame_face_X_e_distance_list.index(
                        min(self.current_frame_face_X_e_distance_list))

                    if min(self.current_frame_face_X_e_distance_list) < 0.4:
                        recog_id =self.face_id_known_list[similar_person_num]
                        self.current_frame_face_id_list[k] = recog_id
                        
                        logging.debug("  Face recognition result: %s",
                                      self.face_id_known_list[similar_person_num])

                        # print(type(self.face_id_known_list[similar_person_num]))
                        self.recog_success = True
                        
                        # print(recog_id)
                        
                        # print(name)
                                
                    else:
                        logging.debug("  Face recognition result: Unknown person")
                        
                    

                # 7.  / Add note on cv2 window
                self.draw_note(img_rd)
        return img_rd


        

    def face_recogition(self):
         
        video_cap = self.vid

        while True:      
            ret,img=video_cap.read()
            if not ret or img is None:
            # Break out of the loop if the frame is empty
                break

            # Faculty recognition
            if (self.faculty_face_recog_start and not self.faculty_face_recog_over and not self.student_attendance_started) or (self.student_attendance_over and self.var_faculty_name_verify):  
                img=self.face_recog(img)

                if self.recog_success:
                    

                    for i in range(self.current_frame_face_cnt):
                        
                        id = self.current_frame_face_id_list[i]

                        if id != "unknown":
                            self.var_faculty_id.set(id)
                            self.fetch_faculty_details()

                            self.current_frame_face_id_list[i] = self.var_faculty_name.get()

                        
                            if self.var_faculty_name_verify:
                                if self.var_faculty_id.get() == str(id):
                                    self.reset()
                                    # self.root.after(2000, self.face_recogition)
                                else:
                                    messagebox.showerror("Verification Failed","Resuming Attendance")
                                    self.take_attendance()
                            else:
                                self.faculty_face_recog_over=True
                                self.display_faculty_info_label()

                    self.current_frame_face_position_list = []
                    self.current_frame_face_X_e_distance_list = []
                    self.current_frame_face_feature_list = []
                    self.reclassify_interval_cnt = 0
                    self.current_frame_face_cnt == 0
                    
                    


            # Student recognition
            if self.faculty_face_recog_over and self.student_attendance_started and not self.student_attendance_over:
                img=self.face_recog(img)

                if self.recog_success:

                    for i in range(self.current_frame_face_cnt):

                        if id != "unknown":
                            id = self.current_frame_face_id_list[i]
                            self.fetch_student_details(id)

                            self.current_frame_face_id_list[i] = self.student_name.get()

                            # cv2.putText(img, f"Name:{self.student_name.get()}", self.current_frame_face_position_list[i], self.font, 0.8, (0, 255, 255), 1, cv2.LINE_AA)
                            self.update_student_info_label()
                            self.mark_attendance()
                    
                    self.current_frame_face_position_list = []
                    self.current_frame_face_X_e_distance_list = []
                    self.current_frame_face_feature_list = []
                    self.reclassify_interval_cnt = 0
                    self.current_frame_face_cnt == 0
            

            # Convert the frame to PIL Image
            img = cv2.resize(img, (500, 480))
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            # Display the image on the Tkinter canvas
            img_tk = ImageTk.PhotoImage(img)
            self.canvas.config(width=img_tk.width(), height=img_tk.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)

            
            root.update_idletasks()
            root.update()



    #***********classifier loading functions************************

    def load__student_encodings(self):
        classifier_directory="student/"+str(self.var_degree.get())+"/"+str(self.var_department.get())+"/"+str(self.var_semester.get())
        self.face_id_known_list = []
        self.face_features_known_list = []
        
        
        if os.path.exists(f"{classifier_directory}/encodings.pickle"):
            with open(f"{classifier_directory}/encodings.pickle", "rb") as f:
                id_encodings_dict = pickle.load(f)
            for id in id_encodings_dict.keys():
                self.face_id_known_list.append(id)
                self.face_features_known_list.append(id_encodings_dict[id])
            print("size:")
            print(len(self.face_features_known_list))
            return 1
        else:
            logging.warning("encodings.pickle.csv not found!")
            return 0

    def load__faculty_encodings(self):
        self.face_id_known_list = []
        self.face_features_known_list = []

        if os.path.exists("faculty/encodings.pickle"):
            with open("faculty/encodings.pickle", "rb") as f:
                id_encodings_dict = pickle.load(f)
            for id in id_encodings_dict.keys():
                self.face_id_known_list.append(id)
                self.face_features_known_list.append(id_encodings_dict[id])
            print("size faculty:")
            print(len(self.face_features_known_list))
            return 1
        else:
            logging.warning("encodings.pickle.csv not found!")
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




        



# Provide your camera source index if it's not the default (0)
camera_source_index = 0

if __name__=="__main__":
    root=Tk()
    obj=Attendance(root, video_source=camera_source_index)
    root.mainloop()