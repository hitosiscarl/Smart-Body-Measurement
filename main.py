

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from time import sleep
from PIL import Image, ImageTk
from numpy import sqrt
import cv2
import mediapipe as mp
import datetime as dt
import numpy as np
import sqlite3
import serial
import math

#Initialize Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)

# Initialize mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

#Initialize database
conn = sqlite3.connect("cust.db")
curr = conn.cursor()

#Main window
window = Tk()
window.resizable(False, False)
window.title("Body Measurement")
window.geometry("1024x570")
window.configure(bg = '#FAC1D4')
#window.wm_attributes('-type', 'splash')
#window.overrideredirect(1)
#pinkbg = PhotoImage(file = r"bg.png")
#bglbl = Label(window, image = pinkbg)
#bglbl.place(x = 0, y = 0)

#Photos/Icons
pic_upload = PhotoImage(file = r"upload.png")
pic_takephoto = PhotoImage(file = r"takephoto.png")
pic_new = PhotoImage(file = r"new.png")
pic_database = PhotoImage(file = r"database.png")
pic_exitb = PhotoImage(file = r"exit.png")

pic_v1 = PhotoImage(file = r"v1.png")
pic_v2 = PhotoImage(file = r"v2.png")
pic_v3 = PhotoImage(file = r"v3.png")
pic_v4 = PhotoImage(file = r"v4.png")

upload_v1 = PhotoImage(file = r"uploadv1.png")
upload_v2 = PhotoImage(file = r"uploadv2.png")
upload_v3 = PhotoImage(file = r"uploadv3.png")
upload_v4 = PhotoImage(file = r"uploadv4.png")

c = 0

#Customer Info
projid = StringVar()
custname = StringVar()
cdate = StringVar()
ctime = StringVar()
cnotes = StringVar()

shoulder = IntVar()
arm_length = IntVar()
upper_arm_length = IntVar()
hip = IntVar()
hip_height = IntVar()
thigh = IntVar()
knee = IntVar()
knee_height = IntVar()
calf = IntVar()
ankle = IntVar()

db_search = StringVar()

def dbFunc():
    global conn, curr
    conn = sqlite3.connect("cust.db")
    curr = conn.cursor()
   
def MainMenu():
    global main_frame
    main_frame = Frame(window, bg = '#FAC1D4')
    main_frame.pack(pady = 50)

    btn_takephoto = Button(main_frame, text = "\nNew Measurement", bg = '#D38CA1', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_new, width = 350, height = 300, font = "Rockwell 20 bold", compound = TOP, relief = FLAT, command = NewMeasurement)
    btn_takephoto.grid(row = 1, column = 1, pady = 20, padx = 20)
    btn_db = Button(main_frame, text = "\nCustomer Database", bg = '#D38CA1', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_database, width = 350, height = 300, font = "Rockwell 20 bold", compound = TOP, relief = FLAT, command = DataBase)
    btn_db.grid(row = 1, column = 2, pady = 20, padx = 20)
   
    btn_exit = Button(main_frame, text = " Exit", bg = '#FAC1D4', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_exitb, width = 200, font = "Rockwell 18 bold", compound = LEFT, relief = FLAT, command = ExitApp)
    btn_exit.grid(row = 2, column = 2, pady = 30, padx = 20)

def UpdateFrame():
    global frame, cap, photo
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1140)
    #cap.set(cv2.CAP_PROP_EXPOSURE, -6)
    while True:
        success, frame = cap.read()
        if not success:
            print("naglaho bidyeo")
            break
        image = cv2.resize(frame, (260, 460))
        row_index = 1100
        alpha = 1.5
        beta = 25
        image = cv2.convertScaleAbs(image, alpha = alpha, beta = beta)
        image = Image.fromarray(image)
        photo = ImageTk.PhotoImage(image)
        framecanvas.create_image(0, 0, anchor = NW, image =  photo)
        window.update()
    cap.release()
    cv2.destroyAllWindows()

def distanceSensor():
    global list_dist, ser
    ser = serial.Serial('/dev/ttyACM0', 9600)
    list_dist = []
    while True:
        line = ser.readline().decode().strip()
        if line == "Distance = Out of range":
            dist = 0
        else:
            dist = re.findall(r'\d+\.\d+', line)
            dist = int(float(dist[0]))
        list_dist.append(dist)
        if len(list_dist) == 10:
            ser.close()
            distance = int(sum(list_dist)/len(list_dist))
            return distance

def ExitApp():
    proceed = messagebox.askyesno("", "Exit?")
    if proceed == 1:
        window.quit()
        window.destroy()
    else:
        return
