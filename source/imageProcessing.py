from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import math
import pandas as pd

FRAME_SIZE_HEIGHT = 551
FRAME_SIZE_WIDTH = 384
NUW_COLUMN_OF_ANSWER = 4  #4 đáp án
NUM_ROW_OF_QUESTIONS_EACH_COLLUMN = 15 #15 câu hỏi mỗi cột
ANSWER_OPTION = ['A', 'B', 'C', 'D'] #4 phương án
NUM_ROW_OF_EXAM_ID = 10 # 10 hàng mã đề
NUM_COLUMN_OF_EXAM_ID = 3
NUM_ROW_OF_STUDENT_ID = NUM_ROW_OF_EXAM_ID
NUM_COLUMN_OF_STUDENT_ID = 6

EXAM_ID_LOCATION = [(45,235),(329,375)] #tọa độ của vùng mã đề ( đáy trên , đáy dưới)(cạnh trái , cạnh phải)
STUDENT_ID_LOCATION = [(45,235),(234,318)]
ANSWER_SHEET_1_LOCATION =[(275,525),(72,163)]
ANSWER_SHEET_2_LOCATION =[(275,525),(247,335)]

class imageProcessing():
    def __init__(self):
        pass
    #Tìm cạnh viền của ảnh
    def finding_edges_image(self,image):
        blurred = cv2.GaussianBlur(image, (5, 5), 1)
        edged = cv2.Canny(blurred,20, 250)
        #cv2.imshow("edge",edged)
        return edged
    #chuyển ảnh về dạng chính diện
    def warping_image(self,image):
            # find contours in the edge map, then initialize
        # the contour that corresponds to the document
        cnts = cv2.findContours(self.finding_edges_image(image).copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        #Sắp xếp các đường viền tìm thấy
        cnts = imutils.grab_contours(cnts)

        docCnt = None
        idCnt = None
        count = 0
        # Tìm trang giấy
        if len(cnts) > 0:
            # sort the contours according to their size in
            # descending order
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            #print(cnts)
            # loop over the sorted contours
            for c in cnts:
                # approximate the contour
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                # if our approximated contour has four points,
                # then we can assume we have found the paper
                if len(approx) == 4:
                        docCnt = approx
                        count = count +1
            
        print(count)
        #paper = four_point_transform(image, docCnt.reshape(4, 2))
        warped = four_point_transform(image, docCnt.reshape(4, 2))
        # cv2.imshow("paper",paper)
        #cv2.imshow("Anh sau khi chinh",warped)
        #cv2.imwrite('warped_image.jpg',warped)
        return warped
    #tách khung ảnh thành các cột và hàng
    def split_image(self,image,row,col):
        # make the number of rows and columns 
        # a multiple of 5 (questions = 15 and answer = 4)
        r = len(image) // row * row 
        c = len(image[0]) // col * col
        image = image[:r, :c]
        # split the image horizontally (row-wise)
        rows = np.vsplit(image, row)
        boxes = []
        for _row in rows:
            # split each row vertically (column-wise)
            cols = np.hsplit(_row, col)
            for box in cols:
                boxes.append(box)
        return boxes
    #tách các ô đã tô
    def split_filled_checkbox(self,image,option):
        
        if option == 0 : #answer sheet
           ret, thresh = cv2.threshold(image, 180, 255, cv2.THRESH_BINARY_INV)  #180 với answer 100 vs exam
           cv2.imshow("thesh answer ",thresh)
           #cv2.waitKey(0)
           return thresh
        elif option == 1: # student id
            ret, thresh = cv2.threshold(image, 175, 255, cv2.THRESH_BINARY_INV)  #180 với answer 100 vs exam
            cv2.imshow("thesh student id",thresh)
            #cv2.waitKey(0)
            return thresh
        elif option ==2 :# exam_id
            ret, thresh = cv2.threshold(image, 175, 255, cv2.THRESH_BINARY_INV)  #180 với answer 100 vs exam
            
            cv2.imshow("thesh exam id",thresh)
            #cv2.waitKey(0)
            return thresh
       
        
    #đánh giấu các ô đã tô
    def find_sellected_checkbox(self,image,row,col,pixel_thresh,option):
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if option == 0 : #answer sheet
            ret, thresh = cv2.threshold(image, 173, 255, cv2.THRESH_BINARY_INV)  #180 với answer 100 vs exam  
            image = thresh
        elif option == 1: # student id
            ret, thresh = cv2.threshold(image, 170, 255, cv2.THRESH_BINARY_INV)  #180 với answer 100 vs exam
            image = thresh
        elif option ==2 :# exam_id
            ret, thresh = cv2.threshold(image, 170, 255, cv2.THRESH_BINARY_INV)  #180 với answer 100 vs exam
            image = thresh
        cv2.imshow("Thresh ",image)

        boxes = self.split_image(image,row,col)
        #cv2.imshow('box 0',boxes[59])
        row_sellected = []
        # loop over the questions
        for i in range(0, row):
            col_sellected = [] 
            # loop over the answers
            for j in range(col):
                pixels = np.sum(boxes[j + i * col] == 255)
                #print(j, pixels)
                col_sellected.append(pixels)
            #print(col_sellected)
            row_sellected.append(col_sellected)
        print(row_sellected)
        array = np.array(row_sellected)
        if option == 0:
            # Xác định phần tử lớn nhất của mỗi hàng
            max_per_row = np.max(array, axis=1)
            row_sellected = np.where(array == max_per_row.reshape(-1,1),1,0)
        elif option == 1 or option == 2:
            # Xác định phần tử lớn nhất của mỗi cột
            max_per_column = np.max(array, axis=0)
            row_sellected = np.where(array == max_per_column, 1, 0)
        print(row_sellected)
        return row_sellected
    #xác nhận số bao danh và mã đề
    def get_student_id_and_exam_id(self,student_id_selected,exam_id_selected):
        student_exam = []
        exam_id = 0
        student_id = 0
        for i in range(NUM_COLUMN_OF_EXAM_ID-1,-1,-1):
            exam_id_col = [tple[i] for tple in exam_id_selected]
            exam_id = exam_id + exam_id_col.index(1)*pow(10,NUM_COLUMN_OF_EXAM_ID-1-i)
            
        for i in range(NUM_COLUMN_OF_STUDENT_ID-1,-1,-1):
            student_id_col = [tple[i] for tple in student_id_selected]
            student_id = student_id + student_id_col.index(1)*pow(10,NUM_COLUMN_OF_STUDENT_ID-1-i)
        student_exam.append(student_id)
        student_exam.append(exam_id)
        return student_exam

    def get_score(self,answer_selected_1,answer_selected_2,filename):
        answer_1 = 0
        answer_2 = 0
        df = pd.read_excel(filename)
        df = df.fillna(0)
        df = df.astype('int64')
        correct_answer = df.values.tolist()
        #print("correct : ",correct_answer)

        index = 0
        for r in (answer_selected_1):
            if np.count_nonzero(r==1) >1  : #check nếu có tồn tại 2 lựa chọn trong 1 câu thì loại
                continue
            else:
                if (r == correct_answer[index]).all() :
                    answer_1 +=1
            index += 1
        for r in (answer_selected_2):
            if np.count_nonzero(r==1) >1 : #check nếu có tồn tại 2 lựa chọn trong 1 câu thì loại
                continue
            else:
                if (r == correct_answer[index-NUM_ROW_OF_QUESTIONS_EACH_COLLUMN]).all() :
                    answer_2 +=1
            index += 1
        print("result : ",answer_1+answer_2)
        return answer_1 + answer_2



if __name__ == '__main__':
    filename = 'dan_an.xlsx'
    filename2 = 'students_list.xlsx'
    image = cv2.imread(r'image\test11.jpg')
    print(image.shape[:2])
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imageProcess = imageProcessing()
    #ảnh mới sau khi đã được chỉnh
    image = imageProcess.warping_image(gray)
    image = cv2.resize(image, (FRAME_SIZE_WIDTH,FRAME_SIZE_HEIGHT), interpolation=cv2.INTER_AREA)
    print(image.shape[:2])
    #cv2.imwrite('warped_image.jpg',image)
    answer_sheet_1 = image[ANSWER_SHEET_1_LOCATION[0][0]:ANSWER_SHEET_1_LOCATION[0][1],ANSWER_SHEET_1_LOCATION[1][0]:ANSWER_SHEET_1_LOCATION[1][1]]
    answer_sheet_2 = image[ANSWER_SHEET_2_LOCATION[0][0]:ANSWER_SHEET_2_LOCATION[0][1],ANSWER_SHEET_2_LOCATION[1][0]:ANSWER_SHEET_2_LOCATION[1][1]]
    student_id_sheet =image[STUDENT_ID_LOCATION[0][0]:STUDENT_ID_LOCATION[0][1],STUDENT_ID_LOCATION[1][0]:STUDENT_ID_LOCATION[1][1]]
    exam_id_sheet = image[EXAM_ID_LOCATION[0][0]:EXAM_ID_LOCATION[0][1],EXAM_ID_LOCATION[1][0]:EXAM_ID_LOCATION[1][1]]

    cv2.imshow("left",answer_sheet_1)
    cv2.imshow("right",answer_sheet_2)
    cv2.imshow("id",student_id_sheet)
    cv2.imshow("qid",exam_id_sheet)
    
    #thay đổi kích cỡ thành các kích cỡ chẵn
    answer_height,answer_width = answer_sheet_1.shape[:2]
    #print(answer_sheet_1.shape[:2])
    new_answer_height = (math.ceil(answer_height // NUM_ROW_OF_QUESTIONS_EACH_COLLUMN +1)* NUM_ROW_OF_QUESTIONS_EACH_COLLUMN)
    new_answer_width = (math.ceil(answer_width // NUW_COLUMN_OF_ANSWER )* NUW_COLUMN_OF_ANSWER)
    answer_sheet_1 = cv2.resize(answer_sheet_1, (new_answer_width,new_answer_height), interpolation=cv2.INTER_AREA)
    answer_sheet_2 = cv2.resize(answer_sheet_2, (new_answer_width,new_answer_height), interpolation=cv2.INTER_AREA)
    #print(answer_sheet_1.shape[:2])
    student_id_height,student_id_width = student_id_sheet.shape[:2]
    exam_id_height,exam_id_width = exam_id_sheet.shape[:2]
    new_exam_height = (math.ceil(exam_id_height // NUM_ROW_OF_EXAM_ID +1 )* NUM_ROW_OF_EXAM_ID)
    new_exam_width = (math.ceil(exam_id_width // NUM_COLUMN_OF_EXAM_ID +1)* NUM_COLUMN_OF_EXAM_ID)
    new_student_width = ((student_id_width // NUM_COLUMN_OF_STUDENT_ID +1)* NUM_COLUMN_OF_STUDENT_ID)

    #print(exam_id_sheet.shape[:2])
    exam_id_sheet = cv2.resize(exam_id_sheet, (new_exam_width,new_exam_height), interpolation=cv2.INTER_AREA)
    student_id_sheet = cv2.resize(student_id_sheet, (new_student_width,new_exam_height), interpolation=cv2.INTER_AREA)
    print("Student id shape: ",student_id_sheet.shape[:2])    
    # print(answer_sheet_1.shape[:2])
    # print(student_id_sheet.shape[:2])
    # print(exam_id_sheet.shape[:2])

    # answer_sheet_1 = imageProcess.split_filled_checkbox(answer_sheet_1,0)
    # answer_sheet_2 = imageProcess.split_filled_checkbox(answer_sheet_2,0)
    # student_id_sheet= imageProcess.split_filled_checkbox(student_id_sheet,1)
    # exam_id_sheet= imageProcess.split_filled_checkbox(exam_id_sheet,2)


    # #boxes = split_image(answer_sheet_1)

    # # cv2.imshow("left",answer_sheet_1)
    # # cv2.imshow("right",answer_sheet_2)
    # # cv2.imshow("id",student_id_sheet)
    # # cv2.imshow("qid",exam_id_sheet)
    print("answer_sheet_1:")
    answer_selected_1 = imageProcess.find_sellected_checkbox(answer_sheet_1,15,4,50,0)
    print("answer_sheet_2:")
    answer_selected_2 = imageProcess.find_sellected_checkbox(answer_sheet_2,15,4,50,0)
    print("student_id_sheet:")
    student_selected = imageProcess.find_sellected_checkbox(student_id_sheet,10,6,50,1)
    print("exam_id_sheet:")
    exam_id_selected = imageProcess.find_sellected_checkbox(exam_id_sheet,10,3,100,2)

    student_id , exam_id = imageProcess.get_student_id_and_exam_id(student_selected,exam_id_selected)

    print("student id : {} , exam id : {}".format(student_id , exam_id))
    
    imageProcess.get_score(answer_selected_1,answer_selected_2,filename)
    cv2.waitKey(0)