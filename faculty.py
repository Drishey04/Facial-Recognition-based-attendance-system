from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
import tkinter.messagebox as messagebox
import mysql.connector
import cv2
import os
import numpy as np


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
                
                self.var_captured_face.set("Yes")

                # Create a new directory for each user inside /data
                user_folder = f"faculty/data/user_{faculty_id}"
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)
                
                face_classifier=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
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

                img_id = 0
                while True:
                    ret, my_frame = cap.read()

                    # Draw rectangle frame in the center
                    cv2.rectangle(my_frame, (center_x - rect_width // 2, center_y - rect_height // 2),
                                  (center_x + rect_width // 2, center_y + rect_height // 2), (0, 255, 0), 2)

                    # Crop the frame to the rectangle area
                    frame_cropped = my_frame[center_y - rect_height // 2:center_y + rect_height // 2,
                                    center_x - rect_width // 2:center_x + rect_width // 2]

                    # Convert to grayscale for face detection
                    gray_frame = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2GRAY)

                    # Detect faces in the cropped frame
                    faces = face_classifier.detectMultiScale(gray_frame, 1.3, 5)

                    # Change frame color based on face detection
                    frame_color = (0, 0, 255)  # Default: Red (No Face)
                    if len(faces) > 0:
                        frame_color = (0, 255, 0)  # Green (Face Detected)

                    # If a face is detected, capture 50 images
                    if len(faces) > 0:
                        img_id += 1
                        for(x,y,w,h) in faces:
                            face_cropped=frame_cropped[y:y+h,x:x+w]
                            face_cropped_gray=cv2.cvtColor(face_cropped,cv2.COLOR_BGR2GRAY)
                        
                        if img_id <= 100:
                            face_path = f"{user_folder}/user_{faculty_id}_{img_id}.jpg"
                            cv2.imwrite(face_path, face_cropped_gray)
                             # Display the captured face
                            cv2.putText(frame_cropped, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2,
                                        (0, 255, 0), 2)
                            # cv2.imshow("Cropped Face", frame_cropped)
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
                messagebox.showinfo("Result", "Generating data sets completed.", parent=self.root)

            except Exception as es:
                messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)


    
    #**************************training dataset***********************************************
    # def create_user_directory(self):

    #     if self.search_var_department.get()=="Department" or self.search_var_caputured.get()=="No":
    #         messagebox.showerror("Error", "Select students Deaprtment, and captured face appropriately.",parent=self.root)
    #     else:
    #         user_directory = f"faculty/{self.search_var_department.get()}"

    #         try:
    #             # Create the directory if it doesn't exist
    #             os.makedirs(user_directory)
    #             return user_directory
    #         except OSError as e:
    #             print(f"Error creating directory: {e}")
    #             return None
            

    def train_classifier(self):

        Training=messagebox.askyesno("Train","Do you want to train selected data?",parent=self.root)
        if Training>0:
            paths = []
            faces=[]
            ids=[]

            if self.faculty_ids:
                for i in self.faculty_ids:
                    user_folder = f"faculty/data/user_{i}"

                    # Check if the user folder exists
                    if os.path.exists(user_folder):
                        # Iterate over files in the user folder
                        for filename in os.listdir(user_folder):
                            if filename.endswith(".jpg"):
                                # Build the full path to each image
                                ids.append(i)
                                image_path = os.path.join(user_folder, filename)
                                paths.append(image_path)
            
            

            for image in paths:
                img=Image.open(image).convert('L') #gray scale image
                imageNp=np.array(img,'uint8')
                faces.append(imageNp)
                cv2.imshow("Training",imageNp)
                cv2.waitKey(1)==27
            
            ids=np.array(ids)


            #****************train classifier**************
            clf=cv2.face.LBPHFaceRecognizer_create()
            
            clf.train(faces,ids)
            clf.write("faculty/"+"faculty_classifier.xml")
            cv2.destroyAllWindows()
            messagebox.showinfo("Result","Training datasets completed!!!",parent=self.root)

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
                my_cursor.execute("SELECT Faculty_code,Name,Department FROM faculty WHERE facultyId="+str(id))
                result=my_cursor.fetchone()
                faculty_code=result[0]
                faculty_name=result[1]
                faculty_department=result[2]
                

                if confidence>77:
                    cv2.putText(img,f"Faculty Code:{faculty_code}",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                    cv2.putText(img,f"Name:{faculty_name}",(x,y-30),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                    cv2.putText(img,f"Department:{faculty_department}",(x,y-55),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
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
        clf.read("faculty/"+"faculty_classifier.xml")

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
    obj=Faculty(root)
    root.mainloop()