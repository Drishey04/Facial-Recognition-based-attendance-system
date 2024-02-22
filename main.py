from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from student import Student
from attendance_sheet import Attendance_sheet
from faculty import Faculty
from subject import Subject
import os



class Face_Recognition_System:
    def __init__(self,root):
        self.root=root
        self.root.geometry("880x590")
        self.root.title("Face Recognition System")

        #landing page image and title
        img=Image.open(r"Photos\landing_page.jpg")
        img=img.resize((880,590))
        self.landingbgd=ImageTk.PhotoImage(img)

        bg_img=Label(self.root,image=self.landingbgd)
        bg_img.place(x=0,y=0,width=880,height=590)


        title = Canvas(bg_img,width=790, height=45)
        title.place(x=40,y=10)
        
        sp_img=Image.open(r"D:\SVNIT\SEMSTER-8\Project\Project_1\Photos\landing_page_title.png")
        sp_img=sp_img.resize((800,50))
        self.sp_title=ImageTk.PhotoImage(sp_img)

        title.create_image(0, 0, anchor="nw", image=self.sp_title)
        title.create_text(400, 20, text="Facial Recognition based Attendance System", font=("times new roman", 30, "bold"), fill="darkgreen")






        # title_lbL=Label(bg_img,text="Faced Recognition Attendance System",font=("times new roman", 30, "bold"), bg="white",fg="red")
        # title_lbL.place(x=0,y=0,width=880,height=50)

        #button-1
        img1=Image.open(r"Photos\student_icon.png")
        img1=img1.resize((200,200))
        self.photoimg=ImageTk.PhotoImage(img1)

        b1=Button(bg_img,image=self.photoimg,command=self.student_details,cursor="hand2")
        b1.place(x=180,y=100,width=200,height=200)

        b1=Button(bg_img,text="Student Details",command=self.student_details,cursor="hand2",font=("times new roman", 20, "bold"), bg="blue",fg="white")
        b1.place(x=180,y=255,width=200,height=45)


        #button-2
        img2=Image.open(r"Photos\faculty_icon.jpg")
        img2=img2.resize((200,200))
        self.photoimg2=ImageTk.PhotoImage(img2)

        b2=Button(bg_img,image=self.photoimg2,command=self.faculty_details,cursor="hand2")
        b2.place(x=500,y=100,width=200,height=200)

        b2=Button(bg_img,text="Faculty Details",command=self.faculty_details,cursor="hand2",font=("times new roman", 19, "bold"), bg="blue",fg="white")
        b2.place(x=500,y=255,width=200,height=45)


        #button-3
        img3=Image.open(r"Photos\subject_icon.jpg")
        img3=img3.resize((200,200))
        self.photoimg3=ImageTk.PhotoImage(img3)

        b3=Button(bg_img,image=self.photoimg3,command=self.subject_details,cursor="hand2")
        b3.place(x=180,y=350,width=200,height=200)

        b3=Button(bg_img,text="Subject Details",command=self.subject_details,cursor="hand2",font=("times new roman", 19, "bold"), bg="blue",fg="white")
        b3.place(x=180,y=505,width=200,height=45)


        #button-4
        img4=Image.open(r"Photos\attendance_icon.png")
        img4=img4.resize((200,200))
        self.photoimg4=ImageTk.PhotoImage(img4)

        b4=Button(bg_img,image=self.photoimg4,command=self.attendance_details,cursor="hand2")
        b4.place(x=500,y=350,width=200,height=200)

        b4=Button(bg_img,text="Attendance Sheet",command=self.attendance_details,cursor="hand2",font=("times new roman", 19, "bold"), bg="blue",fg="white")
        b4.place(x=500,y=505,width=200,height=45)


    #****************functions button***************
    def student_details(self):
        self.new_window=Toplevel(self.root)
        self.app=Student(self.new_window)

    def faculty_details(self):
        self.new_window=Toplevel(self.root)
        self.app=Faculty(self.new_window)
    
    def subject_details(self):
        self.new_window=Toplevel(self.root)
        self.app=Subject(self.new_window)
    
    def attendance_details(self):
        self.new_window=Toplevel(self.root)
        self.app=Attendance_sheet(self.new_window)








if __name__=="__main__":
    root=Tk()
    obj=Face_Recognition_System(root)
    root.mainloop()