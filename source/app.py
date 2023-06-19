import sys
import threading
# pip install pyqt5
from PyQt5 import QtCore,QtGui,QtSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog,QMessageBox
from gui import Ui_MainWindow
from imageProcessing import *
import time



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.img_filename = ''
        self.studentslist_filename = ''
        self.answers_filename = ''
        self.score = 0
        self.student_name =''
        self.student_id =0
        self.exam_id = 0 
        self.img_process = None
        self.img_display_thread = None
        self.answer_sheet_1 = None
        self.answer_sheet_2 = None
        self.img_quality = True
        self.imageProcess = imageProcessing()
        self.uic.setupUi(self)
        for info in QtSerialPort.QSerialPortInfo.availablePorts():
            self.uic.comselect.addItem(info.portName())
        for baudrate in QtSerialPort.QSerialPortInfo.standardBaudRates():
            self.uic.baudselect.addItem(str(baudrate), baudrate)
        self.serial = QtSerialPort.QSerialPort(
            self,
            readyRead=self.receive
        )
        self.uic.open_img_file.clicked.connect(self.openFileNameDialog)
        self.uic.open_answers_file.clicked.connect(self.openFileNameDialog)
        self.uic.open_studentslist_file.clicked.connect(self.openFileNameDialog)
        self.uic.run_processing.clicked.connect(self.startImageProcessing)
        self.uic.connectBtn.clicked.connect(self.connectComport)
        self.uic.runBtn.clicked.connect(self.sendData2Comport)
        self.uic.isUseCamera.clicked.connect(self.useCam)
        self.uic.camtestBtn.clicked.connect(self.testCam)
        #self.startImageDisplay()
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            if self.sender().text() == 'Chọn ảnh':
                self.uic.img_file.setText(fileName)
                self.img_filename = fileName 
                print('Chọn file ảnh :',self.img_filename)
                self.image = cv2.imread(self.img_filename)
                #self.image = cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                self.image1 = QtGui.QImage(self.image.data, self.image.shape[1], self.image.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
                self.uic.origin_img_label.setPixmap(QtGui.QPixmap.fromImage(self.image1))
                self.get_children_img_in_parent_img()
            elif self.sender().text() == 'Chọn đáp án':
                self.uic.answers_file.setText(fileName)
                self.answers_filename = fileName
                print('Chọn file đáp án :',self.answers_filename)
              
            elif self.sender().text() == 'Chọn danh sách sv':
                self.uic.studentlist_file.setText(fileName)
                self.studentslist_filename = fileName
                print('Chọn file danh sách sv :',self.studentslist_filename)
                
            #print(fileName)
    def useCam(self):
        if self.uic.isUseCamera.isChecked():
            self.uic.open_img_file.setEnabled(False)
            self.uic.img_file.setEnabled(False)
        else:
            self.uic.open_img_file.setEnabled(True)
            self.uic.img_file.setEnabled(True)

    def testCam(self):
        self.cap = cv2.VideoCapture(1+cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        ret,frame = self.cap.read() 
        while(ret):
            ret,frame = self.cap.read()    
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            cv2.imshow("Camera test ",frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): #Nhấn q để tắt
                #cv2.imwrite('origin_img.jpg',frame)
                break
        cv2.destroyAllWindows()

    #làm phẳng ảnh và tách các ảnh con từ ảnh ban đầu
    def get_children_img_in_parent_img(self):
        
        #self.image = cv2.imread(self.img_filename)
        h,w = self.image.shape[:2]
        print("Origin image size : ",h,w)
        self.img_quality = True
        if h < 550 and w <400 :
            self.uic.program_status.setText('Ảnh không đúng kích cỡ')
            self.img_quality = False
            

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        if self.img_quality:
            try:
                #ảnh mới sau khi đã được chỉnh
                self.image = self.imageProcess.warping_image(gray)
                h,w = self.image.shape[:2]
                print("Warped image size : ",h,w)
                #nếu ảnh đầu vào k đạt chuẩn
                if h < 500 and w <350 :
                    self.uic.program_status.setText('Ảnh không đúng kích cỡ')
                    self.img_quality = False
                self.uic.program_status.setText('')
            except:
                print("Không thể căn chỉnh ảnh!")
                self.img_quality = False
                if self.uic.connectBtn.text() == 'Disconnect':
                    self.serial.write('Start\n'.encode())
        if self.img_quality : 
            self.image = cv2.resize(self.image, (FRAME_SIZE_WIDTH,FRAME_SIZE_HEIGHT), interpolation=cv2.INTER_AREA)
            #print(self.image.shape[:2])
            self.answer_sheet_1 = self.image[ANSWER_SHEET_1_LOCATION[0][0]:ANSWER_SHEET_1_LOCATION[0][1],ANSWER_SHEET_1_LOCATION[1][0]:ANSWER_SHEET_1_LOCATION[1][1]]
            self.answer_sheet_2 = self.image[ANSWER_SHEET_2_LOCATION[0][0]:ANSWER_SHEET_2_LOCATION[0][1],ANSWER_SHEET_2_LOCATION[1][0]:ANSWER_SHEET_2_LOCATION[1][1]]
            self.student_id_sheet =self.image[STUDENT_ID_LOCATION[0][0]:STUDENT_ID_LOCATION[0][1],STUDENT_ID_LOCATION[1][0]:STUDENT_ID_LOCATION[1][1]]
            self.st_id_sheet_tmp = self.student_id_sheet.copy()
            self.exam_id_sheet = self.image[EXAM_ID_LOCATION[0][0]:EXAM_ID_LOCATION[0][1],EXAM_ID_LOCATION[1][0]:EXAM_ID_LOCATION[1][1]]
            self.ex_id_sheet_tmp = self.exam_id_sheet # biến này để fix lỗi biến dạng
        
            #thay đổi kích cỡ thành các kích cỡ chẵn
            answer_height,answer_width = self.answer_sheet_1.shape[:2]
            print(self.answer_sheet_1.shape[:2])
            new_answer_height = (math.ceil(answer_height // NUM_ROW_OF_QUESTIONS_EACH_COLLUMN +1)* NUM_ROW_OF_QUESTIONS_EACH_COLLUMN)
            new_answer_width = (math.ceil(answer_width // NUW_COLUMN_OF_ANSWER )* NUW_COLUMN_OF_ANSWER)
            self.answer_sheet_1 = cv2.resize(self.answer_sheet_1, (new_answer_width,new_answer_height), interpolation=cv2.INTER_AREA)
            self.answer_sheet_2 = cv2.resize(self.answer_sheet_2, (new_answer_width,new_answer_height), interpolation=cv2.INTER_AREA)
            print(self.answer_sheet_1.shape[:2])
            student_id_height,student_id_width = self.student_id_sheet.shape[:2]
            exam_id_height,exam_id_width = self.exam_id_sheet.shape[:2]
            new_exam_height = (math.ceil(exam_id_height // NUM_ROW_OF_EXAM_ID +1 )* NUM_ROW_OF_EXAM_ID)
            new_exam_width = (math.ceil(exam_id_width // NUM_COLUMN_OF_EXAM_ID +1)* NUM_COLUMN_OF_EXAM_ID)
            new_student_width = ((student_id_width // NUM_COLUMN_OF_STUDENT_ID +1)* NUM_COLUMN_OF_STUDENT_ID)
            self.exam_id_sheet = cv2.resize(self.exam_id_sheet, (new_exam_width,new_exam_height), interpolation=cv2.INTER_AREA)
            self.student_id_sheet = cv2.resize(self.student_id_sheet, (new_student_width,new_exam_height), interpolation=cv2.INTER_AREA)
            self.show_image()
    #Khởi chạy luồng xử lí  
    def startImageProcessing(self):
        if self.img_quality :
            self.img_process = threading.Thread(target=self.runImageProcessing, args=())
            self.img_process.start()
    @QtCore.pyqtSlot()
    def startImageDisplay(self):
        self.img_display_thread = threading.Thread(target=self.imageDisplay)
        self.img_display_thread.start()
     
    #xử lí hình ảnh và tìm đáp án
    def runImageProcessing(self):
        try:
         
            print("answer_sheet_1:")
            answer_selected_1 = self.imageProcess.find_sellected_checkbox(self.answer_sheet_1,15,4,50,0)
            print("answer_sheet_2:")
            answer_selected_2 = self.imageProcess.find_sellected_checkbox(self.answer_sheet_2,15,4,50,0)
            print("student_id_sheet:")
            self.student_selected = self.imageProcess.find_sellected_checkbox(self.student_id_sheet,10,6,50,1)
            print("exam_id_sheet:")
            self.exam_id_selected = self.imageProcess.find_sellected_checkbox(self.exam_id_sheet,10,3,50,2)

            student_id , exam_id = self.imageProcess.get_student_id_and_exam_id(self.student_selected,self.exam_id_selected)

            print("student id : {} , exam id : {}".format(student_id , exam_id))
            #Hiện thị thông tin lên giao diện
            self.uic.exam_id.setText(str(exam_id))
            self.uic.student_id.setText(str(student_id))
            #read student list excel
            df = pd.read_excel(self.studentslist_filename)
            if self.studentslist_filename != '':
                try:
                    nameofStudent = df[df['Mã sinh viên'] == student_id]['Họ và tên'].tolist()[0]
                    self.uic.student_name.setText(nameofStudent)
                    df.at[ df.index[df['Mã sinh viên'] == student_id].tolist()[0],'Mã đề'] = exam_id
                except:
                    self.uic.program_status.setText('Không tồn tại mã sinh viên')
                    print("Không tìm thấy mã sinh viên!")    
            if(self.answers_filename != ''):
                self.score = self.imageProcess.get_score(answer_selected_1,answer_selected_2, self.answers_filename)
                self.uic.score.setText(str(self.score)+'/'+str(NUM_ROW_OF_QUESTIONS_EACH_COLLUMN*2))
                try:
                    df.at[ df.index[df['Mã sinh viên'] == student_id].tolist()[0],'Số câu đúng'] = str(self.score)+'/30'
                    df.at[ df.index[df['Mã sinh viên'] == student_id].tolist()[0],'Điểm'] = self.score
                    df.to_excel(self.studentslist_filename,index=False)
                except:
                    print("Không tìm thấy mã sinh viên!")
            # #send to hardware
            if self.uic.connectBtn.text() == 'Disconnect':
                self.serial.write('Start\n'.encode())
        except:
            print("Khong the xu li anh, bo qua!")
            self.uic.program_status.setText('Không thể xử lí ảnh , bỏ qua!')
            # #Đẩy giấy ra
            if self.uic.connectBtn.text() == 'Disconnect':
                self.serial.write('Start\n'.encode())    
    def show_image(self):
            image1 = cv2.cvtColor(self.answer_sheet_1,cv2.COLOR_GRAY2BGR)
            image1 = QtGui.QImage(image1.data, image1.shape[1], image1.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            self.uic.answer_sheet_1_label.setPixmap(QtGui.QPixmap.fromImage(image1))
            image2 = cv2.cvtColor(self.answer_sheet_2,cv2.COLOR_GRAY2BGR)
            image2 = QtGui.QImage(image2.data, image2.shape[1], image2.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            self.uic.answer_sheet_2_label.setPixmap(QtGui.QPixmap.fromImage(image2))
        #time.sleep(0.1)
    def getCaptureImg(self):
        if self.uic.isUseCamera.isChecked():
            ret,frame = self.cap.read()
            for i in range(5):
                ret,frame = self.cap.read()
            self.image = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.frame = QtGui.QImage(self.image.data, self.image.shape[1], self.image.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            self.uic.origin_img_label.setPixmap(QtGui.QPixmap.fromImage(self.frame)) 
            cv2.imshow("Camera capture ",self.image)
           
            self.get_children_img_in_parent_img()
    ##COMPORT 
    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            text = text.rstrip('\r\n')
            self.uic.com_status.setText(text)
            print("Received data from com : ",text)
            if(text == 'Ready'):
                self.getCaptureImg()
                time.sleep(1)
                if self.img_quality != False:
                    self.runImageProcessing()
    @QtCore.pyqtSlot()
    def sendData2Comport(self):
        data = 'Start\n'
        self.serial.write(data.encode())
        # self.cap = cv2.VideoCapture(1+cv2.CAP_DSHOW)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    @QtCore.pyqtSlot()
    def connectComport(self):
        if self.uic.connectBtn.text() == "Connect":
            self.serial.setPortName(self.uic.comselect.currentText()) # <---
            self.serial.setBaudRate(self.uic.baudselect.currentData()) # <---
            if self.serial.open(QtCore.QIODevice.ReadWrite):
                self.uic.com_status.setText('Connected!')
                self.uic.connectBtn.setText('Disconnect')
            else:
                 self.uic.com_status.setText('Failed to connect comport!')
        else:
            self.disconnectFromPort()
            self.uic.connectBtn.setText('Connect')
            self.uic.com_status.setText('')
    @QtCore.pyqtSlot(bool)
    def disconnectFromPort(self):
        self.serial.close()
         
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())