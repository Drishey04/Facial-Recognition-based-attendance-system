from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
import tkinter.messagebox as messagebox
import mysql.connector
import cv2
import os
import numpy as np
import csv
import logging
import dlib
import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC


# Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()
#  Get face landmarks
predictor = dlib.shape_predictor('data_dlib/shape_predictor_68_face_landmarks.dat')

#  Use Dlib resnet50 model to get 128D face descriptor
face_reco_model = dlib.face_recognition_model_v1("data_dlib/dlib_face_recognition_resnet_model_v1.dat")




class Faculty:
    def __init__(self,root):
        self.root=root
        self.root.geometry("880x590")
        self.root.title("Faculty Management System")

        # Establish MySQL connection
        self.conn = self.create_connection()

        #****************variables******************
        
        self.var_name=StringVar()
        self.var_faculty_code=StringVar()
        self.var_department=StringVar()
        self.var_captured_face=StringVar()
        self.var_facultyId=StringVar()

        self.var_captured_face.set("No")
  
        self.search_var_department=StringVar()
        self.search_var_caputured=StringVar()

        self.faculty_ids = []

        self.font = cv2.FONT_ITALIC

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

        self.no_face=False



        #landing page image and title
        img=Image.open(r"D:\SVNIT\SEMSTER-8\Project\Project_1\Photos\background_page.jpg")
        img=img.resize((880,590))
        self.landingbgd=ImageTk.PhotoImage(img)

        bg_img=Label(self.root,image=self.landingbgd)
        bg_img.place(x=0,y=0,width=880,height=590)

        title = Canvas(bg_img,width=500, height=45)
        title.place(x=200,y=10)
        
        sp_img=Image.open(r"D:\SVNIT\SEMSTER-8\Project\Project_1\Photos\background_page_title.png")
        sp_img=sp_img.resize((510,50))
        self.sp_title=ImageTk.PhotoImage(sp_img)

        title.create_image(0, 0, anchor="nw", image=self.sp_title)
        title.create_text(250, 20, text="Faculty Management System", font=("times new roman", 30, "bold"), fill="darkgreen")



        # title_lbL=Label(bg_img,text="Faulty Management System",font=("times new roman", 30, "bold"), bg="white",fg="darkgreen")
        # title_lbL.place(x=0,y=0,width=880,height=50)

        main_frame=Frame(bg_img,bd=2,relief=SUNKEN)
        main_frame.place(x=17,y=70,width=840,height=430)


        #top frame
        Top_frame=LabelFrame(main_frame,bd=2,relief=RIDGE,text="Information",font=("times new roman", 12, "bold"))
        Top_frame.place(x=10,y=5,width=815,height=105)


        #name
        name_label=Label(Top_frame,text="Faulty Name:",font=("times new roman", 12, "bold"))
        name_label.grid(row=0,column=1,padx=2,pady=5,sticky=W)

        name_entry=ttk.Entry(Top_frame,textvariable=self.var_name,width=30,font=("times new roman",12,"bold"))
        name_entry.grid(row=0,column=2,padx=2,pady=5,sticky=W)

        

        #department
        dep_label=Label(Top_frame,text="Department:",font=("times new roman", 12, "bold"))
        dep_label.grid(row=0,column=3,padx=2,pady=5,sticky=W)

        dep_combo=ttk.Combobox(Top_frame,textvariable=self.var_department,font=("times new roman", 12, "bold"),state="readonly",width=7)
        dep_combo["values"]=("Select","CSE","ECE","EE","ME","CE","CHE")
        dep_combo.current(0)
        dep_combo.grid(row=0,column=4,padx=2,pady=5,sticky=W)


        #faculty code
        faccode_label=Label(Top_frame,text="Faculty Code:",font=("times new roman", 12, "bold"))
        faccode_label.grid(row=0,column=5,padx=2,pady=5,sticky=W)

        faccode_entry=ttk.Entry(Top_frame,textvariable=self.var_faculty_code,width=20,font=("times new roman",12,"bold"))
        faccode_entry.grid(row=0,column=6,padx=5,pady=5,sticky=W)




        # #photo
        # photo_frame=LabelFrame(Top_frame,bd=2,relief=RIDGE,text="Faculty Photo",font=("times new roman", 12, "bold"))
        # photo_frame.place(x=620,y=0,width=170,height=125)

        # img=Image.open(r"Photos\student_example.png")
        # img=img.resize((150,80))
        # self.landingbgd=ImageTk.PhotoImage(img)

        # bg_img=Label(photo_frame,image=self.landingbgd)
        # bg_img.place(x=5,y=0,width=150,height=100)


        btn_frame=LabelFrame(Top_frame,bd=2,relief=FLAT,font=("times new roman", 12, "bold"))
        btn_frame.place(x=5,y=40,width=120,height=40)

        btn_1_frame=LabelFrame(Top_frame,bd=2,relief=FLAT,font=("times new roman", 12, "bold"))
        btn_1_frame.place(x=430,y=40,width=370,height=40)


        take_btn=Button(btn_frame,text="Capture Face",command=self.generate_dataset,width=11,cursor="hand2",font=("times new roman", 12, "bold"),bg="magenta3",fg="white")
        take_btn.grid(row=0,column=1,padx=5,pady=0,sticky=W)

        save_btn=Button(btn_1_frame,text="Save",command=self.add_data,width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="green",fg="white")
        save_btn.grid(row=0,column=3,padx=5,pady=0,sticky=W)

        Update_btn=Button(btn_1_frame,text="Update",command=self.update_data,width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="yellow3",fg="white")
        Update_btn.grid(row=0,column=4,padx=5,pady=0,sticky=W)

        delete_btn=Button(btn_1_frame,command=self.delete_data,text="Delete",width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="red",fg="white")
        delete_btn.grid(row=0,column=5,padx=5,pady=0,sticky=W)

        reset_btn=Button(btn_1_frame,text="Reset",command=self.reset_data,width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="grey",fg="white")
        reset_btn.grid(row=0,column=6,padx=5,pady=0,sticky=W)


        
        #bottom frame
        Bottom_frame=LabelFrame(main_frame,bd=2,relief=RIDGE,text="Faculty Details",font=("times new roman", 12, "bold"))
        Bottom_frame.place(x=10,y=110,width=815,height=310)

        #search frame
        Search_frame=LabelFrame(Bottom_frame,bd=2,relief=GROOVE,font=("times new roman", 12, "bold"),bg="lightgrey")
        Search_frame.place(x=5,y=5,width=800,height=47)

        search_label=Label(Search_frame,text="Filter:",font=("times new roman", 12, "bold"),bg="red",fg="white")
        search_label.grid(row=0,column=1,padx=5,pady=5,sticky=W)


        search_dep_combo=ttk.Combobox(Search_frame,textvariable=self.search_var_department,font=("times new roman", 12, "bold"),state="readonly",width=10)
        search_dep_combo["values"]=("Department","CSE","ECE","EE","ME","CE","CHE")
        search_dep_combo.current(0)
        search_dep_combo.grid(row=0,column=3,padx=2,pady=5,sticky=W)


        search_capture_face_combo=ttk.Combobox(Search_frame,textvariable=self.search_var_caputured,font=("times new roman", 12, "bold"),state="readonly",width=10)
        search_capture_face_combo["values"]=("Captured","Yes","No")
        search_capture_face_combo.current(0)
        search_capture_face_combo.grid(row=0,column=6,padx=2,pady=5,sticky=W)

        search_filter_btn=Button(Search_frame,text="Apply Filter",command=self.apply_filter,width=10,cursor="hand2",font=("times new roman", 12, "bold"),bg="cyan4",fg="white")
        search_filter_btn.grid(row=0,column=7,padx=5,pady=5,sticky=W)

        search_showall_btn=Button(Search_frame,text="Show All",command=self.fetch_data,width=10,cursor="hand2",font=("times new roman", 12, "bold"),bg="brown",fg="white")
        search_showall_btn.grid(row=0,column=8,padx=310,pady=5,sticky=W)


        #table frame
        table_frame=LabelFrame(Bottom_frame,bd=2,relief=GROOVE,font=("times new roman", 12, "bold"))
        table_frame.place(x=5,y=50,width=800,height=195)

        # scroll_x=ttk.Scrollbar(table_frame,orient=HORIZONTAL)
        scroll_y=ttk.Scrollbar(table_frame,orient=VERTICAL)

        self.faculty_table=ttk.Treeview(table_frame,columns=("Faculty ID","Faculty Code","Name","Department","Captured Face"),yscrollcommand=scroll_y.set)

        # scroll_x.pack(side=BOTTOM,fill=X)
        scroll_y.pack(side=RIGHT,fill=Y)

        # scroll_x.config(command=self.faculty_table.xview)
        scroll_y.config(command=self.faculty_table.yview)

        self.faculty_table.heading("Faculty ID",text="Faculty ID")
        self.faculty_table.heading("Faculty Code",text="Faculty Code")
        self.faculty_table.heading("Name",text="Name")
        self.faculty_table.heading("Department",text="Department")
        self.faculty_table.heading("Captured Face",text="Captured Face")
        self.faculty_table["show"]="headings"

        self.faculty_table.column("Faculty ID",width=80)
        self.faculty_table.column("Faculty Code",width=80)
        self.faculty_table.column("Name",width=150)
        self.faculty_table.column("Department",width=80)
        self.faculty_table.column("Captured Face",width=80)
        

        self.faculty_table.pack(fill=BOTH,expand=1)
        self.faculty_table.bind("<ButtonRelease>",self.get_cursor)
        self.fetch_data()

        #buttons
        operations_btn_frame=LabelFrame(Bottom_frame,bd=2,relief=FLAT,font=("times new roman", 12, "bold"))
        operations_btn_frame.place(x=5,y=245,width=800,height=43)

        train_data_btn=Button(operations_btn_frame,text="Train Data",width=15,command=self.train_classifier,cursor="hand2",font=("times new roman", 12, "bold"),bg="darkorange",fg="white")
        train_data_btn.grid(row=0,column=1,padx=5,pady=0,sticky=W)

        face_recog_btn=Button(operations_btn_frame,text="Facial Recognition",command=self.face_recog,width=15,cursor="hand2",font=("times new roman", 12, "bold"),bg="blue",fg="white")
        face_recog_btn.grid(row=0,column=2,padx=5,pady=0,sticky=W)
        

        

        # new_semester_btn=Button(operations_btn_frame,text="New Semester",width=15,cursor="hand2",font=("times new roman", 12, "bold"),bg="green",fg="white")
        # new_semester_btn.grid(row=0,column=3,padx=335,pady=0,sticky=W)



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
        if self.var_department.get()=="Select"  or self.var_name.get()=="" or self.var_faculty_code.get()=="":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                my_cursor=self.conn.cursor()
                add_faculty = ("INSERT INTO faculty (Faculty_code, Name, Department, Captured_face) "
                                "VALUES (%s, %s, %s, %s)")
                
                faculty_data=(self.var_faculty_code.get(),
                                self.var_name.get(),
                                self.var_department.get(),
                                self.var_captured_face.get())

                my_cursor.execute(add_faculty,faculty_data)
                self.conn.commit()
                self.fetch_data()
                my_cursor.close()
                messagebox.showinfo("Success", "Faculty details has been added Successfully",parent=self.root)

            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)


    #******************fetch data*****************
    def fetch_data(self):
        my_cursor=self.conn.cursor()
        my_cursor.execute("Select * from faculty")
        data=my_cursor.fetchall()
        self.faculty_ids = [row[0] for row in data]

        if len(data)!=0:
            self.faculty_table.delete(*self.faculty_table.get_children())
            for i in data:
                self.faculty_table.insert("",END,values=i)
            self.conn.commit()
                

    def apply_filter(self):
        my_cursor=self.conn.cursor()
        
        # Initialize an empty list to store conditions
        conditions = []

        # Check each filter variable and add conditions for filled ones
        if self.search_var_department.get() != "Department":
            conditions.append(f"Department = '{self.search_var_department.get()}'")

        if self.search_var_caputured.get() != "Captured":
            conditions.append(f"Captured_face = '{self.search_var_caputured.get()}'")

        # Construct the SQL query
        query = "SELECT * FROM faculty"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Execute the query
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        self.faculty_ids = [row[0] for row in result]

        if len(result)!=0:
            self.faculty_table.delete(*self.faculty_table.get_children())
            for i in result:
                self.faculty_table.insert("",END,values=i)
            self.conn.commit()


    #***********get cursor************
    def get_cursor(self,event=""):
        cursor_focus=self.faculty_table.focus()
        content=self.faculty_table.item(cursor_focus)
        data=content["values"]

        self.var_facultyId.set(data[0]),
        self.var_faculty_code.set(data[1]),
        self.var_name.set(data[2]),
        self.var_department.set(data[3]),
        self.var_captured_face.set(data[4])

    #update function
    def update_data(self):
        if self.var_department.get()=="Select"  or self.var_name.get()=="" or self.var_faculty_code.get()=="":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                Update=messagebox.askyesno("Update","Do you want to upadate",parent=self.root)
                if Update>0:
                    my_cursor=self.conn.cursor()
                    
                    my_cursor.execute("UPDATE faculty SET Faculty_code=%s,Name=%s,Department=%s,Captured_face=%s WHERE facultyId=%s",
                                      (self.var_faculty_code.get(),
                                        self.var_name.get(),
                                        self.var_department.get(),
                                        self.var_captured_face.get(),
                                        self.var_facultyId.get(),))
                else:
                    if not Update:
                        return
                
                messagebox.showinfo("Success","Faculty details successfully updated",parent=self.root)
                self.conn.commit()
                self.fetch_data()
            
            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)

    #update captured face only
    def update_face(self):
        if self.var_department.get()=="Select"  or self.var_name.get()=="" or self.var_faculty_code.get()=="":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                my_cursor=self.conn.cursor()    
                my_cursor.execute("UPDATE faculty SET Captured_face=%s WHERE facultyId=%s",(self.var_captured_face.get(),self.var_facultyId.get(),))
                messagebox.showinfo("Success","Student details successfully updated",parent=self.root)
                self.conn.commit()
                self.fetch_data()
            
            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)

    #delete function
    def delete_data(self):
        if self.var_facultyId=="":
            messagebox.showerror("Error", "Faculty id must be required",parent=self.root)
        else:
            try:
                Delete=messagebox.askyesno("Delete","Do you want to delete",parent=self.root)
                if Delete>0:
                    my_cursor=self.conn.cursor()
                    query="DELETE FROM faculty WHERE facultyId=%s"
                    val=(self.var_facultyId.get(),)
                    my_cursor.execute(query,val)
                        
                else:
                    if not Delete:
                        return
                    
                messagebox.showinfo("Delete","Successfully deleted faculty details",parent=self.root)
                self.conn.commit()
                self.fetch_data()
                
            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)

    #reset function
    def reset_data(self):
        self.var_department.set("Select")
        self.var_name.set("")
        self.var_faculty_code.set("")

    
    #get last faculty id
    def get_last_faculty_id(self):
        try:
            self.fetch_data() 
            my_cursor=self.conn.cursor()
            query = "SELECT facultyId FROM faculty ORDER BY facultyId DESC LIMIT 1"
            my_cursor.execute(query)
            result = my_cursor.fetchone()
            self.conn.commit()

            if result:
                return result[0]  # Assuming facultyId is the first column in the result
            else:
                return None  # faculty not found

        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def get_details(self,id):
        try:
            my_cursor=self.conn.cursor()
            # print(id)
            query = "SELECT Name FROM faculty WHERE facultyId=%s"
            my_cursor.execute(query,(str(id),))
            result = my_cursor.fetchone()
            self.conn.commit()

            if result:
                # print(result[0])
                return result[0]  # Assuming facultyId is the first column in the result
            else:
                return None  # faculty not found
        
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)



    #**********************generate data set or take photo samples************
    def generate_dataset(self):
        if self.var_department.get()=="Select"  or self.var_name.get()=="" or self.var_faculty_code.get()=="":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                new_faculty = messagebox.askyesno("Confirmation", "Is this a registered faculty?", parent=self.root)

                if new_faculty > 0:
                    faculty_id = self.var_facultyId.get()
                    if self.var_captured_face.get()=="Yes":
                        messagebox.showwarning("Operation already done", "This operation has already been done.", parent=self.root)
                        return
                else:
                    if not new_faculty:
                        faculty_id = self.get_last_faculty_id() + 1

                
                # Create a new directory for each user inside /data
                user_folder = f"faculty/data/user_{faculty_id}"
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

                    # If a face is detected, capture 10 images
                    if len(faces) > 0:
                        frame_color = (0, 255, 0) # Green (Face Detected)

                        if img_id < 5:
                            if capture_image:
                                img_id += 1
                                face_path = f"{user_folder}/user_{faculty_id}_{img_id}.jpg"
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
                if new_faculty > 0:
                    self.update_face()
                else:
                    if not new_faculty:
                        self.add_data()

            except Exception as es:
                messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def minimize_window(self):
        self.root.iconify()

    def maximize_window(self):
        self.root.deiconify()
    
    #**************************training dataset***********************************************
    def face_encodings(self, img):
        faces = detector(img, 1)

        # For photos of faces saved, we need to make sure that we can detect faces from the cropped images
        if len(faces) != 0:
            shape = predictor(img, faces[0])
            face_descriptor = np.array(face_reco_model.compute_face_descriptor(img, shape))
        else:
            face_descriptor = 0
            self.no_face = True
            logging.warning("no face")
        return face_descriptor
    


    def train_classifier(self):

        Training=messagebox.askyesno("Training","Do you want to train selected data?",parent=self.root)
        if Training>0:
            if self.faculty_ids:
                # user_directory = self.create_user_directory()
                id_encondings_dict = {} 
                labels=[]
                features=[]

                for id in self.faculty_ids:
                    user_folder = f"faculty/data/user_{id}"
                    features_list_personX = []

                    # Check if the user folder exists
                    if os.path.exists(user_folder):
                        # Iterate over files in the user folder
                        for filename in os.listdir(user_folder):
                            logging.info("%-40s %-20s", " Image with faces detected:", user_folder+"/"+filename)
                            img_rd = cv2.imread(user_folder+"/"+filename)
                            encodings = self.face_encodings(img_rd)
                            
                            if self.no_face:
                                self.no_face=False
                                print("No face descrpitors were obtained")
                            else:
                                features_list_personX.append(encodings)
                            
                            img=Image.open(user_folder+"/"+filename)
                            imageNp=np.array(img,'uint8')
                            cv2.imshow("Training",imageNp)
                            cv2.waitKey(1)==27
                                
                        
                    if features_list_personX:
                        features_mean_personX = np.array(features_list_personX, dtype=object).mean(axis=0)
                    else:
                        features_mean_personX = np.zeros(128, dtype=object, order='C')       
                        
                    e = id_encondings_dict.get(id, [])
                    e.extend(features_mean_personX)
                    id_encondings_dict[id] = e
                    labels.append(id)
                    features.append(features_mean_personX)
                
                # features = np.nan_to_num(features)  # Convert NaNs to zeros
                # labels = np.array(labels)
                print(labels)
                # classifier = KNeighborsClassifier(n_neighbors=2)
                # classifier.fit(features, labels)
                with open("faculty/encodings.pkl", "wb") as f:
                    pickle.dump(id_encondings_dict, f) 
                             
                with open("faculty/classifier.pkl", "wb") as f:
                    # print(id_encondings_dict)
                    classifier = SVC(kernel='linear', probability=True)  # You can try different kernels and parameters
                    classifier.fit(features, labels)
                    pickle.dump(classifier, f)   

                cv2.destroyAllWindows()
                messagebox.showinfo("Result","Training datasets completed!!!",parent=self.root)
                self.faculty_ids = []
            else:
                messagebox.showwarning("Warning","Selected students list is empty",parent=self.root)

        else:
            if not Training:
                return
            
    
    #***********************Recognition********************************************************
            
    def return_euclidean_distance(self,feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        return dist
    
    def get_face_database(self):
        if os.path.exists("faculty/classifier.pkl") and os.path.exists("faculty/encodings.pkl"):
            with open("faculty/encodings.pkl", "rb") as f:
                self.encodings = pickle.load(f)
            with open("faculty/classifier.pkl", "rb") as f:
                self.classifier = pickle.load(f)

            return 1
        else:
            logging.warning("encodings.pkl or classifier.pkl not found!")
            return 0

    def face_recog(self):   
        video_cap = cv2.VideoCapture(0)

        # 1.  Get faces known from "encodings.pickle"
        if self.get_face_database():
            while video_cap.isOpened():
                ret, img_rd = video_cap.read()

                # 2.  Detect faces for frame X
                faces = detector(img_rd, 1)

                # 3.  Update cnt for faces in frames
                self.last_frame_face_cnt = self.current_frame_face_cnt
                self.current_frame_face_cnt = len(faces)


                for face in faces:
                    # Get the coordinates of the bounding box
                    left, top, right, bottom = face.left(), face.top(), face.right(), face.bottom()

                    if (self.current_frame_face_cnt == self.last_frame_face_cnt):
                        logging.debug("No face cnt changes in this frame")
                        print("not")

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
                        if min_distance < 0.4:
                            label_text = str(predicted_label)
                        else:
                            label_text = "Unknown"

                        print(label_text)

                    # Draw the face boundary
                    cv2.rectangle(img_rd, (left, top), (right, bottom), (255, 255, 255), 2)

                    # Display the predicted label
                    cv2.putText(img_rd, label_text, (left, bottom + 20), self.font, 0.8, (0, 255, 255), 1, cv2.LINE_AA)

                # Display the frame
                cv2.imshow("Welcome to face recognition", img_rd)

                if cv2.waitKey(1) == 27:
                    break

            video_cap.release()
            cv2.destroyAllWindows()

        

if __name__=="__main__":
    root=Tk()
    obj=Faculty(root)
    root.mainloop()
