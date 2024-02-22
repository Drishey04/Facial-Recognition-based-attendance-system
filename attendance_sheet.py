from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
import tkinter.messagebox as messagebox
import mysql.connector
import cv2
import os
import numpy as np
import pandas as pd
from tkinter import filedialog



class Attendance_sheet:
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
        self.root.title("Attendance Management System")

        # Establish MySQL connection
        self.conn = self.create_connection()

        self.var_degree=StringVar()
        self.var_department=StringVar()
        self.var_semester=StringVar()
        self.var_division=StringVar()
        self.var_sub_code=StringVar()

        self.export_filename={}


        #landing page image and title
        img=Image.open(r"D:\SVNIT\SEMSTER-8\Project\Project_1\Photos\background_page.jpg")
        img=img.resize((880,590))
        self.landingbgd=ImageTk.PhotoImage(img)

        self.bg_img=Label(self.root,image=self.landingbgd)
        self.bg_img.place(x=0,y=0,width=880,height=590)


        title = Canvas(self.bg_img,width=555, height=45)
        title.place(x=160,y=10)
        
        sp_img=Image.open(r"D:\SVNIT\SEMSTER-8\Project\Project_1\Photos\background_page_title.png")
        sp_img=sp_img.resize((560,50))
        self.sp_title=ImageTk.PhotoImage(sp_img)

        title.create_image(0, 0, anchor="nw", image=self.sp_title)
        title.create_text(280, 20, text="Attendance Mangement System", font=("times new roman", 30, "bold"), fill="darkgreen")


        main_frame=Frame(self.bg_img,bd=2,relief=SUNKEN)
        main_frame.place(x=17,y=70,width=840,height=500)


        #degree
        degree_label=Label(main_frame,text="Degree:",font=("times new roman", 12, "bold"))
        degree_label.grid(row=0,column=1,padx=2,pady=5,sticky=W)

        self.degree_combo=ttk.Combobox(main_frame,textvariable=self.var_degree,font=("times new roman", 12, "bold"),state="readonly",width=7)
        self.degree_combo["values"]=("Select","B.Tech","M.Tech")
        self.degree_combo.current(0)
        self.degree_combo.grid(row=0,column=2,padx=2,pady=5,sticky=W)
        self.degree_combo.bind("<<ComboboxSelected>>", self.load_departments)

        #department
        dep_label=Label(main_frame,text="Department:",font=("times new roman", 12, "bold"))
        dep_label.grid(row=0,column=3,padx=3,pady=5,sticky=W)

        self.dep_combo=ttk.Combobox(main_frame,textvariable=self.var_department,font=("times new roman", 12, "bold"),state="readonly",width=10)
        self.dep_combo["values"]=("Select")
        self.dep_combo.current(0)
        self.dep_combo.grid(row=0,column=4,padx=2,pady=5,sticky=W)

        #semester
        sem_label=Label(main_frame,text="Semester:",font=("times new roman", 12, "bold"))
        sem_label.grid(row=0,column=5,padx=2,pady=5,sticky=W)

        self.sem_combo=ttk.Combobox(main_frame,textvariable=self.var_semester,font=("times new roman", 12, "bold"),state="readonly",width=10)
        self.sem_combo["values"]=("Select")
        self.sem_combo.current(0)
        self.sem_combo.grid(row=0,column=6,padx=2,pady=5,sticky=W)


        show_btn=Button(main_frame,text="Show Attendance",command=self.show_attendance,cursor="hand2",font=("times new roman", 12, "bold"),bg="blue",fg="white")
        show_btn.grid(row=0,column=9,padx=5,pady=5,sticky=W)

        reset_btn=Button(main_frame,text="Reset",command=self.reset_data,width=10,cursor="hand2",font=("times new roman", 12, "bold"),bg="grey",fg="white")
        reset_btn.grid(row=0,column=10,padx=51,pady=8,sticky=W)



        #search frame
        Search_frame=LabelFrame(main_frame,bd=2,relief=GROOVE,font=("times new roman", 12, "bold"),bg="lightgrey")
        Search_frame.place(x=5,y=50,width=830,height=47)

        search_label=Label(Search_frame,text="Filter:",font=("times new roman", 12, "bold"),bg="red",fg="white")
        search_label.grid(row=0,column=1,padx=5,pady=5,sticky=W)


        self.division_combo=ttk.Combobox(Search_frame,textvariable=self.var_division,font=("times new roman", 12, "bold"),state="readonly",width=10)
        self.division_combo["values"]=("Division")
        self.division_combo.current(0)
        self.division_combo.grid(row=0,column=2,padx=2,pady=5,sticky=W)

        #search
        self.search_sub_code_combo=ttk.Combobox(Search_frame,textvariable=self.var_sub_code,font=("times new roman", 12, "bold"),state="readonly",width=15)
        self.search_sub_code_combo["values"]=("Subject_Code")
        self.search_sub_code_combo.current(0)
        self.search_sub_code_combo.grid(row=0,column=3,padx=2,pady=5,sticky=W)
        

        filter_btn=Button(Search_frame,text="Apply Filter",command=self.apply_filter,width=10,cursor="hand2",font=("times new roman", 12, "bold"),bg="cyan4",fg="white")
        filter_btn.grid(row=0,column=5,padx=5,pady=5,sticky=W)

        export_btn=Button(Search_frame,text="Export CSV",command=self.export_table_to_csv_pandas,width=10,cursor="hand2",font=("times new roman", 12, "bold"),bg="Green",fg="white")
        export_btn.grid(row=0,column=7,padx=300,pady=5,sticky=W)

        #table frame
        self.table_frame=LabelFrame(main_frame,bd=2,relief=GROOVE,font=("times new roman", 12, "bold"))
        self.table_frame.place(x=5,y=96,width=830,height=395)



    def reset_data(self):
        self.var_department.set("Select")
        self.var_degree.set("Select")
        self.var_semester.set("Select")
        self.var_division.set("Division")
        self.var_sub_code.set("Subject_Code")

        self.dep_combo["values"] = ["Select"]
        self.sem_combo["values"] = ["Select"]
        self.division_combo["values"] = ["Division"]
        self.search_sub_code_combo["values"] = ["Subject_Code"]

        for widget in self.table_frame.winfo_children():
            widget.destroy()



    #create database connection*********************
    def create_connection(self):
        return mysql.connector.connect(
            host="localhost",
            username="root",
            password="Drishey@9845",
            database="face_recognizer"
        )
    

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


    def read_attendance_data(self):
        file_path = f"student/{self.var_degree.get()}/{self.var_department.get()}/{self.var_semester.get()}/attendance.csv"
        attendance_df = pd.read_csv(file_path)
        attendance_df = attendance_df.drop(columns=["Flag"])  # Drop the "Flag" column
        return attendance_df

    # Function to read total classes data from CSV file using pandas
    def read_total_classes(self):
        file_path = f"student/{self.var_degree.get()}/{self.var_department.get()}/{self.var_semester.get()}/total_classes.csv"
        total_classes_df = pd.read_csv(file_path)  # Assuming total classes are in the first column
        
        # select = total_classes_df.loc[0]["EC420"]
        # print(select)


        return total_classes_df
    

    def generate_table(self, table_columns,data):
        for widget in self.table_frame.winfo_children():
            widget.destroy()


        scroll_x=ttk.Scrollbar(self.table_frame,orient=HORIZONTAL)
        scroll_y=ttk.Scrollbar(self.table_frame,orient=VERTICAL)

        self.student_table=ttk.Treeview(self.table_frame,columns=tuple(table_columns),xscrollcommand=scroll_x.set,yscrollcommand=scroll_y.set)

        scroll_x.pack(side=BOTTOM,fill=X)
        scroll_y.pack(side=RIGHT,fill=Y)

        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        
        for col in table_columns:
            self.student_table.heading(col, text=col,anchor="center")
            self.student_table.column(col,width=80, anchor="center")
        
        self.student_table["show"]="headings"
        self.student_table.column("Name", width=150)

        self.student_table.pack(fill=BOTH,expand=1)

        # Populate table with data
        self.student_table.delete(*self.student_table.get_children())
        for row in data:
            self.student_table.insert("", END, values=row)


    def export_table_to_csv_pandas(self):
        table_data = []

        for row in self.student_table.get_children():
            item_dict = self.student_table.item(row)
            table_data.append(item_dict['values'])
        
        
        # Construct the default filename based on export_filename dictionary
        default_filename_parts = []
        
        default_filename_parts.append(self.export_filename['Degree'])
        default_filename_parts.append(self.export_filename['Department'])
        default_filename_parts.append(self.export_filename['Semester'])

        if 'Division' in self.export_filename:
            default_filename_parts.append(self.export_filename['Division'])
        if 'Sub_Code' in self.export_filename:
            default_filename_parts.append(self.export_filename['Sub_Code'])

        default_filename = '_'.join(default_filename_parts) + ".csv"

        # Ask the user to select a file location and name for saving the CSV file
        csv_filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile=default_filename)

            # Check if the user canceled the file dialog
        if csv_filename == "":
            return

        # Set the chosen filename to self.export_filename
        self.export_filename.set(os.path.basename(csv_filename))

        # Convert table data to a DataFrame
        df = pd.DataFrame(table_data, columns=self.student_table["columns"])

        # Write the DataFrame to the selected CSV file location
        df.to_csv(csv_filename, index=False)





    def show_attendance(self):
        if self.var_degree.get()=="Select" or self.var_department.get()=="Select" or self.var_semester.get()=="Select":
            messagebox.showerror("Error", "All Fields are required",parent=self.root)
        else:
            try:
                attendance_df = self.read_attendance_data()
                # total = self.read_total_classes()
                # print(total)

                table_columns = attendance_df.columns.tolist()
                data = attendance_df.values.tolist()
                data = [[0 if str(cell) == 'nan' else cell for cell in row] for row in data]

                subject_df = ["Subject_Code"] + attendance_df.drop(columns=["Name", "Roll_no", "Division"]).columns.tolist()
                self.search_sub_code_combo["values"] = subject_df
                divisions = ["Division"] + self.FILTER_OPTIONS_MAPPING[self.var_degree.get()]["Division"][self.var_department.get()]
                self.division_combo["values"] = divisions


                self.export_filename.clear()
                semester=self.var_semester.get()
                sem=semester.split("-")[1]
                self.export_filename["Degree"] = self.var_degree.get()
                self.export_filename["Department"] = self.var_department.get()
                self.export_filename["Semester"] = sem
 


                self.generate_table(table_columns, data)
            except Exception as es:
                messagebox.showerror("Error", f"Due To:{str(es)}",parent=self.root)


    def apply_filter(self):
        try:
            # Read attendance data
            attendance_df = self.read_attendance_data()
            if 'Division' in self.export_filename:
                del self.export_filename['Division']
            if 'Sub_Code' in self.export_filename:
                del self.export_filename['Sub_Code']

            # Filter by division if selected
            if self.var_division.get() != "Division":
                attendance_df = attendance_df[attendance_df["Division"] == self.var_division.get()]
                
                division = self.var_division.get()
                div=division.split("-")[1]
                self.export_filename["Division"] = div
                


            # Filter by subject code if selected
            if self.var_sub_code.get() != "Subject_Code":
                # Retain only selected columns and add a "Percentage" column
                selected_columns = ["Name", "Roll_no", "Division", self.var_sub_code.get()]
                selected_df = attendance_df[selected_columns].copy()

                
                total_classes = self.read_total_classes()
                total_classes = total_classes.loc[0][self.var_sub_code.get()]
                # print(total_classes)
                selected_df["Total Classes"] = float(total_classes)
                selected_df["Percentage"] = round((selected_df[self.var_sub_code.get()] / total_classes) * 100, 2)


                data = selected_df.values.tolist()
                data = [[0 if str(cell) == 'nan' else cell for cell in row] for row in data]


                self.export_filename["Sub_Code"] = self.var_sub_code.get()


                # Generate table with filtered data
                self.generate_table(selected_df.columns.tolist(), data)
            else:
                # Generate table with filtered attendance data
                data = attendance_df.values.tolist()
                data = [[0 if str(cell) == 'nan' else cell for cell in row] for row in data]
                self.generate_table(attendance_df.columns.tolist(), data)
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)






if __name__=="__main__":
    root=Tk()
    obj=Attendance_sheet(root)
    root.mainloop()