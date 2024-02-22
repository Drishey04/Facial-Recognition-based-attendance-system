from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
import tkinter.messagebox as messagebox
import mysql.connector
import cv2
import os
import numpy as np


class Subject:
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
        self.root.title("Subject Management System")

        # Establish MySQL connection
        self.conn = self.create_connection()

        #****************variables******************
        
        self.var_subname=StringVar()
        self.var_subject_code=StringVar()
        self.var_faculty_1_code=StringVar()
        self.var_faculty_2_code=StringVar()
        self.var_faculty_3_code=StringVar()
        self.var_degree=StringVar()
        self.var_department=StringVar()
        self.var_semester=StringVar()

        self.var_subjectId=StringVar()

  
        self.search_var_degree=StringVar()
        self.search_var_department=StringVar()
        self.search_var_semester=StringVar()
        

        self.subject_ids = []



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
        title.create_text(250, 20, text="Subject Management System", font=("times new roman", 30, "bold"), fill="darkgreen")



        # title_lbL=Label(bg_img,text="Subject Management System",font=("times new roman", 30, "bold"), bg="white",fg="darkgreen")
        # title_lbL.place(x=0,y=0,width=880,height=50)

        main_frame=Frame(bg_img,bd=2,relief=SUNKEN)
        main_frame.place(x=17,y=70,width=840,height=450)


        #top frame
        Top_frame=LabelFrame(main_frame,bd=2,relief=RIDGE,text="Information",font=("times new roman", 12, "bold"))
        Top_frame.place(x=10,y=5,width=815,height=135)

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
        sem_label.grid(row=2,column=1,padx=2,pady=5,sticky=W)

        self.sem_combo=ttk.Combobox(Top_frame,textvariable=self.var_semester,font=("times new roman", 12, "bold"),state="readonly",width=10)
        self.sem_combo["values"]=("Select")
        self.sem_combo.current(0)
        self.sem_combo.grid(row=2,column=2,padx=2,pady=5,sticky=W)


        #subject code
        subcode_label=Label(Top_frame,text="Subject Code:",font=("times new roman", 12, "bold"))
        subcode_label.grid(row=1,column=5,padx=2,pady=5,sticky=W)

        subcode_entry=ttk.Entry(Top_frame,textvariable=self.var_subject_code,width=12,font=("times new roman",12,"bold"))
        subcode_entry.grid(row=1,column=6,padx=5,pady=5,sticky=W)


        #faculty-1 code
        faccode_1_label=Label(Top_frame,text="Faculty-1 Code:",font=("times new roman", 12, "bold"))
        faccode_1_label.grid(row=0,column=3,padx=2,pady=5,sticky=W)

        faccode_entry=ttk.Entry(Top_frame,textvariable=self.var_faculty_1_code,width=12,font=("times new roman",12,"bold"))
        faccode_entry.grid(row=0,column=4,padx=5,pady=5,sticky=W)


        #faculty-2 code
        faccode_2_label=Label(Top_frame,text="Faculty-2 Code:",font=("times new roman", 12, "bold"))
        faccode_2_label.grid(row=1,column=3,padx=2,pady=5,sticky=W)

        faccode_2_entry=ttk.Entry(Top_frame,textvariable=self.var_faculty_2_code,width=12,font=("times new roman",12,"bold"))
        faccode_2_entry.grid(row=1,column=4,padx=5,pady=5,sticky=W)

        #faculty-3 code
        faccode_3_label=Label(Top_frame,text="Faculty-3 Code:",font=("times new roman", 12, "bold"))
        faccode_3_label.grid(row=2,column=3,padx=2,pady=5,sticky=W)

        faccode_3_entry=ttk.Entry(Top_frame,textvariable=self.var_faculty_3_code,width=12,font=("times new roman",12,"bold"))
        faccode_3_entry.grid(row=2,column=4,padx=5,pady=5,sticky=W)


        #name
        subname_label=Label(Top_frame,text="Subject Name:",font=("times new roman", 12, "bold"))
        subname_label.grid(row=0,column=5,padx=2,pady=5,sticky=W)

        subname_entry=ttk.Entry(Top_frame,textvariable=self.var_subname,width=31,font=("times new roman",12,"bold"))
        subname_entry.grid(row=0,column=6,padx=2,pady=5,sticky=W)

        #btn frame
        btn_frame=LabelFrame(Top_frame,bd=2,relief=FLAT,font=("times new roman", 12, "bold"))
        btn_frame.place(x=430,y=70,width=370,height=40)

        save_btn=Button(btn_frame,text="Save",command=self.add_data,width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="green",fg="white")
        save_btn.grid(row=0,column=3,padx=5,pady=0,sticky=W)

        Update_btn=Button(btn_frame,text="Update",command=self.update_data,width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="yellow3",fg="white")
        Update_btn.grid(row=0,column=4,padx=5,pady=0,sticky=W)

        delete_btn=Button(btn_frame,command=self.delete_data,text="Delete",width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="red",fg="white")
        delete_btn.grid(row=0,column=5,padx=5,pady=0,sticky=W)

        reset_btn=Button(btn_frame,text="Reset",command=self.reset_data,width=8,cursor="hand2",font=("times new roman", 12, "bold"),bg="grey",fg="white")
        reset_btn.grid(row=0,column=6,padx=5,pady=0,sticky=W)


        
        #bottom frame
        Bottom_frame=LabelFrame(main_frame,bd=2,relief=RIDGE,text="Subject Details",font=("times new roman", 12, "bold"))
        Bottom_frame.place(x=10,y=150,width=815,height=280)

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


        search_filter_btn=Button(Search_frame,text="Apply Filter",command=self.apply_filter,width=10,cursor="hand2",font=("times new roman", 12, "bold"),bg="cyan4",fg="white")
        search_filter_btn.grid(row=0,column=7,padx=5,pady=5,sticky=W)

        search_showall_btn=Button(Search_frame,text="Show All",command=self.fetch_data,width=10,cursor="hand2",font=("times new roman", 12, "bold"),bg="brown",fg="white")
        search_showall_btn.grid(row=0,column=8,padx=100,pady=5,sticky=W)


        #table frame
        table_frame=LabelFrame(Bottom_frame,bd=2,relief=GROOVE,font=("times new roman", 12, "bold"))
        table_frame.place(x=5,y=50,width=800,height=195)

        scroll_x=ttk.Scrollbar(table_frame,orient=HORIZONTAL)
        scroll_y=ttk.Scrollbar(table_frame,orient=VERTICAL)

        self.subject_table=ttk.Treeview(table_frame,columns=("Subject ID","Subject Code","Name","Degree","Department","Semester","Faculty-1","Faculty-2","Faculty-3"),xscrollcommand=scroll_x.set,yscrollcommand=scroll_y.set)

        scroll_x.pack(side=BOTTOM,fill=X)
        scroll_y.pack(side=RIGHT,fill=Y)

        scroll_x.config(command=self.subject_table.xview)
        scroll_y.config(command=self.subject_table.yview)

        self.subject_table.heading("Subject ID",text="Subject ID")
        self.subject_table.heading("Subject Code",text="Subject Code")
        self.subject_table.heading("Name",text="Name")
        self.subject_table.heading("Degree",text="Degree")
        self.subject_table.heading("Department",text="Department")
        self.subject_table.heading("Semester",text="Semester")
        self.subject_table.heading("Faculty-1",text="Faculty-1")
        self.subject_table.heading("Faculty-2",text="Faculty-2")
        self.subject_table.heading("Faculty-3",text="Faculty-3")
        self.subject_table["show"]="headings"

        self.subject_table.column("Subject ID",width=90)
        self.subject_table.column("Subject Code",width=90)
        self.subject_table.column("Name",width=240)
        self.subject_table.column("Degree",width=90)
        self.subject_table.column("Department",width=90)
        self.subject_table.column("Semester",width=90)
        self.subject_table.column("Faculty-1",width=90)
        self.subject_table.column("Faculty-2",width=90)
        self.subject_table.column("Faculty-3",width=90)
        

        self.subject_table.pack(fill=BOTH,expand=1)
        self.subject_table.bind("<ButtonRelease>",self.get_cursor)
        self.fetch_data()

        #buttons
        # operations_btn_frame=LabelFrame(Bottom_frame,bd=2,relief=FLAT,font=("times new roman", 12, "bold"))
        # operations_btn_frame.place(x=5,y=245,width=800,height=43)

        # train_data_btn=Button(operations_btn_frame,text="Train Data",width=15,command=self.train_classifier,cursor="hand2",font=("times new roman", 12, "bold"),bg="darkorange",fg="white")
        # train_data_btn.grid(row=0,column=1,padx=5,pady=0,sticky=W)

        # face_recog_btn=Button(operations_btn_frame,text="Facial Recognition",command=self.face_recog,width=15,cursor="hand2",font=("times new roman", 12, "bold"),bg="blue",fg="white")
        # face_recog_btn.grid(row=0,column=2,padx=5,pady=0,sticky=W)

        # new_semester_btn=Button(operations_btn_frame,text="New Semester",width=15,cursor="hand2",font=("times new roman", 12, "bold"),bg="green",fg="white")
        # new_semester_btn.grid(row=0,column=3,padx=335,pady=0,sticky=W)


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
        if self.var_department.get()=="Select"  or self.var_degree.get()=="Select" or self.var_semester.get()=="Select" or self.var_subname.get()=="" or self.var_subject_code.get()==""  or self.var_faculty_1_code.get()=="":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                my_cursor=self.conn.cursor()
                add_subject = ("INSERT INTO subject (Subject_code, Name, Degree, Department, Semester, Faculty_1_code, Faculty_2_code, Faculty_3_code) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
                
                subject_data=(self.var_subject_code.get(),
                                self.var_subname.get(),
                                self.var_degree.get(),
                                self.var_department.get(),
                                self.var_semester.get(),
                                self.var_faculty_1_code.get(),
                                self.var_faculty_2_code.get(),
                                self.var_faculty_3_code.get(),)

                my_cursor.execute(add_subject,subject_data)
                self.conn.commit()
                self.fetch_data()
                my_cursor.close()
                messagebox.showinfo("Success", "Subject details has been added Successfully",parent=self.root)

            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)


    #******************fetch data*****************
    def fetch_data(self):
        my_cursor=self.conn.cursor()
        my_cursor.execute("Select * from subject")
        data=my_cursor.fetchall()

        if len(data)!=0:
            self.subject_table.delete(*self.subject_table.get_children())
            for i in data:
                self.subject_table.insert("",END,values=i)
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

        # Construct the SQL query
        query = "SELECT * FROM subject"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Execute the query
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        # self.subject_ids = [row[0] for row in result]

        if len(result)!=0:
            self.subject_table.delete(*self.subject_table.get_children())
            for i in result:
                self.subject_table.insert("",END,values=i)
            self.conn.commit()

    

    #***********get cursor************
    def get_cursor(self,event=""):
        cursor_focus=self.subject_table.focus()
        content=self.subject_table.item(cursor_focus)
        data=content["values"]

        self.var_subjectId.set(data[0]),
        self.var_subject_code.set(data[1]),
        self.var_subname.set(data[2]),
        self.var_degree.set(data[3]),
        self.var_department.set(data[4]),
        self.var_semester.set(data[5]),
        self.var_faculty_1_code.set(data[6]),
        self.var_faculty_2_code.set(data[7]),
        self.var_faculty_3_code.set(data[8]),


    #update function
    def update_data(self):
        if self.var_department.get()=="Select"  or self.var_degree.get()=="Select" or self.var_semester.get()=="Select" or self.var_subname.get()=="" or self.var_subject_code.get()==""  or self.var_faculty_1_code.get()=="":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                Update=messagebox.askyesno("Update","Do you want to upadate",parent=self.root)
                if Update>0:
                    my_cursor=self.conn.cursor()

                    subject_data=(self.var_subject_code.get(),
                                self.var_subname.get(),
                                self.var_degree.get(),
                                self.var_department.get(),
                                self.var_semester.get(),
                                self.var_faculty_1_code.get(),
                                self.var_faculty_2_code.get(),
                                self.var_faculty_3_code.get(),
                                self.var_subjectId.get(),)
                    
                    my_cursor.execute("UPDATE subject SET Subject_code=%s,Name=%s,Degree=%s,Department=%s,Semester=%s,Faculty_1_code=%s, Faculty_2_code=%s, Faculty_3_code=%s  WHERE subjectId=%s",subject_data)
                else:
                    if not Update:
                        return
                
                messagebox.showinfo("Success","Subject details successfully updated",parent=self.root)
                self.conn.commit()
                self.fetch_data()
            
            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)


    #delete function
    def delete_data(self):
        if self.var_subjectId=="":
            messagebox.showerror("Error", "Subject id must be required",parent=self.root)
        else:
            try:
                Delete=messagebox.askyesno("Delete","Do you want to delete",parent=self.root)
                if Delete>0:
                    my_cursor=self.conn.cursor()
                    query="DELETE FROM subject WHERE subjectId=%s"
                    val=(self.var_subjectId.get(),)
                    my_cursor.execute(query,val)
                        
                else:
                    if not Delete:
                        return
                    
                messagebox.showinfo("Delete","Successfully deleted subject details",parent=self.root)
                self.conn.commit()
                self.fetch_data()
                
            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)


    #reset function
    def reset_data(self):
        self.var_subject_code.set(""),
        self.var_subname.set(""),
        self.var_degree.set("Select"),
        self.var_department.set("Select"),
        self.var_semester.set("Select"),
        self.var_faculty_1_code.set(""),
        self.var_faculty_2_code.set(""),


                            
        
        
        

if __name__=="__main__":
    root=Tk()
    obj=Subject(root)
    root.mainloop()