########################################################NEW MEASUREMENT#######################################################
def NewMeasurement():
    global new_measure_frame
    main_frame.pack_forget()
    new_measure_frame = Frame(window, bg = '#FAC1D4')
    new_measure_frame.pack(pady = 50)
    left_frame = Frame(new_measure_frame, bg = '#FAC1D4')
    left_frame.pack(side = LEFT, padx = 15)
    right_frame = Frame(new_measure_frame, bg = '#FAC1D4')
    right_frame.pack(side = RIGHT, padx = 15)

    base_frame = Frame(left_frame, bg = '#FAC1D4')
    base_frame.pack(fill = X)

    dbFunc()
    curr.execute("""SELECT COUNT(DISTINCT projID) FROM project""")
    fetch = curr.fetchone()
    n = int(1)
    for x in fetch:
        n+=x
    n2 = str(n)
    projid.set("PROJ" + n2.zfill(6))
    custname.set("")
    cnotes.set("")
   
    lbl_projid = Label(base_frame, text = "Project ID: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_projid.grid(row = 1, sticky = W, pady = 6)
    lbl_custname = Label(base_frame, text = "Name: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_custname.grid(row = 2, sticky = W, pady = 6)
    lbl_cdate = Label(base_frame, text = "Date: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_cdate.grid(row = 3, sticky = W, pady = 6)
    lbl_ctime = Label(base_frame, text = "Time: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_ctime.grid(row = 4, sticky = W, pady = 6)
    lbl_cnotes = Label(base_frame, text = "Notes: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_cnotes.grid(row = 5, sticky = W, pady = 6)

    projid_entry = Label(base_frame, text = projid.get(), font = "Rockwell 20", bg = '#FAC1D4')
    projid_entry.grid(row = 1, column = 1, sticky = W)
    custname_entry = Entry(base_frame, textvariable = custname, width = 24, font = "Rockwell 20")
    custname_entry.grid(row = 2, pady=3, column = 1, sticky = W)
    now = dt.datetime.now()
    date = now.strftime("%B:%d:%Y")
    cdate_entry = Label(base_frame, text = date, font = "Rockwell 20", bg = '#FAC1D4')
    cdate_entry.grid(row = 3, column = 1, sticky = W)
    time = now.strftime("%I:%M:%S")
    ctime_entry = Label(base_frame, text = time, font = "Rockwell 20", bg = '#FAC1D4')
    ctime_entry.grid(row = 4, column = 1, sticky = W)
    cnotes_entry = Entry(base_frame, textvariable = cnotes, width = 24, font = "Rockwell 20")
    cnotes_entry.grid(row = 5, column = 1, sticky = W)
    cdate.set(date)
    ctime.set(time)

    btn_take = Button(right_frame, text = "  Take Photos", bg = '#D38CA1', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_takephoto, width = 350, height = 120, font = "Rockwell 20 bold", compound = LEFT, relief = FLAT, command = TakePhoto)
    btn_take.grid(row = 1, pady = 10)
    btn_upload = Button(right_frame, text = "  Upload Photos", bg = '#D38CA1', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_upload, width = 350, height = 120, font = "Rockwell 20 bold", compound = LEFT, relief = FLAT, command = UploadPhoto)
    btn_upload.grid(row = 2, pady = 10)
    btn_back = Button(right_frame, text = " Back", bg = '#FAC1D4', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_database, width = 350, height = 120, font = "Rockwell 18 bold", compound = LEFT, relief = FLAT, command = MeasureBackMain)
    btn_back.grid(row = 3, pady = 20)

def MeasureBackMain():
    new_measure_frame.pack_forget()
    main_frame.pack(pady = 50)
   
def TakePhoto():
    global take_photo_frame, framecanvas, posecanvas, btn_takephoto
    cust = custname.get()
    notes = cnotes.get()
    if cust == "" or notes == "":
        messagebox.showerror('Entry Error', 'Fill in missing entries!')
    else:
        proceed = messagebox.askyesno("", "Proceed?")
        if proceed == 1:
            dbFunc()
            curr.execute("""INSERT INTO project VALUES(?, ?, ?, ?, ?, ?)""", (str(projid.get()), str(custname.get()), str(cdate.get()), str(ctime.get()), str(cnotes.get()), str("On-site")))
            conn.commit()
            curr.close()
            conn.close()
            new_measure_frame.pack_forget()
            take_photo_frame = Frame(window, bg = '#FAC1D4')
            take_photo_frame.pack(pady = 10)
            cvs_frame = Frame(take_photo_frame, bg = '#FAC1D4')
            cvs_frame.pack(side = TOP, fill = X, anchor = CENTER)
            btn_frame = Frame(take_photo_frame, bg = '#FAC1D4')
            btn_frame.pack(side = BOTTOM, pady = 10, fill = X)
           
            posecanvas = Canvas(cvs_frame, width = 256, height = 426)
            posecanvas.pack(side = LEFT, padx = 125)
            posecanvas.create_image(0,0, anchor ='nw', image = pic_v1)
            framecanvas = Canvas(cvs_frame, width = 256, height = 426)
            framecanvas.pack(side = LEFT, padx = 125)
           
            btn_takephoto = Button(btn_frame, text = "  Take Photos", bg = '#D38CA1', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_takephoto, width = 350, height = 60, font = "Rockwell 20 bold", compound = LEFT, relief = FLAT, command = CaptureFrame)
            btn_takephoto.config(state = NORMAL)
            btn_takephoto.pack()

            UpdateFrame()
            cap.release()
            cv2.destroyAllWindows()
        else:
            print("chose no")
       
def CaptureFrame():
    global image, c, frontcanvas, front, right, left, back, fdistance, rdistance, ldistance, bdistance
    x = projid.get()
    alpha = 1
    beta = 25
    print(c)
    while c == 0:
        print("Front View")
        fdistance = distanceSensor()
        print(fdistance)
        btn_takephoto.config(state = DISABLED)
        front = "/home/opstrix/Desktop/bodymeasurement/temp/{}_FRONT.png".format(x)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.convertScaleAbs(image, alpha = alpha, beta = beta)
        cv2.imwrite(front, image)
        img = cv2.imread(front)
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_model:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose_model.process(image)
            focalpts = 0
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    if landmark.visibility > 0.5:
                        focalpts += 1
                if focalpts == 33:
                    MediapipeFront(front, fdistance)
                    photo = Image.open(front)
                    photo = photo.resize((256,456), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(photo)
                    try:
                        posecanvas.create_image(0, 0, anchor = NW, image =  photo)
                        posecanvas.itemconfig(image_container, image = photo)
                    except:
                        pass
                    proceed = messagebox.askyesno("", "Proceed?")
                    if proceed == 1:
                        btn_takephoto.config(state = NORMAL)
                        try:
                            posecanvas.create_image(0, 0, anchor = NW, image =  pic_v2)
                            posecanvas.itemconfig(image_container, image = pic_v2)
                        except:
                            pass
                        c+=1
                        return
                    else:
                        print("chose no")
                        btn_takephoto.config(state = NORMAL)
                        posecanvas.create_image(0, 0, anchor = NW, image =  pic_v1)
                        posecanvas.itemconfig(image_container, image = pic_v1)
                        break
                else:
                    btn_takephoto.config(state = NORMAL)
                    print("focalpts")
                    messagebox.showerror('Invalid Photo', 'Focal Point Error')
                    break
            else:
                btn_takephoto.config(state = NORMAL)
                print("no pose")
                messagebox.showerror('Invalid Photo', 'Pose not Detected')
                break
    while c == 1:
        print("Right View")
        rdistance = distanceSensor()
        print(rdistance)
        btn_takephoto.config(state = DISABLED)
        right = "/home/opstrix/Desktop/bodymeasurement/temp/{}_RIGHT.png".format(x)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.convertScaleAbs(image, alpha = alpha, beta = beta)
        cv2.imwrite(right, image)
        img = cv2.imread(right)
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_model:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose_model.process(image)
            focalpts = 0
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    if landmark.visibility > 0.5:
                        focalpts += 1
                if focalpts >= 20 and focalpts <= 33:
                    print(focalpts)
                    MediapipeRight(right, rdistance)
                    photo = Image.open(right)
                    photo = photo.resize((256,456), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(photo)
                    try:
                        posecanvas.create_image(0, 0, anchor = NW, image =  photo)
                        posecanvas.itemconfig(image_container, image = photo)
                    except:
                        pass
                    proceed = messagebox.askyesno("", "Proceed?")
                    if proceed == 1:
                        btn_takephoto.config(state = NORMAL)
                        try:
                            posecanvas.create_image(0, 0, anchor = NW, image =  pic_v3)
                            posecanvas.itemconfig(image_container, image = pic_v3)
                        except:
                            pass
                        c+=1
                        return
                    else:
                        print("chose no")
                        btn_takephoto.config(state = NORMAL)
                        posecanvas.create_image(0, 0, anchor = NW, image =  pic_v2)
                        posecanvas.itemconfig(image_container, image = pic_v2)
                        break
                else:
                    btn_takephoto.config(state = NORMAL)
                    print("focalpts")
                    messagebox.showerror('Invalid Photo', 'Focal Point Error')
                    break
            else:
                btn_takephoto.config(state = NORMAL)
                print("no pose")
                messagebox.showerror('Invalid Photo', 'Pose not Detected')
                break
    while c == 2:
        print("Left View")
        ldistance = distanceSensor()
        print(ldistance)
        btn_takephoto.config(state = DISABLED)
        left = "/home/opstrix/Desktop/bodymeasurement/temp/{}_LEFT.png".format(x)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.convertScaleAbs(image, alpha = alpha, beta = beta)
        cv2.imwrite(left, image)
        img = cv2.imread(left)
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_model:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose_model.process(image)
            focalpts = 0
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    if landmark.visibility > 0.5:
                        focalpts += 1
                print(focalpts)
                if focalpts >= 20 and focalpts <= 33:
                    MediapipeLeft(left, ldistance)
                    photo = Image.open(left)
                    photo = photo.resize((256,456), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(photo)
                    try:
                        posecanvas.create_image(0, 0, anchor = NW, image =  photo)
                        posecanvas.itemconfig(image_container, image = photo)
                    except:
                        pass
                    proceed = messagebox.askyesno("", "Proceed?")
                    if proceed == 1:
                        btn_takephoto.config(state = NORMAL)
                        try:
                            posecanvas.create_image(0, 0, anchor = NW, image =  pic_v4)
                            posecanvas.itemconfig(image_container, image = pic_v4)
                        except:
                            pass
                        c+=1
                        return
                    else:
                        print("chose no")
                        btn_takephoto.config(state = NORMAL)
                        posecanvas.create_image(0, 0, anchor = NW, image =  pic_v3)
                        posecanvas.itemconfig(image_container, image = pic_v3)
                        break
                else:
                    btn_takephoto.config(state = NORMAL)
                    print("focalpts")
                    messagebox.showerror('Invalid Photo', 'Focal Point Error')
                    break
            else:
                btn_takephoto.config(state = NORMAL)
                print("no pose")
                messagebox.showerror('Invalid Photo', 'Pose not Detected')
                break
    while c == 3:
        print("Back View")
        bdistance = distanceSensor()
        print(bdistance)
        btn_takephoto.config(state = DISABLED)
        back = "/home/opstrix/Desktop/bodymeasurement/temp/{}_BACK.png".format(x)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.convertScaleAbs(image, alpha = alpha, beta = beta)
        cv2.imwrite(back, image)
        img = cv2.imread(back)
        with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose_model:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose_model.process(image)
            focalpts = 0
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    if landmark.visibility > 0.5:
                        focalpts += 1
                if focalpts == 33:
                    MediapipeBack(back, bdistance)
                    photo = Image.open(back)
                    photo = photo.resize((256,456), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(photo)
                    try:
                        posecanvas.create_image(0, 0, anchor = NW, image =  photo)
                        posecanvas.itemconfig(image_container, image = photo)
                    except:
                        pass
                    proceed = messagebox.askyesno("", "Proceed?")
                    if proceed == 1:
                        btn_takephoto.config(state = NORMAL)
                        try:
                            posecanvas.create_image(0, 0, anchor = NW, image =  pic_v1)
                            posecanvas.itemconfig(image_container, image = pic_v1)
                        except:
                            pass
                        dbFunc()
                        curr.execute("""INSERT INTO photos VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", (str(x), str(front), int(fdistance), str(right), int(rdistance), str(left), int(ldistance), str(back), int(bdistance)))
                        conn.commit()
                        curr.close()
                        conn.close()
                        c+=1
                        break
                    else:
                        print("chose no")
                        btn_takephoto.config(state = NORMAL)
                        posecanvas.create_image(0, 0, anchor = NW, image =  pic_v4)
                        posecanvas.itemconfig(image_container, image = pic_v4)
                        break
                else:
                    btn_takephoto.config(state = NORMAL)
                    print("focalpts")
                    messagebox.showerror('Invalid Photo', 'Focal Point Error')
                    break
            else:
                btn_takephoto.config(state = NORMAL)
                print("no pose")
                messagebox.showerror('Invalid Photo', 'Pose not Detected')
                break
    if c == 4:
        take_photo_frame.pack_forget()
        Result()
        c = 0

#####################################################UPLOAD PHOTO#####################################################      
def UploadPhoto():
    global upload_photo_frame, posecanvas, framecanvas, btn_takephoto
    cust = custname.get()
    notes = cnotes.get()
    if cust == "" or notes == "":
        messagebox.showerror('Entry Error', 'Fill in missing entries!')
    else:
        proceed = messagebox.askyesno("", "Proceed?")
        if proceed == 1:
            dbFunc()
            curr.execute("""INSERT INTO project VALUES(?, ?, ?, ?, ?, ?)""", (str(projid.get()), str(custname.get()), str(cdate.get()), str(ctime.get()), str(cnotes.get()), str("Off-site")))
            conn.commit()
            curr.close()
            conn.close()
            new_measure_frame.pack_forget()
            upload_photo_frame = Frame(window, bg = '#FAC1D4')
            upload_photo_frame.pack()
            cvs_frame = Frame(upload_photo_frame, bg = '#FAC1D4')
            cvs_frame.pack(side = TOP, fill = X, pady = 10, anchor = CENTER)
            btn_frame = Frame(upload_photo_frame, bg = '#FAC1D4')
            btn_frame.pack(side = BOTTOM, pady = 10, fill = X)
           
            posecanvas = Canvas(cvs_frame, width = 256, height = 456)
            posecanvas.pack(side = LEFT, padx = 125)
            posecanvas.create_image(0,0, anchor ='nw', image = pic_v1)

            framecanvas = Canvas(cvs_frame, width = 256, height = 456)
            framecanvas.pack(side = LEFT, padx = 125)
            framecanvas.create_image(0,0, anchor ='nw', image = upload_v1)

            btn_takephoto = Button(btn_frame, text = "  Upload", bg = '#D38CA1', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_takephoto, width = 350, height = 100, font = "Rockwell 20 bold", compound = LEFT, relief = FLAT, command = PhotoUpload)
            btn_takephoto.config(state = NORMAL)
            btn_takephoto.pack()
        else:
            print("choose no")

def PhotoUpload():
    global image, c, frontcanvas, front, right, left, back, fdistance, rdistance, ldistance, bdistance
    x = projid.get()
    print(c)
    while c == 0:
        print("Front View")
        fdistance = 200
        btn_takephoto.config(state = DISABLED)
        frontupload = filedialog.askopenfilename()
        if not frontupload:
            btn_takephoto.config(state = NORMAL)
            break
        front = "/home/opstrix/Desktop/bodymeasurement/temp/{}_FRONT.png".format(x)
        frontsrc = cv2.imread(frontupload)
        cv2.imwrite(front, frontsrc)
        img = cv2.imread(front)
        with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose_model:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose_model.process(image)
            focalpts = 0
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    if landmark.visibility > 0.5:
                        focalpts += 1
                if focalpts == 33:
                    MediapipeFront(front, fdistance)
                    photo = Image.open(front)            
                    photo = photo.resize((256,456), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(photo)
                    try:
                        framecanvas.create_image(0, 0, anchor = NW, image =  photo)
                        framecanvas.itemconfig(image_container, image = photo)
                    except:
                        pass
                    proceed = messagebox.askyesno("", "Proceed?")
                    if proceed == 1:
                        btn_takephoto.config(state = NORMAL)
                        try:
                            posecanvas.create_image(0, 0, anchor = NW, image =  pic_v2)
                            posecanvas.itemconfig(image_container, image = pic_v2)
                            framecanvas.create_image(0,0, anchor ='nw', image = upload_v2)
                        except:
                            pass
                        c+=1
                        return
                    else:
                        print("chose no")
                        btn_takephoto.config(state = NORMAL)
                        posecanvas.create_image(0, 0, anchor = NW, image =  pic_v1)
                        posecanvas.itemconfig(image_container, image = pic_v1)
                        framecanvas.create_image(0,0, anchor ='nw', image = upload_v1)
                        break
                else:
                    btn_takephoto.config(state = NORMAL)
                    print("focalpts")
                    messagebox.showerror('Invalid Photo', 'Focal Point Error')
                    break
            else:
                btn_takephoto.config(state = NORMAL)
                print("no pose")
                messagebox.showerror('Invalid Photo', 'Pose not Detected')
                break
    while c == 1:
        print("Right View")
        rdistance = 200
        btn_takephoto.config(state = DISABLED)
        rightupload = filedialog.askopenfilename()
        if not rightupload:
            btn_takephoto.config(state = NORMAL)
            break
        right = "/home/opstrix/Desktop/bodymeasurement/temp/{}_RIGHT.png".format(x)
        rightsrc = cv2.imread(rightupload)
        cv2.imwrite(right, rightsrc)
        img = cv2.imread(right)
        with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose_model:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose_model.process(image)
            focalpts = 0
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    if landmark.visibility > 0.5:
                        focalpts += 1
                if focalpts >= 20 and focalpts <= 33:
                    MediapipeRight(right, rdistance)
                    photo = Image.open(right)            
                    photo = photo.resize((256,456), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(photo)
                    try:
                        framecanvas.create_image(0, 0, anchor = NW, image =  photo)
                        framecanvas.itemconfig(image_container, image = photo)
                    except:
                        pass
                    proceed = messagebox.askyesno("", "Proceed?")
                    if proceed == 1:
                        btn_takephoto.config(state = NORMAL)
                        try:
                            posecanvas.create_image(0, 0, anchor = NW, image =  pic_v3)
                            posecanvas.itemconfig(image_container, image = pic_v3)
                            framecanvas.create_image(0,0, anchor ='nw', image = upload_v3)
                        except:
                            pass
                        c+=1
                        return
                    else:
                        print("chose no")
                        btn_takephoto.config(state = NORMAL)
                        posecanvas.create_image(0, 0, anchor = NW, image =  pic_v2)
                        posecanvas.itemconfig(image_container, image = pic_v2)
                        framecanvas.create_image(0,0, anchor ='nw', image = upload_v2)
                        break
                else:
                    btn_takephoto.config(state = NORMAL)
                    print("focalpts")
                    messagebox.showerror('Invalid Photo', 'Focal Point Error')
                    break
            else:
                btn_takephoto.config(state = NORMAL)
                print("no pose")
                messagebox.showerror('Invalid Photo', 'Pose not Detected')
                break
    while c == 2:
        print("Left View")
        ldistance = 200
        btn_takephoto.config(state = DISABLED)
        leftupload = filedialog.askopenfilename()
        if not leftupload:
            btn_takephoto.config(state = NORMAL)
            break
        left = "/home/opstrix/Desktop/bodymeasurement/temp/{}_LEFT.png".format(x)
        leftsrc = cv2.imread(leftupload)
        cv2.imwrite(left, leftsrc)
        img = cv2.imread(left)
        with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose_model:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose_model.process(image)
            focalpts = 0
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    if landmark.visibility > 0.5:
                        focalpts += 1
                if focalpts >= 20 and focalpts <= 33:
                    MediapipeLeft(left, ldistance)
                    photo = Image.open(left)            
                    photo = photo.resize((256,456), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(photo)
                    try:
                        framecanvas.create_image(0, 0, anchor = NW, image =  photo)
                        framecanvas.itemconfig(image_container, image = photo)
                    except:
                        pass
                    proceed = messagebox.askyesno("", "Proceed?")
                    if proceed == 1:
                        btn_takephoto.config(state = NORMAL)
                        try:
                            posecanvas.create_image(0, 0, anchor = NW, image =  pic_v4)
                            posecanvas.itemconfig(image_container, image = pic_v4)
                            framecanvas.create_image(0,0, anchor ='nw', image = upload_v4)
                        except:
                            pass
                        c+=1
                        return
                    else:
                        print("chose no")
                        btn_takephoto.config(state = NORMAL)
                        posecanvas.create_image(0, 0, anchor = NW, image =  pic_v3)
                        posecanvas.itemconfig(image_container, image = pic_v3)
                        framecanvas.create_image(0,0, anchor ='nw', image = upload_v3)
                        break
                else:
                    btn_takephoto.config(state = NORMAL)
                    print("focalpts")
                    messagebox.showerror('Invalid Photo', 'Focal Point Error')
                    break
            else:
                btn_takephoto.config(state = NORMAL)
                print("no pose")
                messagebox.showerror('Invalid Photo', 'Pose not Detected')
                break
    while c == 3:
        print("Back View")
        bdistance = 200
        btn_takephoto.config(state = DISABLED)
        backupload = filedialog.askopenfilename()
        if not backupload:
            btn_takephoto.config(state = NORMAL)
            break
        back = "/home/opstrix/Desktop/bodymeasurement/temp/{}_BACK.png".format(x)
        backsrc = cv2.imread(backupload)
        cv2.imwrite(back, backsrc)
        img = cv2.imread(back)
        with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose_model:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose_model.process(image)
            focalpts = 0
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    if landmark.visibility > 0.5:
                        focalpts += 1
                if focalpts == 33:
                    MediapipeBack(back, bdistance)
                    photo = Image.open(back)            
                    photo = photo.resize((256,456), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(photo)
                    try:
                        framecanvas.create_image(0, 0, anchor = NW, image =  photo)
                        framecanvas.itemconfig(image_container, image = photo)
                    except:
                        pass
                    proceed = messagebox.askyesno("", "Proceed?")
                    if proceed == 1:
                        btn_takephoto.config(state = DISABLED)
                        try:
                            posecanvas.create_image(0, 0, anchor = NW, image =  pic_v1)
                            posecanvas.itemconfig(image_container, image = pic_v1)
                            framecanvas.create_image(0,0, anchor ='nw', image = upload_v1)
                        except:
                            pass
                        dbFunc()
                        curr.execute("""INSERT INTO photos VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", (str(x), str(front), int(fdistance), str(right), int(rdistance), str(left), int(ldistance), str(back), int(bdistance)))
                        conn.commit()
                        curr.close()
                        conn.close()
                        c+=1
                        print(c)
                        break
                    else:
                        print("chose no")
                        btn_takephoto.config(state = NORMAL)
                        posecanvas.create_image(0, 0, anchor = NW, image =  pic_v4)
                        posecanvas.itemconfig(image_container, image = pic_v4)
                        framecanvas.create_image(0,0, anchor ='nw', image = upload_v4)
                        break
                else:
                    btn_takephoto.config(state = NORMAL)
                    print("focalpts")
                    messagebox.showerror('Invalid Photo', 'Focal Point Error')
                    break
            else:
                btn_takephoto.config(state = NORMAL)
                print("no pose")
                messagebox.showerror('Invalid Photo', 'Pose not Detected')
                break
    if c == 4:
        upload_photo_frame.pack_forget()
        Result()
        c = 0
       
#############################################################Algo##############################################################
def MediapipeFront(front, distance):
    global f_shoulder, f_hip_girth, f_rthigh_girth, f_lthigh_girth, f_rknee_girth, f_lknee_girth, f_rcalf_girth, f_lcalf_girth, f_rankle_girth, f_lankle_girth
    x = projid.get()
    distance = distance/2.54
    img = cv2.imread(front)
    with mp_pose.Pose(static_image_mode = True, min_detection_confidence=0.5, enable_segmentation = True) as pose:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img)

        mask = results.segmentation_mask.astype(float)
        mask = cv2.normalize(mask, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        frontbinary = "/home/opstrix/Desktop/bodymeasurement/temp/{}_BINARY_FRONT.png".format(x)
        cv2.imwrite(frontbinary, mask)
        binary = cv2.imread(frontbinary, cv2.IMREAD_GRAYSCALE)
        edges = cv2.Canny(binary, 1, 250)
        canny = "/home/opstrix/Desktop/bodymeasurement/temp/{}_Canny_FRONT.jpg".format(x)
        cv2.imwrite(canny, edges)
        canny = cv2.imread(canny, cv2.IMREAD_GRAYSCALE)
        points = cv2.findNonZero(canny)
           
        left_shoulder = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * img.shape[1],
                         results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * img.shape[0])                
        right_shoulder = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * img.shape[1],
                          results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * img.shape[0])
        left_elbow = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].y * img.shape[0])
        right_elbow = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].x * img.shape[1],
                      results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].y * img.shape[0])
        left_wrist = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * img.shape[0])
        right_wrist = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x * img.shape[1],
                      results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * img.shape[0])
        left_hip = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x * img.shape[1],
                   results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * img.shape[0])
        right_hip = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x * img.shape[1],
                    results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y * img.shape[0])
        left_knee = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x * img.shape[1],
                    results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y * img.shape[0])
        right_knee = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].y * img.shape[0])
        left_ankle = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x * img.shape[1],
                        results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y * img.shape[0])
        right_ankle = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].x * img.shape[1],
                        results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].y * img.shape[0])

        #Shoulder Width
        shoulder_pixels = abs(left_shoulder[0] - right_shoulder[0])
        f_shoulder = ((distance * 4.6 * shoulder_pixels)/(3.04 * img.shape[0])) * 1.36
        print("Shoulder", f_shoulder)

        #Hip Girth
        x = int(left_hip[0])
        y = int(left_hip[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:  
                    min_dist = dist
                    left_edge = p[0]
        x = int(right_hip[0])
        y = int(right_hip[1])
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        hip_girth_pixel = x - left_edge[0]
        f_hip_girth = ((distance * 4.6 * hip_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Hip Girth:", f_hip_girth)

        #Thigh Girth(RIGHT)
        x = int((right_knee[0] + right_hip[0])/2)
        y = int((right_knee[1] + right_hip[1])/2)
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        thigh_girth_pixel = x - left_edge[0]
        f_rthigh_girth = ((distance * 4.6 * thigh_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Right Thigh Girth:", f_rthigh_girth)
       
        #Thigh Girth(LEFT)
        x = int((left_knee[0] + left_hip[0])/2)
        y = int((left_knee[1] + left_hip[1])/2)
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        thigh_girth_pixel = x - left_edge[0]
        f_lthigh_girth = ((distance * 4.6 * thigh_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Left Thigh Girth:", f_lthigh_girth)

        #Knee Girth(RIGHT)
        x = int(right_knee[0])
        y = int(right_knee[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        knee_girth_pixel = x - left_edge[0]
        f_rknee_girth = ((distance * 4.6 * knee_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Right Knee Girth:", f_rknee_girth)
       
        #Knee Girth(LEFT)
        x = int(left_knee[0])
        y = int(left_knee[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        knee_girth_pixel = x - left_edge[0]
        f_lknee_girth = ((distance * 4.6 * knee_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Left Knee Girth:", f_lknee_girth)

        #Calf Girth(RIGHT)
        x = int((right_ankle[0] + right_knee[0])/2)
        y = int((right_ankle[1] + right_knee[1])/2)
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        calf_girth_pixel = x - left_edge[0]
        f_rcalf_girth = ((distance * 4.6 * calf_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Right Calf Girth:", f_rcalf_girth)
       
        #Calf Girth(LEFT)
        x = int((left_ankle[0] + left_knee[0])/2)
        y = int((left_ankle[1] + left_knee[1])/2)
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        calf_girth_pixel = x - left_edge[0]
        f_lcalf_girth = ((distance * 4.6 * calf_girth_pixel/(3.04 * img.shape[0]))) * 1.36  
        print("Left Girth:", f_lcalf_girth)

        #Ankle Girth(RIGHT)
        x = int(right_ankle[0])
        y = int(right_ankle[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        ankle_girth_pixel = x - left_edge[0]
        f_rankle_girth = ((distance * 4.6 * ankle_girth_pixel/(3.04 * img.shape[0]))) * 1.36      
        print("Right Ankle Girth:", f_rankle_girth)

        #Ankle Girth(LEFT)
        x = int(left_ankle[0])
        y = int(left_ankle[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        ankle_girth_pixel = x - left_edge[0]
        f_lankle_girth = ((distance * 4.6 * ankle_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Left Ankle Girth:", f_lankle_girth)

def MediapipeRight(right, distance):
    global r_height, r_arm_length, r_upper_arm_length, r_hip_girth, r_hip_height, r_thigh_girth, r_knee_girth, r_knee_height, r_calf_girth, r_ankle_girth
    x = projid.get()
    distance = distance/2.54
    img = cv2.imread(right)
    with mp_pose.Pose(static_image_mode = True, min_detection_confidence=0.5, enable_segmentation = True) as pose:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img)

        mask = results.segmentation_mask.astype(float)
        mask = cv2.normalize(mask, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        rightbinary = "/home/opstrix/Desktop/bodymeasurement/temp/{}_BINARY_RIGHT.png".format(x)
        cv2.imwrite(rightbinary, mask)
        binary = cv2.imread(rightbinary, cv2.IMREAD_GRAYSCALE)
        edges = cv2.Canny(binary, 1, 250)
        canny = "/home/opstrix/Desktop/bodymeasurement/temp/{}_Canny_RIGHT.jpg".format(x)
        cv2.imwrite(canny, edges)
        canny = cv2.imread(canny, cv2.IMREAD_GRAYSCALE)
        points = cv2.findNonZero(canny)
           
        right_shoulder = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * img.shape[1],
                          results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * img.shape[0])
        right_elbow = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].x * img.shape[1],
                      results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].y * img.shape[0])
        right_wrist = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x * img.shape[1],
                      results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * img.shape[0])
        left_hip = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x * img.shape[1],
                   results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * img.shape[0])
        right_hip = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x * img.shape[1],
                    results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y * img.shape[0])
        left_knee = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x * img.shape[1],
                    results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y * img.shape[0])
        right_knee = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].y * img.shape[0])
        left_ankle = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x * img.shape[1],
                        results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y * img.shape[0])
        right_ankle = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].x * img.shape[1],
                        results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].y * img.shape[0])

        #Height
        indices = np.where(binary > 200)
        y_min = np.min(indices[0])
        y_max = np.max(indices[0])
        height_pixels = y_max - y_min
        r_height = ((distance * 4.6 * height_pixels)/(3.04 * img.shape[1])) * 0.71
        print("Height", r_height)

        #Arm Length
        shoulder_elbow_pixels = math.sqrt((right_elbow[0] - right_shoulder[0]) ** 2  + (right_elbow[1] - right_shoulder[1]) ** 2)
        elbow_wrist_pixels = math.sqrt((right_wrist[0] - right_elbow[0]) ** 2  + (right_wrist[1] - right_elbow[1]) ** 2)
        r_arm_length = ((distance * 4.6 * (shoulder_elbow_pixels + elbow_wrist_pixels)/(3.04 * img.shape[1]))) * 0.71
        print("Arm Length:", r_arm_length)

        #Upper Arm Length
        r_upper_arm_length = ((distance * 4.6 * shoulder_elbow_pixels/(3.04 * img.shape[1]))) * 0.71
        print("Upper Arm Length:", r_upper_arm_length)
       
        #Hip Girth
        x = int(left_hip[0])
        y = int(left_hip[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:  
                    min_dist = dist
                    left_edge = p[0]
        x = int(right_hip[0])
        y = int(right_hip[1])
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        hip_girth_pixel = x - left_edge[0]
        r_hip_girth = ((distance * 4.6 * hip_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Hip Girth:", r_hip_girth)
       
        #Hip Height
        hip_height_pixel = y_max - right_hip[1]
        print(hip_height_pixel)
        r_hip_height = ((distance * 4.6 * hip_height_pixel)/(3.04 * img.shape[1])) * 0.71
        print("Hip Height:", r_hip_height)
       
        #Thigh Girth(RIGHT)
        x = int((right_knee[0] + right_hip[0])/2)
        y = int((right_knee[1] + right_hip[1])/2)
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        thigh_girth_pixel = x - left_edge[0]
        r_thigh_girth = ((distance * 4.6 * thigh_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Right Thigh Girth:", r_thigh_girth)
       
        #Knee Girth(RIGHT)
        x = int(right_knee[0])
        y = int(right_knee[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        knee_girth_pixel = x - left_edge[0]
        r_knee_girth = ((distance * 4.6 * knee_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Knee Girth:", r_knee_girth)
       
        #Knee Height
        knee_height_pixel = y_max - right_knee[1]
        r_knee_height = ((distance * 4.6 * knee_height_pixel)/(3.04 * img.shape[1])) * 0.71
        print("Knee Height:", r_knee_height)
       
        #Calf Girth(RIGHT)
        x = int((right_ankle[0] + right_knee[0])/2)
        y = int((right_ankle[1] + right_knee[1])/2)
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        calf_girth_pixel = x - left_edge[0]
        r_calf_girth = ((distance * 4.6 * calf_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Calf Girth:", r_calf_girth)
           
        #Ankle Girth(RIGHT)
        x = int(right_ankle[0])
        y = int(right_ankle[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        ankle_girth_pixel = x - left_edge[0]
        r_ankle_girth = ((distance * 4.6 * ankle_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Right Ankle Girth:", r_ankle_girth)

def MediapipeLeft(left, distance):
    global l_height, l_arm_length, l_upper_arm_length, l_hip_girth, l_hip_height, l_thigh_girth, l_knee_girth, l_knee_height, l_calf_girth, l_ankle_girth
    x = projid.get()
    distance = distance/2.54
    img = cv2.imread(left)
    with mp_pose.Pose(static_image_mode = True, min_detection_confidence=0.5, enable_segmentation = True) as pose:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img)

        mask = results.segmentation_mask.astype(float)
        mask = cv2.normalize(mask, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        leftbinary = "/home/opstrix/Desktop/bodymeasurement/temp/{}_BINARY_LEFT.png".format(x)
        cv2.imwrite(leftbinary, mask)
        binary = cv2.imread(leftbinary, cv2.IMREAD_GRAYSCALE)
        edges = cv2.Canny(binary, 1, 250)
        canny = "/home/opstrix/Desktop/bodymeasurement/temp/{}_Canny_LEFT.jpg".format(x)
        cv2.imwrite(canny, edges)
        canny = cv2.imread(canny, cv2.IMREAD_GRAYSCALE)
        points = cv2.findNonZero(canny)
           
        left_shoulder = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * img.shape[1],
                         results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * img.shape[0])                
        left_elbow = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].y * img.shape[0])
        left_wrist = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * img.shape[0])
        left_hip = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x * img.shape[1],
                   results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * img.shape[0])
        right_hip = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x * img.shape[1],
                    results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y * img.shape[0])
        left_knee = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x * img.shape[1],
                    results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y * img.shape[0])
        right_knee = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].y * img.shape[0])
        left_ankle = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x * img.shape[1],
                        results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y * img.shape[0])
        right_ankle = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].x * img.shape[1],
                        results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].y * img.shape[0])

        #Height
        indices = np.where(binary > 200)
        y_min = np.min(indices[0])
        y_max = np.max(indices[0])
        height_pixels = y_max - y_min
        l_height = ((distance * 4.6 * height_pixels)/(3.04 * img.shape[1])) * 0.71
        print("Height", l_height)

        #Arm Length
        shoulder_elbow_pixels = math.sqrt((left_elbow[0] - left_shoulder[0]) ** 2  + (left_elbow[1] - left_shoulder[1]) ** 2)
        elbow_wrist_pixels = math.sqrt((left_wrist[0] - left_elbow[0]) ** 2  + (left_wrist[1] - left_elbow[1]) ** 2)
        l_arm_length = ((distance * 4.6 * (shoulder_elbow_pixels + elbow_wrist_pixels)/(3.04 * img.shape[1]))) * 0.71
        print("Arm Length:", l_arm_length)

        #Upper Arm Length
        l_upper_arm_length = ((distance * 4.6 * shoulder_elbow_pixels/(3.04 * img.shape[1]))) * 0.71
        print("Upper Arm Length:", l_upper_arm_length)
       
        #Hip Girth
        x = int(left_hip[0])
        y = int(left_hip[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:  
                    min_dist = dist
                    left_edge = p[0]
        x = int(right_hip[0])
        y = int(right_hip[1])
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        hip_girth_pixel = x - left_edge[0]
        l_hip_girth = ((distance * 4.6 * hip_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Hip Girth:", l_hip_girth)

        #Hip Height
        hip_height_pixel = y_max - left_hip[1]
        print(hip_height_pixel)
        l_hip_height = ((distance * 4.6 * hip_height_pixel)/(3.04 * img.shape[1])) * 0.71
        print("Hip Height:", l_hip_height)
       
        #Thigh Girth(LEFT)
        x = int((left_knee[0] + left_hip[0])/2)
        y = int((left_knee[1] + left_hip[1])/2)
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        thigh_girth_pixel = x - left_edge[0]
        l_thigh_girth = ((distance * 4.6 * thigh_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Thigh Girth:", l_thigh_girth)
           
        #Knee Girth(LEFT)
        x = int(left_knee[0])
        y = int(left_knee[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        knee_girth_pixel = x - left_edge[0]
        l_knee_girth = ((distance * 4.6 * knee_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Knee Girth:", l_knee_girth)

        #Knee Height
        knee_height_pixel = y_max - left_knee[1]
        l_knee_height = ((distance * 4.6 * knee_height_pixel)/(3.04 * img.shape[1])) * 0.71
        print("Hip Height:", l_knee_height)
       
        #Calf Girth(LEFT)
        x = int((left_ankle[0] + left_knee[0])/2)
        y = int((left_ankle[1] + left_knee[1])/2)
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        calf_girth_pixel = x - left_edge[0]
        l_calf_girth = ((distance * 4.6 * calf_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Calf Girth:", l_calf_girth)
           
        #Ankle Girth(LEFT)
        x = int(left_ankle[0])
        y = int(left_ankle[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    left_edge = p[0]
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        ankle_girth_pixel = x - left_edge[0]
        l_ankle_girth = ((distance * 4.6 * ankle_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Ankle Girth:", l_ankle_girth)

def MediapipeBack(back, distance):
    global b_shoulder, b_rarm_length, b_upper_rarm_length, b_hip_girth
    x = projid.get()
    distance = distance/2.54
    img = cv2.imread(back)

    with mp_pose.Pose(static_image_mode = True, min_detection_confidence=0.5, enable_segmentation = True) as pose:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img)

        mask = results.segmentation_mask.astype(float)
        mask = cv2.normalize(mask, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        backbinary = "/home/opstrix/Desktop/bodymeasurement/temp/{}_BINARY_BACK.png".format(x)
        cv2.imwrite(backbinary, mask)
        binary = cv2.imread(backbinary, cv2.IMREAD_GRAYSCALE)
        edges = cv2.Canny(binary, 1, 250)
        canny = "/home/opstrix/Desktop/bodymeasurement/temp/{}_Canny_BACK.jpg".format(x)
        cv2.imwrite(canny, edges)
        canny = cv2.imread(canny, cv2.IMREAD_GRAYSCALE)
        points = cv2.findNonZero(canny)
           
        left_shoulder = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * img.shape[1],
                         results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * img.shape[0])                
        right_shoulder = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * img.shape[1],
                          results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * img.shape[0])
        left_elbow = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].y * img.shape[0])
        right_elbow = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].x * img.shape[1],
                      results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].y * img.shape[0])
        left_wrist = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * img.shape[0])
        right_wrist = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x * img.shape[1],
                      results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * img.shape[0])
        left_hip = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x * img.shape[1],
                   results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * img.shape[0])
        right_hip = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x * img.shape[1],
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].y * img.shape[0])

        #Shoulder Width
        shoulder_pixels = abs(left_shoulder[0] - right_shoulder[0])
        b_shoulder = ((distance * 4.6 * shoulder_pixels)/(3.04 * img.shape[0])) * 1.36
        print("Shoulder", b_shoulder)

        #Arm Length
        shoulder_elbow_pixels = math.sqrt((left_elbow[0] - left_shoulder[0]) ** 2  + (left_elbow[1] - left_shoulder[1]) ** 2)
        elbow_wrist_pixels = math.sqrt((left_wrist[0] - left_elbow[0]) ** 2  + (left_wrist[1] - left_elbow[1]) ** 2)
        b_rarm_length = ((distance * 4.6 * (shoulder_elbow_pixels + elbow_wrist_pixels)/(3.04 * img.shape[1]))) * 0.71
        print("Arm Length:", b_rarm_length)

        #Upper Arm Length
        b_upper_rarm_length = ((distance * 4.6 * shoulder_elbow_pixels/(3.04 * img.shape[1]))) * 0.71
        print("Upper Arm Length:", b_upper_rarm_length)
       
        #Hip Girth
        x = int(right_hip[0])
        y = int(right_hip[1])
        min_dist = float('inf')
        left_edge = None
        for p in points:
            if p[0][1] == y:
                dist = x - p[0][0]
                if dist > 0 and dist < min_dist:  
                    min_dist = dist
                    left_edge = p[0]
        x = int(left_hip[0])
        y = int(left_hip[1])
        width = canny.shape[1]
        while x < width:
            if canny[y, x] > 0:
                break
            x += 1
        hip_girth_pixel = x - left_edge[0]
        b_hip_girth = ((distance * 4.6 * hip_girth_pixel/(3.04 * img.shape[0]))) * 1.36
        print("Hip Girth:", b_hip_girth)
       
def FinalMeasure():
    global height, shoulder, arm_length, upper_arm_length, hip_girth, hip_height, thigh_girth, knee_girth, knee_height, calf_girth, ankle_girth
    x = projid.get()
    pi = math.pi
    height = round((r_height + l_height)/2, 2)
    shoulder = round((f_shoulder + b_shoulder)/2, 2)
    arm_length = round((r_arm_length + l_arm_length)/2, 2)
    upper_arm_length = round((r_upper_arm_length + l_upper_arm_length)/2, 2)

    a = int((f_hip_girth + b_hip_girth))
    b = int((r_hip_girth + l_hip_girth))
    hip_girth_formula = (pi * (a + b)) * (1 + 3 * (a - b)**2) / ((a - b)**2 * (10 + sqrt(4 - (3 * ((a - b)**2)) / (a + b)**2)))
    hip_girth = round(hip_girth_formula, 2)
   
    hip_height = round((r_hip_height + l_hip_height)/2, 2)

    a = int((f_rthigh_girth + f_lthigh_girth))
    b = int((r_thigh_girth + l_thigh_girth))
    thigh_girth = (pi * (a + b)) * (1 + 3 * (a - b)**2) / ((a - b)**2 * (10 + sqrt(4 - (3 * ((a - b)**2)) / (a + b)**2)))
    thigh_girth = round(thigh_girth, 2)
   
    a = int((f_rknee_girth + f_lknee_girth))
    b = int((r_knee_girth + l_knee_girth))
    knee_girth_formula = (pi * (a + b)) * (1 + 3 * (a - b)**2) / ((a - b)**2 * (10 + sqrt(4 - (3 * ((a - b)**2)) / (a + b)**2)))
    knee_girth = round(knee_girth_formula, 2)
   
    knee_height = round((r_knee_height + l_knee_height)/2, 2)

    a = int((f_rcalf_girth + f_lcalf_girth))
    b = int((r_calf_girth + l_calf_girth))
    calf_girth_formula = (pi * (a + b)) * (1 + 3 * (a - b)**2) / ((a - b)**2 * (10 + sqrt(4 - (3 * ((a - b)**2)) / (a + b)**2)))
    calf_girth = round(calf_girth_formula, 2)

    a = int((f_rankle_girth + f_lankle_girth))
    b = int((r_ankle_girth + l_ankle_girth))
    ankle_girth_formula = (pi * (a + b)) * (1 + 3 * (a - b)**2) / ((a - b)**2 * (10 + sqrt(4 - (3 * ((a - b)**2)) / (a + b)**2)))
    ankle_girth = round(ankle_girth_formula, 2)

    dbFunc()
    curr.execute("""INSERT INTO measurements VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (str(x),  str(height), str(shoulder), str(arm_length), str(upper_arm_length), str(hip_girth), str(hip_height), str(thigh_girth), str(knee_girth), str(knee_height), str(calf_girth), str(ankle_girth)))
    conn.commit()
    curr.close()
    conn.close()
   
def Result():
    global scrollbary, resultcanvas, result_frame
    FinalMeasure()
    #take_photo_frame.pack_forget()
    #upload_photo_frame.pack_forget()
    dbFunc()
    x = projid.get()
    photos = []
    info = []
    measurements = []
    curr.execute("""SELECT * FROM project WHERE projID = ?""", (x, ))
    fetch = curr.fetchall()
    for data in fetch[0]:
        info.append(data)
    curr.execute("""SELECT * FROM photos WHERE projID = ?""", (x, ))
    fetch = curr.fetchall()
    for data in fetch[0]:
        photos.append(data)
    curr.execute("""SELECT * FROM measurements WHERE projID = ?""", (x, ))
    fetch = curr.fetchall()
    for data in fetch[0]:
        measurements.append(data)
    curr.close()
    conn.close()
   
    front = photos[1]
    front = Image.open(front)
    front = front.resize((200,356), Image.Resampling.LANCZOS)
    front_photo = ImageTk.PhotoImage(front)
    right = photos[3]
    right = Image.open(right)
    right = right.resize((200,356), Image.Resampling.LANCZOS)
    right_photo = ImageTk.PhotoImage(right)
    left = photos[5]
    left = Image.open(left)
    left = left.resize((200,356), Image.Resampling.LANCZOS)
    left_photo = ImageTk.PhotoImage(left)
    back = photos[7]
    back = Image.open(back)
    back = back.resize((200,356), Image.Resampling.LANCZOS)
    back_photo = ImageTk.PhotoImage(back)

    scrollbary = Scrollbar(window, orient = VERTICAL)
    scrollbary.pack(side = RIGHT, fill = Y)

    resultcanvas = Canvas(window, yscrollcommand = scrollbary.set)
    resultcanvas.pack(side = TOP, fill = BOTH, expand = True)
    scrollbary.config(command = resultcanvas.yview)

    result_frame = Frame(resultcanvas, bg = '#FAC1D4')
    result_frame.pack(fill = BOTH)

    btn_mainmenu = Button(result_frame, text = " Main Menu", bg = '#FAC1D4', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_database, width = 350, height = 120, font = "Rockwell 18 bold", compound = LEFT, relief = FLAT, command = ResultBack)
    btn_mainmenu.pack(side = TOP, pady = 10, padx = 50)

    info_frame = Frame(result_frame, bg = '#FAC1D4')
    info_frame.pack(side = TOP, pady = 10, padx = 50, fill = X)

    measurements_frame = Frame(result_frame, bg = '#FAC1D4')
    measurements_frame.pack(side = TOP, pady = 10, padx = 50, fill = X)

    photos_frame = Frame(result_frame, bg = '#FAC1D4')
    photos_frame.pack(side = TOP, pady = 10, padx = 30, fill = X)

    lbl_projid = Label(info_frame, text = "Project ID: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_projid.grid(row = 2, sticky = W)
    lbl_custname = Label(info_frame, text = "Name: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_custname.grid(row = 3, sticky = W)
    lbl_cdate = Label(info_frame, text = "Date: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_cdate.grid(row = 4, sticky = W)
    lbl_ctime = Label(info_frame, text = "Time: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_ctime.grid(row = 5, sticky = W)
    lbl_cnotes = Label(info_frame, text = "Notes: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_cnotes.grid(row = 6, sticky = W)

    entry_projid = Label(info_frame, text = info[0], font = "Rockwell 20", bg = '#FAC1D4')
    entry_projid.grid(row = 2, column = 1, sticky = W)
    entry_custname = Label(info_frame, text = info[1], font = "Rockwell 20", bg = '#FAC1D4')
    entry_custname.grid(row = 3, column = 1, sticky = W)
    entry_cdate = Label(info_frame, text = info[2], font = "Rockwell 20", bg = '#FAC1D4')
    entry_cdate.grid(row = 4, column = 1, sticky = W)
    entry_ctime = Label(info_frame, text = info[3], font = "Rockwell 20", bg = '#FAC1D4')
    entry_ctime.grid(row = 5, column = 1, sticky = W)
    entry_cnotes = Label(info_frame, text = info[4], font = "Rockwell 20", bg = '#FAC1D4')
    entry_cnotes.grid(row = 6, column = 1, sticky = W)

    lbl_height = Label(measurements_frame, text = "Height: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_height.grid(row = 1, sticky = W)
    lbl_shoulder = Label(measurements_frame, text = "Shoulder: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_shoulder.grid(row = 2, sticky = W)
    lbl_arm_length = Label(measurements_frame, text = "Arm Length: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_arm_length.grid(row = 3, sticky = W)
    lbl_upper_arm_length = Label(measurements_frame, text = "Upper Arm Length: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_upper_arm_length.grid(row = 4, sticky = W)
    lbl_hip_girth = Label(measurements_frame, text = "Hip Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_hip_girth.grid(row = 5, sticky = W)
    lbl_hip_height = Label(measurements_frame, text = "Hip Height: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_hip_height.grid(row = 6, sticky = W)
    lbl_thigh_girth = Label(measurements_frame, text = "Thigh Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_thigh_girth.grid(row = 7, sticky = W)
    lbl_knee_girth = Label(measurements_frame, text = "Knee Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_knee_girth.grid(row = 8, sticky = W)
    lbl_knee_height = Label(measurements_frame, text = "Knee Height: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_knee_height.grid(row = 9, sticky = W)
    lbl_calf_girth = Label(measurements_frame, text = "Calf Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_calf_girth.grid(row = 10, sticky = W)
    lbl_ankle_girth = Label(measurements_frame, text = "Ankle Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
    lbl_ankle_girth.grid(row = 11, sticky = W)

    entry_height = Label(measurements_frame, text = measurements[1], font = "Rockwell 20", bg = '#FAC1D4')
    entry_height.grid(row = 1, column = 1, sticky = W)
    entry_shoulder = Label(measurements_frame, text = measurements[2], font = "Rockwell 20", bg = '#FAC1D4')
    entry_shoulder.grid(row = 2, column = 1, sticky = W)
    entry_arm_length = Label(measurements_frame, text = measurements[3], font = "Rockwell 20", bg = '#FAC1D4')
    entry_arm_length.grid(row = 3, column = 1, sticky = W)
    entry_upper_arm_length = Label(measurements_frame, text = measurements[4], font = "Rockwell 20", bg = '#FAC1D4')
    entry_upper_arm_length.grid(row = 4, column = 1, sticky = W)
    entry_hip_girth = Label(measurements_frame, text = measurements[5], font = "Rockwell 20", bg = '#FAC1D4')
    entry_hip_girth.grid(row = 5, column = 1, sticky = W)
    entry_hip_height = Label(measurements_frame, text = measurements[6], font = "Rockwell 20", bg = '#FAC1D4')
    entry_hip_height.grid(row = 6, column = 1, sticky = W)
    entry_thigh_girth = Label(measurements_frame, text = measurements[7], font = "Rockwell 20", bg = '#FAC1D4')
    entry_thigh_girth.grid(row = 7, column = 1, sticky = W)
    entry_knee_girth = Label(measurements_frame, text =  measurements[8], font = "Rockwell 20", bg = '#FAC1D4')
    entry_knee_girth.grid(row = 8, column = 1, sticky = W)
    entry_knee_height = Label(measurements_frame, text = measurements[9], font = "Rockwell 20", bg = '#FAC1D4')
    entry_knee_height.grid(row = 9, column = 1, sticky = W)
    entry_calf_girth = Label(measurements_frame, text = measurements[10], font = "Rockwell 20", bg = '#FAC1D4')
    entry_calf_girth.grid(row = 10, column = 1, sticky = W)
    entry_ankle_girth = Label(measurements_frame, text = measurements[11], font = "Rockwell 20", bg = '#FAC1D4')
    entry_ankle_girth.grid(row = 11, column = 1, sticky = W)

    cvs_v1 = Canvas(photos_frame, width = 200, height = 356)
    cvs_v1.grid(row = 1, column = 1, pady = 15, padx = 20)
    cvs_v2 = Canvas(photos_frame, width = 200, height = 356)
    cvs_v2.grid(row = 1, column = 2, pady = 15, padx = 20)
    cvs_v3 = Canvas(photos_frame, width = 200, height = 356)
    cvs_v3.grid(row = 1, column = 3, pady = 15, padx = 20)
    cvs_v4 = Canvas(photos_frame, width = 200, height = 356)
    cvs_v4.grid(row = 1, column = 4, pady = 15, padx = 20)
    v1_distance = Label(photos_frame, text = photos[2], font = "Rockwell 20", bg = '#FAC1D4')
    v1_distance.grid(row = 2, column = 1, pady = 15, padx = 20)
    v2_distance = Label(photos_frame, text = photos[4], font = "Rockwell 20", bg = '#FAC1D4')
    v2_distance.grid(row = 2, column = 2, pady = 15, padx = 20)
    v3_distance = Label(photos_frame, text = photos[6], font = "Rockwell 20", bg = '#FAC1D4')
    v3_distance.grid(row = 2, column = 3, pady = 15, padx = 20)
    v4_distance = Label(photos_frame, text = photos[8], font = "Rockwell 20", bg = '#FAC1D4')
    v4_distance.grid(row = 2, column = 4, pady = 15, padx = 20)

    try:
        cvs_v1.create_image(0, 0, anchor = NW, image =  front_photo)
        cvs_v1.itemconfig(image_container, image = front_photo)
    except:
        pass
    try:
        cvs_v2.create_image(0, 0, anchor = NW, image =  rightt_photo)
        cvs_v2.itemconfig(image_container, image = right_photo)
    except:
        pass
    try:
        cvs_v3.create_image(0, 0, anchor = NW, image =  left_photo)
        cvs_v3.itemconfig(image_container, image = left_photo)
    except:
        pass
    try:
        cvs_v4.create_image(0, 0, anchor = NW, image =  back_photo)
        cvs_v4.itemconfig(image_container, image = back_photo)
    except:
        pass

    resultcanvas.create_window((0,0), window = result_frame, anchor = NW)
    result_frame.bind("<Configure>", lambda event: resultcanvas.configure(scrollregion = resultcanvas.bbox("all")))

def ResultBack():
    scrollbary.pack_forget()
    resultcanvas.pack_forget()
    result_frame.pack_forget()
    main_frame.pack(pady = 50)
           
########################################DATABASE#################################
def DataBase():
    global database_frame, db_tree
    main_frame.pack_forget()
    database_frame = Frame(window, bg = '#FAC1D4')
    database_frame.pack()
    db_top_frame = Frame(database_frame, width = 600, bg = '#FAC1D4', relief = GROOVE, bd = 1)
    db_top_frame.pack(side = TOP, fill = X)
    db_left_frame = Frame(database_frame, width = 600, bg = '#D38CA1', relief = GROOVE, bd = 1)
    db_left_frame.pack(side = LEFT, fill = Y)
    tree_frame = Frame(database_frame, width = 600, bg = '#FAC1D4')
    tree_frame.pack(side = RIGHT)

    search_entry = Entry(db_top_frame, textvariable = db_search, width = 30)
    search_entry.pack(side = RIGHT, padx = 10, pady = 10, fill = X)
    btn_search = Button(db_top_frame, text = "Search", bg = '#D38CA1', relief = FLAT, overrelief = SUNKEN, width = 15, font = ('Consolas', 15), command = DbSearch)
    btn_search.pack(side = RIGHT, padx = 10, pady = 10, fill = X)
    btn_refresh = Button(db_left_frame, text = "Refresh", bg = '#FAC1D4', relief = FLAT, overrelief = SUNKEN, width = 15, font = ('Consolas', 15), command = DbRefresh)
    btn_refresh.pack(side = TOP, padx = 10, pady = 10, fill = X)
    btn_select = Button(db_left_frame, text = "Select", bg = '#FAC1D4', relief = FLAT, overrelief = SUNKEN, width = 15, font = ('Consolas', 15), command = DbSelect)
    btn_select.pack(side = TOP, padx = 10, pady = 10, fill = X)
    btn_back = Button(db_left_frame, text = "Back", bg = '#FAC1D4', relief = FLAT, overrelief = SUNKEN, width = 15, font = ('Consolas', 15), command = DatabaseBackMain)
    btn_back.pack(side = TOP, padx = 10, pady = 10, fill = X)

    db_scrollbarx = Scrollbar(tree_frame, orient = HORIZONTAL)
    db_scrollbary = Scrollbar(tree_frame, orient = VERTICAL)
    db_tree = ttk.Treeview(tree_frame, columns = ('ProjectID', 'CustName', 'Date','Time', 'Notes', 'Type'), selectmode = "extended", height = 100, yscrollcommand = db_scrollbary.set, xscrollcommand = db_scrollbarx.set)
    db_scrollbary.config(command = db_tree.yview)
    db_scrollbary.pack(side = RIGHT, fill = Y)
    db_scrollbarx.config(command = db_tree.xview)
    db_scrollbarx.pack(side = BOTTOM, fill = X)
    db_tree.heading('ProjectID', text = "Project ID", anchor = W)
    db_tree.heading('CustName', text = "Customer Name", anchor = W)
    db_tree.heading('Date', text = "Date", anchor = W)
    db_tree.heading('Time', text = "Time",anchor = W)
    db_tree.heading('Notes', text = "Notes", anchor = W)
    db_tree.heading('Type', text = "Type", anchor = W)
    db_tree.column('#0', stretch = NO, minwidth = 0, width = 0)
    db_tree.column('#1', width = 120)
    db_tree.column('#2', width = 200)
    db_tree.column('#3', width = 130)
    db_tree.column('#4', width = 130)
    db_tree.column('#5', width = 250)
    db_tree.column('#6', width = 120)
    db_tree.pack()
    DbDisplay()

def DatabaseBackMain():
    database_frame.pack_forget()
    main_frame.pack(pady = 60)

def DbDisplay():
    dbFunc()
    curr.execute("""SELECT * FROM project ORDER BY projID""")
    fetch = curr.fetchall()
    for data in fetch:
        db_tree.insert('', 'end', values=(data))
    curr.close()
    conn.close()

def DbSearch():
    if db_search.get() != "":
        db_tree.delete(*db_tree.get_children())
        dbFunc()
        curr.execute("""SELECT * FROM project WHERE projID LIKE ? or custName LIKE ? or cDate LIKE ? or cTime LIKE ? or notes LIKE ? or type LIKE ?""", (str(db_search.get()), str(db_search.get()), str(db_search.get()), str(db_search.get()), str(db_search.get()),))
        fetch = curr.fetchall()
        for data in fetch:
            db_tree.insert('', 'end', values=(data))
        curr.close()
        conn.close()

def DbRefresh():
    db_tree.delete(*db_tree.get_children())
    DbDisplay()
    db_search.set("")
   
def DbSelect():
    global scrollbary, resultcanvas, result_frame
    if not db_tree.selection():
       print("ERROR")
       return
    else:
        db_tree
        curItem = db_tree.focus()
        contents =(db_tree.item(curItem))
        selecteditem = contents['values']
        dbFunc()
        x = selecteditem[0]
        photos = []
        info = []
        measurements = []
        curr.execute("""SELECT * FROM project WHERE projID = ?""", (x, ))
        fetch = curr.fetchall()
        for data in fetch[0]:
            info.append(data)
        curr.execute("""SELECT * FROM photos WHERE projID = ?""", (x, ))
        fetch = curr.fetchall()
        for data in fetch[0]:
            photos.append(data)
        curr.execute("""SELECT * FROM measurements WHERE projID = ?""", (x, ))
        fetch = curr.fetchall()
        for data in fetch[0]:
            measurements.append(data)
        curr.close()
        conn.close()
       
        front = photos[1]
        front = Image.open(front)
        front = front.resize((200,356), Image.Resampling.LANCZOS)
        front_photo = ImageTk.PhotoImage(front)
        right = photos[3]
        right = Image.open(right)
        right = right.resize((200,356), Image.Resampling.LANCZOS)
        right_photo = ImageTk.PhotoImage(right)
        left = photos[5]
        left = Image.open(left)
        left = left.resize((200,356), Image.Resampling.LANCZOS)
        left_photo = ImageTk.PhotoImage(left)
        back = photos[7]
        back = Image.open(back)
        back = back.resize((200,356), Image.Resampling.LANCZOS)
        back_photo = ImageTk.PhotoImage(back)

        database_frame.pack_forget()
        scrollbary = Scrollbar(window, orient = VERTICAL)
        scrollbary.pack(side = RIGHT, fill = Y)

        resultcanvas = Canvas(window, yscrollcommand = scrollbary.set)
        resultcanvas.pack(side = TOP, fill = BOTH, expand = True)
        scrollbary.config(command = resultcanvas.yview)

        result_frame = Frame(resultcanvas, bg = '#FAC1D4')
        result_frame.pack(fill = BOTH)

        btn_mainmenu = Button(result_frame, text = " Main Menu", bg = '#FAC1D4', fg = '#FFFFFF', activebackground = '#FFDCE7', bd = 0, image = pic_database, width = 350, height = 120, font = "Rockwell 18 bold", compound = LEFT, relief = FLAT, command = DbBack)
        btn_mainmenu.pack(side = TOP, pady = 10, padx = 50)

        info_frame = Frame(result_frame, bg = '#FAC1D4')
        info_frame.pack(side = TOP, pady = 10, padx = 50, fill = X)

        measurements_frame = Frame(result_frame, bg = '#FAC1D4')
        measurements_frame.pack(side = TOP, pady = 10, padx = 50, fill = X)

        photos_frame = Frame(result_frame, bg = '#FAC1D4')
        photos_frame.pack(side = TOP, pady = 10, padx = 30, fill = X)

        lbl_projid = Label(info_frame, text = "Project ID: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_projid.grid(row = 2, sticky = W)
        lbl_custname = Label(info_frame, text = "Name: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_custname.grid(row = 3, sticky = W)
        lbl_cdate = Label(info_frame, text = "Date: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_cdate.grid(row = 4, sticky = W)
        lbl_ctime = Label(info_frame, text = "Time: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_ctime.grid(row = 5, sticky = W)
        lbl_cnotes = Label(info_frame, text = "Notes: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_cnotes.grid(row = 6, sticky = W)

        entry_projid = Label(info_frame, text = info[0], font = "Rockwell 20", bg = '#FAC1D4')
        entry_projid.grid(row = 2, column = 1, sticky = W)
        entry_custname = Label(info_frame, text = info[1], font = "Rockwell 20", bg = '#FAC1D4')
        entry_custname.grid(row = 3, column = 1, sticky = W)
        entry_cdate = Label(info_frame, text = info[2], font = "Rockwell 20", bg = '#FAC1D4')
        entry_cdate.grid(row = 4, column = 1, sticky = W)
        entry_ctime = Label(info_frame, text = info[3], font = "Rockwell 20", bg = '#FAC1D4')
        entry_ctime.grid(row = 5, column = 1, sticky = W)
        entry_cnotes = Label(info_frame, text = info[4], font = "Rockwell 20", bg = '#FAC1D4')
        entry_cnotes.grid(row = 6, column = 1, sticky = W)

        lbl_height = Label(measurements_frame, text = "Height: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_height.grid(row = 1, sticky = W)
        lbl_shoulder = Label(measurements_frame, text = "Shoulder: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_shoulder.grid(row = 2, sticky = W)
        lbl_arm_length = Label(measurements_frame, text = "Arm Length: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_arm_length.grid(row = 3, sticky = W)
        lbl_upper_arm_length = Label(measurements_frame, text = "Upper Arm Length: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_upper_arm_length.grid(row = 4, sticky = W)
        lbl_hip_girth = Label(measurements_frame, text = "Hip Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_hip_girth.grid(row = 5, sticky = W)
        lbl_hip_height = Label(measurements_frame, text = "Hip Height: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_hip_height.grid(row = 6, sticky = W)
        lbl_thigh_girth = Label(measurements_frame, text = "Thigh Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_thigh_girth.grid(row = 7, sticky = W)
        lbl_knee_girth = Label(measurements_frame, text = "Knee Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_knee_girth.grid(row = 8, sticky = W)
        lbl_knee_height = Label(measurements_frame, text = "Knee Height: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_knee_height.grid(row = 9, sticky = W)
        lbl_calf_girth = Label(measurements_frame, text = "Calf Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_calf_girth.grid(row = 10, sticky = W)
        lbl_ankle_girth = Label(measurements_frame, text = "Ankle Girth: ", font = "Rockwell 20", bg = '#FAC1D4')
        lbl_ankle_girth.grid(row = 11, sticky = W)

        entry_height = Label(measurements_frame, text = measurements[1], font = "Rockwell 20", bg = '#FAC1D4')
        entry_height.grid(row = 1, column = 1, sticky = W)
        entry_shoulder = Label(measurements_frame, text = measurements[2], font = "Rockwell 20", bg = '#FAC1D4')
        entry_shoulder.grid(row = 2, column = 1, sticky = W)
        entry_arm_length = Label(measurements_frame, text = measurements[3], font = "Rockwell 20", bg = '#FAC1D4')
        entry_arm_length.grid(row = 3, column = 1, sticky = W)
        entry_upper_arm_length = Label(measurements_frame, text = measurements[4], font = "Rockwell 20", bg = '#FAC1D4')
        entry_upper_arm_length.grid(row = 4, column = 1, sticky = W)
        entry_hip_girth = Label(measurements_frame, text = measurements[5], font = "Rockwell 20", bg = '#FAC1D4')
        entry_hip_girth.grid(row = 5, column = 1, sticky = W)
        entry_hip_height = Label(measurements_frame, text = measurements[6], font = "Rockwell 20", bg = '#FAC1D4')
        entry_hip_height.grid(row = 6, column = 1, sticky = W)
        entry_thigh_girth = Label(measurements_frame, text = measurements[7], font = "Rockwell 20", bg = '#FAC1D4')
        entry_thigh_girth.grid(row = 7, column = 1, sticky = W)
        entry_knee_girth = Label(measurements_frame, text =  measurements[8], font = "Rockwell 20", bg = '#FAC1D4')
        entry_knee_girth.grid(row = 8, column = 1, sticky = W)
        entry_knee_height = Label(measurements_frame, text = measurements[9], font = "Rockwell 20", bg = '#FAC1D4')
        entry_knee_height.grid(row = 9, column = 1, sticky = W)
        entry_calf_girth = Label(measurements_frame, text = measurements[10], font = "Rockwell 20", bg = '#FAC1D4')
        entry_calf_girth.grid(row = 10, column = 1, sticky = W)
        entry_ankle_girth = Label(measurements_frame, text = measurements[11], font = "Rockwell 20", bg = '#FAC1D4')
        entry_ankle_girth.grid(row = 11, column = 1, sticky = W)

        cvs_v1 = Canvas(photos_frame, width = 200, height = 356)
        cvs_v1.grid(row = 1, column = 1, pady = 15, padx = 20)
        cvs_v2 = Canvas(photos_frame, width = 200, height = 356)
        cvs_v2.grid(row = 1, column = 2, pady = 15, padx = 20)
        cvs_v3 = Canvas(photos_frame, width = 200, height = 356)
        cvs_v3.grid(row = 1, column = 3, pady = 15, padx = 20)
        cvs_v4 = Canvas(photos_frame, width = 200, height = 356)
        cvs_v4.grid(row = 1, column = 4, pady = 15, padx = 20)
        v1_distance = Label(photos_frame, text = photos[2], font = "Rockwell 20", bg = '#FAC1D4')
        v1_distance.grid(row = 2, column = 1, pady = 15, padx = 20)
        v2_distance = Label(photos_frame, text = photos[4], font = "Rockwell 20", bg = '#FAC1D4')
        v2_distance.grid(row = 2, column = 2, pady = 15, padx = 20)
        v3_distance = Label(photos_frame, text = photos[6], font = "Rockwell 20", bg = '#FAC1D4')
        v3_distance.grid(row = 2, column = 3, pady = 15, padx = 20)
        v4_distance = Label(photos_frame, text = photos[8], font = "Rockwell 20", bg = '#FAC1D4')
        v4_distance.grid(row = 2, column = 4, pady = 15, padx = 20)


        try:
            cvs_v1.create_image(0, 0, anchor = NW, image =  front_photo)
            cvs_v1.itemconfig(image_container, image = front_photo)
        except:
            pass
        try:
            cvs_v2.create_image(0, 0, anchor = NW, image =  rightt_photo)
            cvs_v2.itemconfig(image_container, image = right_photo)
        except:
            pass
        try:
            cvs_v3.create_image(0, 0, anchor = NW, image =  left_photo)
            cvs_v3.itemconfig(image_container, image = left_photo)
        except:
            pass
        try:
            cvs_v4.create_image(0, 0, anchor = NW, image =  back_photo)
            cvs_v4.itemconfig(image_container, image = back_photo)
        except:
            pass

        resultcanvas.create_window((0,0), window = result_frame, anchor = NW)
        result_frame.bind("<Configure>", lambda event: resultcanvas.configure(scrollregion = resultcanvas.bbox("all")))

def DbBack():
    scrollbary.pack_forget()
    resultcanvas.pack_forget()
    result_frame.pack_forget()
    database_frame.pack()
   
MainMenu()
cv2.waitKey(0)
