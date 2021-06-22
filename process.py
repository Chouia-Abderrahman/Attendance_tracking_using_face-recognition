import os
from PyQt5 import QtWidgets
from bruh_ui import Ui_MainWindow
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timedelta
import pymysql
import cv2
import numpy as np
import face_recognition
import csv
from PyQt5.QtWidgets import QMessageBox

conn = pymysql.connect(host="localhost", user="root", passwd="", database="bruh")
path = 'pictures'
images = []
class_ids = []
camera_status = True
mylist = []
exporting_cursor = None

def show_message_box():
    msg = QMessageBox()
    msg.setWindowTitle("Success")
    msg.setText("Exported Successfully")
    msg.setIcon(QMessageBox.Information)
    x = msg.exec_()

def writing_attendance_for_recognized_face(self,name):
    chantie = self.chantie_text.text()
    today = str(datetime.now()).split(" ", 1)
    tomorrow = str(datetime.now() + timedelta(days=1)).split(" ", 1)
    cursor = conn.cursor()
    query = "select * from attendance where Nom_et_prenom ='" + name + "' and date_and_time > '" + today[
        0] + "' and date_and_time < '" + tomorrow[0] + "'"
    if cursor.execute(query) == 0:
        cursor.execute("INSERT INTO attendance (Nom_et_prenom,in_out,endroit) VALUES ('" + name + "','entered','"+chantie+"');")
        conn.commit()
    else:
        today_datetime_before_5 = datetime.now() - timedelta(minutes=5)
        cursor = conn.cursor()
        cursor.execute("select max(date_and_time),in_out from attendance where nom_et_prenom ='" + name + "'")
        result = cursor.fetchall()
        if today_datetime_before_5 < result[0][0]:
            print("he got in or out less than 5 minutes ago")
        else:
            cursor.execute(
                "select in_out from attendance where nom_et_prenom ='" + name + "' and date_and_time ='" + str(
                    result[0][0]) + "'")
            result = cursor.fetchall()
            # print(result[0][0])
            if (str(result[0][0]) == "entered"):
                cursor.execute("INSERT INTO attendance (Nom_et_prenom,in_out,endroit) VALUES ('" + name + "','exited','"+chantie+"');")
                conn.commit()
            else:
                cursor.execute("INSERT INTO attendance (Nom_et_prenom,in_out,endroit) VALUES ('" + name + "','entered','"+chantie+"');")
                conn.commit()


def export_attendance_to_csv():
    if (exporting_cursor is not None):
        fileVariable = open('Attendance.csv', 'r+')
        fileVariable.truncate(0)
        fileVariable.close()
        with open('Attendance.csv', 'r+') as f:
            f.writelines(f'{"Id,Nom et prenom,Date and Time,Enter/Exit,Chantier"}\n')
            for row in exporting_cursor:
                stringinput = str(row[0]) + "," + str(row[1]) + "," + str(row[2]) + "," + str(row[3]) + "," + str(
                    row[4])
                f.writelines(f'{stringinput}\n')
        show_message_box()


def find_encodings(imagess):
    encoded_list = []
    for img in imagess:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encoded_list.append(encode)
    return encoded_list

def camera_initiation(self):
    global mylist
    mylist = os.listdir(path)
    class_ids.clear()
    images.clear()
    for cl in mylist:
        current_image = cv2.imread(f'{path}/{cl}')
        images.append(current_image)
        class_ids.append(os.path.splitext(cl)[0])
    # print(class_ids)
    encoded_list_known = find_encodings(images)
    self.face_nbr_encoded.setText(str(len(encoded_list_known)) + " faces encoded")
    self.encoding_status.setText("Encoding Complete")
    cap = cv2.VideoCapture(0)
    while True:
        if cv2.waitKey(1) == ord('q'):
            break
        success, img = cap.read()
        img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        # img_small = cv2.resize(img, (0, 0), None, 1,1 )
        img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
        # face_Locations_current_frame is facescurrfram
        face_Locations_current_frame = face_recognition.face_locations(img_small)
        encode_current_frame = face_recognition.face_encodings(img_small, face_Locations_current_frame)

        for encodeFace, face_Loc in zip(encode_current_frame, face_Locations_current_frame):
            matches = face_recognition.compare_faces(encoded_list_known, encodeFace, 0.5)
            faceDis = face_recognition.face_distance(encoded_list_known, encodeFace)
            print(faceDis)
            matchIndex = np.argmin(faceDis)
            if cv2.waitKey(1) == ord('q'):
                break

            if matches[matchIndex]:
                name = class_ids[matchIndex].upper()
                cv2.waitKey(1)
                if cv2.waitKey(1) == ord('q'):
                    break
                y1, x2, y2, x1 = face_Loc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
                writing_attendance_for_recognized_face(self,name)
            else:
                cv2.waitKey(1)
                y1, x2, y2, x1 = face_Loc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
                cv2.putText(img, "UNKNOWN", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Camera', img)
    self.encoding_status.setText("")
    self.face_nbr_encoded.setText("")
    cap.release()
    cv2.destroyAllWindows()


def timeConversion(s):
    if "PM" in s:
        s = s.replace("PM", " ")
        t = s.split(":")
        if t[0] != '12':
            t[0] = str(int(t[0]) + 12)
            s = (":").join(t)
        return s
    else:
        s = s.replace("AM", " ")
        t = s.split(":")
        if t[0] == '12':
            t[0] = '00'
            s = (":").join(t)
        return s.strip()


def displaying_cursor_in_table(self, cursor):
    self.attendance_table_display.setRowCount(0)
    for row_number, row_data in enumerate(cursor):
        self.attendance_table_display.insertRow(row_number)
        for column_number, data in enumerate(row_data):
            self.attendance_table_display.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))


