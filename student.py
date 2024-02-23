from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
import tkinter.messagebox as messagebox
import mysql.connector
import cv2
import os
import numpy as np
import logging
import shutil
import dlib
import pandas as pd
import csv
import time

# Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()
#  Get face landmarks
predictor = dlib.shape_predictor('data_dlib/shape_predictor_68_face_landmarks.dat')

#  Use Dlib resnet50 model to get 128D face descriptor
face_reco_model = dlib.face_recognition_model_v1("data_dlib/dlib_face_recognition_resnet_model_v1.dat")


class Student:
    FILTER_OPTIONS_MAPPING = {
        "B.Tech": {
            "Department": ["CSE", "ECE", "EE", "ME", "CE", "CHE"],
            "Semester": ["Semester-1","Semester-2","Semester-3","Semester-4","Semester-5","Semester-6","Semester-7","Semester-8"],
            "Division": {"CSE":["Division-A","Division-B"],
                        "ECE":["Division-A","Division-B"],
                        "EE":["Division-A","Division-B","Division-C"],
                        "ME":["Division-A","Division-B","Division-C","Division-D","Division-E"],
                        "CE":["Division-A","Division-B","Division-C"],
                        "CHE":["Division-A","Division-B"],
                        },
            
        },
        "M.Tech": {
            "Department": ["CSE", "ECE", "EE", "ME"],
            "Semester": ["Semester 1", "Semester 2", "Semester 3", "Semester 4"],
            "Division": ["Division-A","Division-B"]
        }
        
    }

    def __init__(self,root):
        self.root=root
        self.root.geometry("880x590")
        self.root.title("Student Management System")

        # Establish MySQL connection
        self.conn = self.create_connection()

        #****************variables******************
        self.var_degree=StringVar()
        self.var_department=StringVar()
        self.var_semester=StringVar()
        self.var_division=StringVar()
        self.var_name=StringVar()
        self.var_rollno=StringVar()
        self.var_studentId=StringVar()
        self.var_captured_face=StringVar()

        self.var_captured_face.set("No")

        self.search_var_degree=StringVar()
        self.search_var_department=StringVar()
        self.search_var_semester=StringVar()
        self.search_var_division=StringVar()
        self.search_var_caputured=StringVar()

        self.student_ids = []



        #landing page image and title
        img=Image.open(r"D:\SVNIT\SEMSTER-8\Project\Project_1\Photos\background_page.jpg")
        img=img.resize((880,590))
        self.landingbgd=ImageTk.PhotoImage(img)

        bg_img=Label(self.root,image=self.landingbgd)
        bg_img.place(x=0,y=0,width=880,height=590)

        # title_lbL=Label(bg_img,text="Student Management System",font=("times new roman", 30, "bold"),fg="darkgreen")
        # title_lbL.place(x=200,y=0)

        title = Canvas(bg_img,width=500, height=45)
        title.place(x=200,y=10)
        
        sp_img=Image.open(r"D:\SVNIT\SEMSTER-8\Project\Project_1\Photos\background_page_title.png")
        sp_img=sp_img.resize((510,50))
        self.sp_title=ImageTk.PhotoImage(sp_img)

        title.create_image(0, 0, anchor="nw", image=self.sp_title)
        title.create_text(250, 20, text="Student Management System", font=("times new roman", 30, "bold"), fill="darkgreen")


        main_frame=Frame(bg_img,bd=2,relief=SUNKEN)
        main_frame.place(x=17,y=70,width=840,height=500)


        #top frame
        Top_frame=LabelFrame(main_frame,bd=2,relief=RIDGE,text="Degree Information",font=("times new roman", 12, "bold"))
        Top_frame.place(x=10,y=5,width=815,height=160)
        

        #course
        degree_label=Label(Top_frame,text="Degree:",font=("times new roman", 12, "bold"))
        degree_label.grid(row=0,column=1,padx=2,pady=5,sticky=W)

        self.degree_combo=ttk.Combobox(Top_frame,textvariable=self.var_degree,font=("times new roman", 12, "bold"),state="readonly",width=7)
        self.degree_combo["values"]=("Select","B.Tech","M.Tech")
        self.degree_combo.current(0)
        self.degree_combo.grid(row=0,column=2,padx=2,pady=5,sticky=W)
        self.degree_combo.bind("<<ComboboxSelected>>", self.load_departments)

        #department
        dep_label=Label(Top_frame,text="Department:",font=("times new roman", 12, "bold"))
        dep_label.grid(row=1,column=1,padx=2,pady=5,sticky=W)

        self.dep_combo=ttk.Combobox(Top_frame,textvariable=self.var_department,font=("times new roman", 12, "bold"),state="readonly",width=7)
        self.dep_combo["values"]=("Select")
        self.dep_combo.current(0)
        self.dep_combo.grid(row=1,column=2,padx=2,pady=5,sticky=W)
        self.dep_combo.bind("<<ComboboxSelected>>", self.load_divisions)

        #semester
        sem_label=Label(Top_frame,text="Semester:",font=("times new roman", 12, "bold"))
        sem_label.grid(row=0,column=7,padx=10,pady=5,sticky=W)

        self.sem_combo=ttk.Combobox(Top_frame,textvariable=self.var_semester,font=("times new roman", 12, "bold"),state="readonly",width=10)
        self.sem_combo["values"]=("Select")
        self.sem_combo.current(0)
        self.sem_combo.grid(row=0,column=8,padx=2,pady=5,sticky=W)

        #division
        division_label=Label(Top_frame,text="Division:",font=("times new roman", 12, "bold"))
        division_label.grid(row=1,column=7,padx=10,pady=5,sticky=W)

        self.division_combo=ttk.Combobox(Top_frame,textvariable=self.var_division,font=("times new roman", 12, "bold"),state="readonly",width=10)
        self.division_combo["values"]=("Select")
        self.division_combo.current(0)
        self.division_combo.grid(row=1,column=8,padx=2,pady=5,sticky=W)

        #name
        name_label=Label(Top_frame,text="Name:",font=("times new roman", 12, "bold"))
        name_label.grid(row=0,column=12,padx=2,pady=5,sticky=W)

        name_entry=ttk.Entry(Top_frame,textvariable=self.var_name,width=20,font=("times new roman",12,"bold"))
        name_entry.grid(row=0,column=13,padx=2,pady=5)

        #roll no
        rollno_label=Label(Top_frame,text="Roll no:",font=("times new roman", 12, "bold"))
        rollno_label.grid(row=1,column=12,padx=2,pady=5,sticky=W)

        rollno_entry=ttk.Entry(Top_frame,textvariable=self.var_rollno,width=20,font=("times new roman",12,"bold"))
        rollno_entry.grid(row=1,column=13,padx=2,pady=5)


        #photo
        photo_frame=LabelFrame(Top_frame,bd=2,relief=RIDGE,text="Student Photo",font=("times new roman", 12, "bold"))
        photo_frame.place(x=620,y=0,width=170,height=125)

        profile_pic=Image.open(r"Photos\student_example.png")
        profile_pic=profile_pic.resize((150,80))
        self.profile_pic=ImageTk.PhotoImage(profile_pic)


        profile_img=Label(photo_frame,image=self.profile_pic)
        profile_img.place(x=5,y=0,width=150,height=100)


        #buttons
        btn_frame=LabelFrame(Top_frame,bd=2,relief=FLAT,font=("times new roman", 12, "bold"))
        btn_frame.place(x=5,y=70,width=610,height=55)

        take_photo=Button(btn_frame,text="Capture Face",command=self.generate_dataset,width=11,cursor="hand2",font=("times new roman", 12, "bold"),bg="magenta3",fg="white")
        take_photo.grid(row=0,column=1,padx=5,pady=8,sticky=W)

        upload_btn=Button(btn_frame,text="Profile Picture",width=11,cursor="hand2",font=("times new roman", 12, "bold"),bg="indian red",fg="white")
        upload_btn.grid(row=0,column=2,padx=5,pady=8,sticky=W)

        save_btn=Button(btn_frame,text="Save",command=self.add_data,width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="green",fg="white")
        save_btn.grid(row=0,column=3,padx=5,pady=8,sticky=W)

        Update_btn=Button(btn_frame,text="Update",command=self.update_data,width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="yellow3",fg="white")
        Update_btn.grid(row=0,column=4,padx=5,pady=8,sticky=W)

        delete_btn=Button(btn_frame,command=self.delete_data,text="Delete",width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="red",fg="white")
        delete_btn.grid(row=0,column=5,padx=5,pady=8,sticky=W)

        reset_btn=Button(btn_frame,text="Reset",command=self.reset_data,width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="grey",fg="white")
        reset_btn.grid(row=0,column=6,padx=5,pady=8,sticky=W)


        
        #bottom frame
        Bottom_frame=LabelFrame(main_frame,bd=2,relief=RIDGE,text="Student Details",font=("times new roman", 12, "bold"))
        Bottom_frame.place(x=10,y=170,width=815,height=310)

        #search frame
        Search_frame=LabelFrame(Bottom_frame,bd=2,relief=GROOVE,font=("times new roman", 12, "bold"),bg="lightgrey")
        Search_frame.place(x=5,y=5,width=800,height=47)

        search_label=Label(Search_frame,text="Filter:",font=("times new roman", 12, "bold"),bg="red",fg="white")
        search_label.grid(row=0,column=1,padx=5,pady=5,sticky=W)


        self.search_degree_combo=ttk.Combobox(Search_frame,textvariable=self.search_var_degree,font=("times new roman", 12, "bold"),state="readonly",width=7)
        self.search_degree_combo["values"]=("Degree","B.Tech","M.Tech")
        self.search_degree_combo.current(0)
        self.search_degree_combo.grid(row=0,column=2,padx=2,pady=5,sticky=W)
        self.search_degree_combo.bind("<<ComboboxSelected>>", self.search_load_departments)

        self.search_dep_combo=ttk.Combobox(Search_frame,textvariable=self.search_var_department,font=("times new roman", 12, "bold"),state="readonly",width=10)
        self.search_dep_combo["values"]=("Department")
        self.search_dep_combo.current(0)
        self.search_dep_combo.grid(row=0,column=3,padx=2,pady=5,sticky=W)
        self.search_dep_combo.bind("<<ComboboxSelected>>", self.search_load_divisions)

        self.search_sem_combo=ttk.Combobox(Search_frame,textvariable=self.search_var_semester,font=("times new roman", 12, "bold"),state="readonly",width=10)
        self.search_sem_combo["values"]=("Semester")
        self.search_sem_combo.current(0)
        self.search_sem_combo.grid(row=0,column=4,padx=2,pady=5,sticky=W)

        self.search_division_combo=ttk.Combobox(Search_frame,textvariable=self.search_var_division,font=("times new roman", 12, "bold"),state="readonly",width=10)
        self.search_division_combo["values"]=("Division")
        self.search_division_combo.current(0)
        self.search_division_combo.grid(row=0,column=5,padx=2,pady=5,sticky=W)

        search_capture_face_combo=ttk.Combobox(Search_frame,textvariable=self.search_var_caputured,font=("times new roman", 12, "bold"),state="readonly",width=10)
        search_capture_face_combo["values"]=("Captured","Yes","No")
        search_capture_face_combo.current(0)
        search_capture_face_combo.grid(row=0,column=6,padx=2,pady=5,sticky=W)

        search_filter_btn=Button(Search_frame,text="Apply Filter",command=self.apply_filter,width=10,cursor="hand2",font=("times new roman", 12, "bold"),bg="cyan4",fg="white")
        search_filter_btn.grid(row=0,column=7,padx=5,pady=5,sticky=W)

        search_showall_btn=Button(Search_frame,text="Show All",command=self.fetch_data,width=10,cursor="hand2",font=("times new roman", 12, "bold"),bg="brown",fg="white")
        search_showall_btn.grid(row=0,column=8,padx=5,pady=5,sticky=W)


        #table frame
        table_frame=LabelFrame(Bottom_frame,bd=2,relief=GROOVE,font=("times new roman", 12, "bold"))
        table_frame.place(x=5,y=50,width=800,height=195)

        # scroll_x=ttk.Scrollbar(table_frame,orient=HORIZONTAL)
        scroll_y=ttk.Scrollbar(table_frame,orient=VERTICAL)

        self.student_table=ttk.Treeview(table_frame,columns=("Student ID","Department","Degree","Semester","Division","Name","Roll no","Captured Face"),yscrollcommand=scroll_y.set)

        # scroll_x.pack(side=BOTTOM,fill=X)
        scroll_y.pack(side=RIGHT,fill=Y)

        # scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        self.student_table.heading("Student ID",text="Student ID")
        self.student_table.heading("Degree",text="Degree")
        self.student_table.heading("Department",text="Department")
        self.student_table.heading("Semester",text="Semester")
        self.student_table.heading("Division",text="Division")
        self.student_table.heading("Name",text="Name")
        self.student_table.heading("Roll no",text="Roll no")
        self.student_table.heading("Captured Face",text="Captured Face")
        self.student_table["show"]="headings"

        self.student_table.column("Name",width=150)
        self.student_table.column("Roll no",width=80)
        self.student_table.column("Semester",width=80)
        self.student_table.column("Division",width=80)
        self.student_table.column("Degree",width=80)
        self.student_table.column("Department",width=80)
        self.student_table.column("Student ID",width=80)
        self.student_table.column("Captured Face",width=80)

        self.student_table.pack(fill=BOTH,expand=1)
        self.student_table.bind("<ButtonRelease>",self.get_cursor)
        self.fetch_data()

        #buttons
        operations_btn_frame=LabelFrame(Bottom_frame,bd=2,relief=FLAT,font=("times new roman", 12, "bold"))
        operations_btn_frame.place(x=5,y=245,width=800,height=43)

        train_data_btn=Button(operations_btn_frame,text="Train Data",width=15,command=self.train_classifier,cursor="hand2",font=("times new roman", 12, "bold"),bg="darkorange",fg="white")
        train_data_btn.grid(row=0,column=1,padx=5,pady=0,sticky=W)

        face_recog_btn=Button(operations_btn_frame,text="Facial Recognition",command=self.face_recog,width=15,cursor="hand2",font=("times new roman", 12, "bold"),bg="blue",fg="white")
        face_recog_btn.grid(row=0,column=2,padx=5,pady=0,sticky=W)

        new_semester_btn=Button(operations_btn_frame,text="New Semester",width=15,cursor="hand2",font=("times new roman", 12, "bold"),bg="green",fg="white")
        new_semester_btn.grid(row=0,column=3,padx=335,pady=0,sticky=W)


    def load_departments(self, event=None):
        if self.var_degree.get() == "Select":
            return
        departments = ["Select"] + self.FILTER_OPTIONS_MAPPING[self.var_degree.get()]["Department"]
        semesters = ["Select"] + self.FILTER_OPTIONS_MAPPING[self.var_degree.get()]["Semester"]
        self.dep_combo["values"] = departments
        self.sem_combo["values"] = semesters
    

    def load_divisions(self, event=None):
        if self.var_degree.get() == "Select":
            return
        if self.var_department.get() == "Select":
            return
    
        divisions = ["Select"] + self.FILTER_OPTIONS_MAPPING[self.var_degree.get()]["Division"][self.var_department.get()]
        self.division_combo["values"] = divisions
    

    def search_load_departments(self, event=None):
        if self.search_var_degree.get() == "Degree":
            return
        departments = ["Department"] + self.FILTER_OPTIONS_MAPPING[self.search_var_degree.get()]["Department"]
        semesters = ["Semester"] + self.FILTER_OPTIONS_MAPPING[self.search_var_degree.get()]["Semester"]
        self.search_dep_combo["values"] = departments
        self.search_sem_combo["values"] = semesters
    

    def search_load_divisions(self, event=None):
        if self.search_var_degree.get() == "Degree":
            return
        if self.search_var_department.get() == "Department":
            return
    
        divisions = ["Division"] + self.FILTER_OPTIONS_MAPPING[self.search_var_degree.get()]["Division"][self.search_var_department.get()]
        self.search_division_combo["values"] = divisions


    #create database connection*********************
    def create_connection(self):
        return mysql.connector.connect(
            host="localhost",
            username="root",
            password="Drishey@9845",
            database="face_recognizer"
        )

    #***********functions******************
    def add_data(self):
        if self.var_department.get()=="Select" or self.var_degree.get()=="Select" or self.var_semester.get()=="Select" or self.var_name.get()=="" or self.var_rollno.get()=="":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                my_cursor=self.conn.cursor()
                add_student = ("INSERT INTO student (Department, Degree, Semester, Division, Name, Roll_no, Captured_face) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s)")
                
                student_data=(self.var_department.get(),
                                self.var_degree.get(),
                                self.var_semester.get(),
                                self.var_division.get(),
                                self.var_name.get(),
                                self.var_rollno.get(),
                                self.var_captured_face.get())

                my_cursor.execute(add_student,student_data)
                self.conn.commit()
                self.fetch_data()
                my_cursor.close()
                self.var_captured_face.set("No")
                messagebox.showinfo("Success", "Student details has been added Successfully",parent=self.root)

            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)


    #******************fetch data*****************
    def fetch_data(self):
        my_cursor=self.conn.cursor()
        my_cursor.execute("Select * from student")
        data=my_cursor.fetchall()

        if len(data)!=0:
            self.student_table.delete(*self.student_table.get_children())
            for i in data:
                self.student_table.insert("",END,values=i)
            self.conn.commit()
                


    def apply_filter(self):
        my_cursor=self.conn.cursor()
        
        # Initialize an empty list to store conditions
        conditions = []

        # Check each filter variable and add conditions for filled ones
        if self.search_var_department.get() != "Department":
            conditions.append(f"Department = '{self.search_var_department.get()}'")

        if self.search_var_degree.get() != "Degree":
            conditions.append(f"Degree = '{self.search_var_degree.get()}'")

        if self.search_var_semester.get() != "Semester":
            conditions.append(f"Semester = '{self.search_var_semester.get()}'")

        if self.search_var_division.get() != "Division":
            conditions.append(f"Division = '{self.search_var_division.get()}'")

        if self.search_var_caputured.get() != "Captured":
            conditions.append(f"Captured_face = '{self.search_var_caputured.get()}'")

        # Construct the SQL query
        query = "SELECT * FROM student"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Execute the query
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        self.student_ids = [row[0] for row in result]

        if len(result)!=0:
            self.student_table.delete(*self.student_table.get_children())
            for i in result:
                self.student_table.insert("",END,values=i)
            self.conn.commit()

    

    #***********get cursor************
    def get_cursor(self,event=""):
        cursor_focus=self.student_table.focus()
        content=self.student_table.item(cursor_focus)
        data=content["values"]

        self.var_studentId.set(data[0]),
        self.var_department.set(data[1]),
        self.var_degree.set(data[2]),
        self.var_semester.set(data[3]),
        self.var_division.set(data[4]),
        self.var_name.set(data[5]),
        self.var_rollno.set(data[6]),
        self.var_captured_face.set(data[7]),

    #update function
    def update_data(self):
        if self.var_department.get()=="Select" or self.var_degree.get()=="Select" or self.var_semester.get()=="Select" or self.var_name.get()=="" or self.var_rollno.get()=="":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                Update=messagebox.askyesno("Update","Do you want to upadate",parent=self.root)
                if Update>0:
                    my_cursor=self.conn.cursor()
                    
                    my_cursor.execute("UPDATE student SET Department=%s,Degree=%s,Semester=%s,Division=%s,Name=%s,Roll_no=%s,Captured_face=%s WHERE studentId=%s",
                                      (self.var_department.get(),
                                        self.var_degree.get(),
                                        self.var_semester.get(),
                                        self.var_division.get(),
                                        self.var_name.get(),
                                        self.var_rollno.get(),
                                        self.var_captured_face.get(),
                                        self.var_studentId.get()))
                else:
                    if not Update:
                        return
                
                messagebox.showinfo("Success","Student details successfully updated",parent=self.root)
                self.conn.commit()
                self.fetch_data()
            
            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)


    def update_face(self):
        if self.var_department.get()=="Select" or self.var_degree.get()=="Select" or self.var_semester.get()=="Select" or self.var_name.get()=="" or self.var_rollno.get()=="":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                my_cursor=self.conn.cursor()    
                my_cursor.execute("UPDATE student SET Captured_face=%s WHERE studentId=%s",(self.var_captured_face.get(),self.var_studentId.get(),))
                messagebox.showinfo("Success","Student details successfully updated",parent=self.root)
                self.conn.commit()
                self.fetch_data()
            
            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)


    #delete function
    def delete_data(self):
        if self.var_studentId=="":
            messagebox.showerror("Error", "Student id must be required",parent=self.root)
        else:
            try:
                Delete=messagebox.askyesno("Delete","Do you want to delete",parent=self.root)
                if Delete>0:
                    my_cursor=self.conn.cursor()
                    query="DELETE FROM student WHERE studentId=%s"
                    val=(self.var_studentId.get(),)
                    my_cursor.execute(query,val)
                    self.var_captured_face.set("No")
                        
                else:
                    if not Delete:
                        return
                    
                messagebox.showinfo("Delete","Successfully deleted student details",parent=self.root)
                self.conn.commit()
                self.fetch_data()
                
            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)


    #reset function
    def reset_data(self):
        self.var_department.set("Select")
        self.var_degree.set("Select")
        self.var_semester.set("Select")
        self.var_division.set("Select")
        self.var_name.set("")
        self.var_rollno.set("")

    
    #get last student id
    def get_last_student_id(self):
        try:
            self.fetch_data() 
            my_cursor=self.conn.cursor()
            query = "SELECT studentId FROM student ORDER BY studentId DESC LIMIT 1"
            my_cursor.execute(query)
            result = my_cursor.fetchone()
            self.conn.commit()

            if result:
                return result[0]  # Assuming studentId is the first column in the result
            else:
                return None  # Student not found

        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    

    #**********************generate data set or take photo samples************

    def generate_dataset(self):
        if self.var_department.get() == "Select" or self.var_degree.get() == "Select" or self.var_semester.get() == "Select" or self.var_name.get() == "" or self.var_rollno.get() == "":
            messagebox.showerror("Error", "All Fields are required", parent=self.root)
        else:
            try:
                new_student = messagebox.askyesno("Confirmation", "Is the student a registered student?", parent=self.root)

                if new_student > 0:
                    student_id = self.var_studentId.get()
                    if self.var_captured_face.get()=="Yes":
                        messagebox.showwarning("Operation already done", "This operation has already been done.", parent=self.root)
                        return
                else:
                    if not new_student:
                        student_id = self.get_last_student_id() + 1
                
                
                # Create a new directory for each user inside /data
                user_folder = f"student/data/user_{student_id}"
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)
                
                cap = cv2.VideoCapture(0)

                # Create a window to display camera feed
                cv2.namedWindow("Camera Feed", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Camera Feed", 500, 400)  # Set the window size

                frame_width = int(cap.get(3))
                frame_height = int(cap.get(4))

                # Calculate the center of the frame
                center_x = frame_width // 2
                center_y = frame_height // 2

                # Size of the rectangle frame
                rect_width = 300  # Increase the width
                rect_height = 300

                capture_image = False
                img_id = 0

                def mouse_callback(event, x, y, flags, param):
                    nonlocal capture_image
                    if event == cv2.EVENT_LBUTTONDOWN:  # Check if the left mouse button is pressed
                        capture_image = True

                cv2.setMouseCallback("Camera Feed", mouse_callback)  # Set the mouse callback

                self.minimize_window()
                

                while True:
                    ret, my_frame = cap.read()

                    # Draw rectangle frame in the center
                    cv2.rectangle(my_frame, (center_x - rect_width // 2, center_y - rect_height // 2),
                                  (center_x + rect_width // 2, center_y + rect_height // 2), (0, 255, 0), 2)

                    # Crop the frame to the rectangle area
                    frame_cropped = my_frame[center_y - rect_height // 2:center_y + rect_height // 2,
                                    center_x - rect_width // 2:center_x + rect_width // 2]

                    # Convert to grayscale for face detection
                    current_frame = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2RGB)
                    faces = detector(current_frame, 0)


                    # Change frame color based on face detection
                    frame_color = (0, 0, 255)  # Default: Red (No Face)
                    # if len(faces) > 0:
                    #      

                    # If a face is detected, capture 10 images
                    if len(faces) > 0:
                        frame_color = (0, 255, 0) # Green (Face Detected)

                        if img_id < 5:
                            if capture_image:
                                img_id += 1
                                face_path = f"{user_folder}/user_{student_id}_{img_id}.jpg"
                                cv2.imwrite(face_path, frame_cropped)
                                capture_image=False
                            else:
                                if img_id==0:
                                    cv2.putText(my_frame, "Tap to start.", (20, 25), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 2)
                                else:
                                    display_text = f"Saved images: {img_id}."
                                    cv2.putText(my_frame, display_text, (20, 25), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 255, 0), 2)
                                
                        else:
                            break

                    # Draw the rectangle frame with the determined color
                    cv2.rectangle(my_frame, (center_x - rect_width // 2, center_y - rect_height // 2),
                                  (center_x + rect_width // 2, center_y + rect_height // 2), frame_color, 2)

                    # Display the frame
                    cv2.imshow("Camera Feed", my_frame)


                    # Break the loop if 'Esc' key is pressed
                    if cv2.waitKey(20) == 27:
                        break

                cap.release()
                cv2.destroyAllWindows()

                self.maximize_window()

                self.var_captured_face.set("Yes")
                if new_student > 0:
                    self.update_face()
                else:
                    if not new_student:
                        self.add_data()

            except Exception as es:
                messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def minimize_window(self):
        self.root.iconify()

    def maximize_window(self):
        self.root.deiconify()
    
    #**************************training dataset***********************************************
    def create_user_directory(self):

        if self.search_var_degree.get()=="Degree" or self.search_var_department.get()=="Department" or self.search_var_semester.get()=="Semester" or self.search_var_caputured.get()=="No":
            messagebox.showerror("Error", "Select students Degreee, Deaprtment, Semester, and captured face appropriately.",parent=self.root)
        else:
            user_directory = f"student/{self.search_var_degree.get()}/{self.search_var_department.get()}/{self.search_var_semester.get()}"
            try:
                # Create the directory if it doesn't exist
                if not os.path.exists(user_directory):
                    os.makedirs(user_directory)

                return user_directory
            
            except OSError as e:
                print(f"Error creating directory: {e}")
                return None
    
    def return_128d_features(self, path_img):
        # img=Image.open(image)
        # imageNp=np.array(img,'uint8')
        # print(path_img)
        img_rd = cv2.imread(path_img)
        gray = cv2.cvtColor(img_rd, cv2.COLOR_BGR2GRAY)

        faces = detector(gray, 1)

        logging.info("%-40s %-20s", " Image with faces detected:", path_img)

        # For photos of faces saved, we need to make sure that we can detect faces from the cropped images
        if len(faces) != 0:
            shape = predictor(img_rd, faces[0])
            face_descriptor = np.array(face_reco_model.compute_face_descriptor(img_rd, shape))
        else:
            face_descriptor = 0
            logging.warning("no face")
        return face_descriptor

    def train_classifier(self):

        Training=messagebox.askyesno("Training","Do you want to train selected data?",parent=self.root)
        if Training>0:
            paths = []
            faces=[]
            ids=[]

            if self.student_ids:
                user_directory = self.create_user_directory()
                feature_file = user_directory + "/features.csv"
                # df = pd.read_csv(feature_file)
                with open(feature_file,"w",newline="") as csvfile:
                    writer = csv.writer(csvfile)
                

                    for i in self.student_ids:
                        user_folder = f"student/data/user_{i}"
                        features_list_personX = []

                        # Check if the user folder exists
                        if os.path.exists(user_folder):
                            # Iterate over files in the user folder
                            for filename in os.listdir(user_folder):
                                features_128d = self.return_128d_features(user_folder+"/"+filename)
                                if features_128d != 0:
                                    features_list_personX.append(features_128d)
                                
                                img=Image.open(user_folder+"/"+filename)
                                imageNp=np.array(img,'uint8')
                                cv2.imshow("Training",imageNp)
                                cv2.waitKey(1)==27
                                
                                    
                        if features_list_personX:
                            features_mean_personX = np.array(features_list_personX, dtype=object).mean(axis=0)
                        else:
                            features_mean_personX = np.zeros(128, dtype=object, order='C')       

                        features_mean_personX = np.insert(features_mean_personX, 0, i, axis=0) 
                        writer.writerow(features_mean_personX)     
                        
                cv2.destroyAllWindows()
                messagebox.showinfo("Result","Training datasets completed!!!",parent=self.root)
                self.student_ids = []
            else:
                messagebox.showwarning("Warning","Selected students list is empty",parent=self.root)

        else:
            if not Training:
                return

    def face_recog(self):
        def draw_boundray(img,classifier,scaleFactor,minNeighbors,color,text,clf):
            gray_image=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            features=classifier.detectMultiScale(gray_image,scaleFactor,minNeighbors)

            coord=[]

            for(x,y,w,h) in features:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
                id,predict=clf.predict(gray_image[y:y+h,x:x+w])
                confidence=int((100*(1-predict/300)))

                my_cursor=self.conn.cursor()
                my_cursor.execute("SELECT Name,Roll_no,Semester,Department FROM student WHERE studentId="+str(id))
                result=my_cursor.fetchone()
                student_name=result[0]
                student_rollno=result[1]
                student_semester=result[2]
                student_department=result[3]
                

                if confidence>77:
                    cv2.putText(img,f"Name:{student_name}",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                    cv2.putText(img,f"Roll No:{student_rollno}",(x,y-30),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                    cv2.putText(img,f"Semester:{student_semester}",(x,y-55),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                    cv2.putText(img,f"Department:{student_department}",(x,y-80),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                else:
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),3)
                    cv2.putText(img,"Unknown Face",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),3)
                
                coord=[x,y,w,h]
            return coord
        
        def recognize(img,clf,faceCascade):
            coord=draw_boundray(img,faceCascade,1.1,10,(255,25,255),"Face",clf)
            return img
        
        faceCascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        clf=cv2.face.LBPHFaceRecognizer_create()
        clf.read("classifier.xml")

        video_cap=cv2.VideoCapture(0)

        while True:
            ret,img=video_cap.read()
            img=recognize(img,clf,faceCascade)
            cv2.imshow("Welcome to face recognition",img)

            if cv2.waitKey(1) == 27:
                break
        video_cap.release()
        cv2.destroyAllWindows()




                            
        
        









        

if __name__=="__main__":
    root=Tk()
    logging.basicConfig(level=logging.INFO)
    obj=Student(root)
    root.mainloop()