class windows(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        cursor = conn.cursor()
        #       cursor.execute('''CREATE TABLE IF NOT EXISTS `attendance` (
        # `ID` int(11) NOT NULL AUTO_INCREMENT,
        # `Nom_et_prenom` varchar(50) NOT NULL,
        # `date_and_time` datetime NOT NULL DEFAULT current_timestamp(),
        # `Endroit` varchar(50) DEFAULT NULL,
        # PRIMARY KEY (`ID`)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS `attendance` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Nom_et_prenom` varchar(50) NOT NULL,
  `date_and_time` datetime NOT NULL DEFAULT current_timestamp(),
  `in_out` varchar(50) NOT NULL,
  `Endroit` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=180 DEFAULT CHARSET=utf8mb4
''')
        conn.commit()

        self.browse_for_folder_button.clicked.connect(self.browse_for_folder_function)
        # self.Enter_values_button.clicked.connect(self.enter_values_function)
        self.display_all_attendances_btn.clicked.connect(self.display_all)
        self.search_attendances_btn.clicked.connect(self.display_search)
        self.attendance_table_display.setColumnWidth(0, 50)
        self.attendance_table_display.setColumnWidth(1, 200)
        self.attendance_table_display.setColumnWidth(2, 200)
        self.attendance_table_display.setColumnWidth(3, 150)
        self.attendance_table_display.setColumnWidth(4, 150)
        self.start_button.clicked.connect(lambda: camera_initiation(self))
        self.export_csv_btn.clicked.connect(export_attendance_to_csv)
        self.export_hours_csv_btn.clicked.connect(self.calculating_hours_worked_for_everyone)


    def calculating_hours_worked_for_everyone(self):
        global mylist
        the_pay_list=[]
        mylist = os.listdir(path)
        cursor = conn.cursor()
        the_before_time_textbox = self.before_timedate_edit.text()
        the_after_time_textbox = self.after_timedate_edit.text()
        the_before_time_textbox = self.before_timedate_edit.text().split(" ", 1)
        the_after_time_textbox = self.after_timedate_edit.text().split(" ", 1)
        before_time = timeConversion(the_before_time_textbox[1])
        after_time = timeConversion(the_after_time_textbox[1])
        the_before_date = datetime.strptime(the_before_time_textbox[0], "%d/%m/%Y")
        the_after_date = datetime.strptime(the_after_time_textbox[0], "%d/%m/%Y")
        before = the_before_date
        g = []
        for cl in mylist:
            g.append(os.path.splitext(cl)[0])
        for person in g:
            worked_hours = timedelta(0)
            the_before_date = before
            while (the_before_date < the_after_date):
                only_date = the_before_date.strftime("%Y-%m-%d")
                the_before_date = the_before_date + timedelta(days=1)
                only_date_2 = the_before_date.strftime("%Y-%m-%d")
                query = "select date_and_time,in_out from attendance where date_and_time >='" + only_date + \
                        "' and date_and_time < '" + only_date_2 + "' and nom_et_prenom ='" + person + "'"
                lines_returned = cursor.execute(query)
                result = cursor.fetchall()

                if (lines_returned != 0):
                    i = 0
                    mul_of_2 = len(result)
                    if (len(result) % 2 != 0):
                        if (result[len(result)-1][1] == 'entered'):
                            mul_of_2 = len(result)-1
                    while (i < mul_of_2):
                        worked_hours = worked_hours + (result[i + 1][0] - result[i][0])
                        i = i + 2
            var = person+","+str(worked_hours)
            the_pay_list.append(var)
        with open('Hours worked.csv', 'r+') as f:
            f.writelines(f'{"Nom et prenom,Hours Worked"}\n')
            for ro in the_pay_list:
                f.writelines(f'{ro}\n')
        show_message_box()

    def display_search(self):
        global exporting_cursor
        cursor = conn.cursor()
        the_before_time_textbox = self.before_timedate_edit.text()
        the_after_time_textbox = self.after_timedate_edit.text()

        the_before_time_textbox = self.before_timedate_edit.text().split(" ", 1)
        the_after_time_textbox = self.after_timedate_edit.text().split(" ", 1)
        before_time = timeConversion(the_before_time_textbox[1])
        after_time = timeConversion(the_after_time_textbox[1])
        the_before_date = datetime.strptime(the_before_time_textbox[0], "%d/%m/%Y").strftime("%Y-%m-%d")
        the_after_date = datetime.strptime(the_after_time_textbox[0], "%d/%m/%Y").strftime("%Y-%m-%d")
        before = the_before_date + " " + before_time + ":00"
        print(before)
        after = the_after_date + " " + after_time + ":00"
        query = "select * from attendance where date_and_time >= '" + before + "'and attendance.date_and_time <= '" + after + "'"
        cursor.execute(query)
        result = cursor.fetchall()
        exporting_cursor = result
        displaying_cursor_in_table(self, result)

    def display_all(self):
        global exporting_cursor
        cursor = conn.cursor()
        cursor.execute("select * from attendance")
        result = cursor.fetchall()
        exporting_cursor = result
        displaying_cursor_in_table(self, result)

    def browse_for_folder_function(self):
        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askdirectory()
        self.the_folder_textedit.setText(filename)
        global path
        path = filename
