import cv2
import numpy as np
import imutils
from imutils.perspective import four_point_transform
questions = 15
answers = 4
answer_options= ['A','B','C','D']
# split the thresholded image into boxes
def split_image(image):
    # make the number of rows and columns 
    # a multiple of 5 (questions = answers = 5)
    r = len(image) // questions * questions 
    c = len(image[0]) // answers * answers
    image = image[:r, :c]
    # split the image horizontally (row-wise)
    rows = np.vsplit(image, questions)
    boxes = []
    for row in rows:
        # split each row vertically (column-wise)
        cols = np.hsplit(row, answers)
        for box in cols:
            boxes.append(box)
    return boxes



# Đọc ảnh đầu vào
img = cv2.imread('cot_1_fix.jpg')
# height = 700 
# width = 400
# # Thực hiện giảm kích thước ảnh xuống 1 nửa
# img = cv2.resize(img, (int(width/1), int(height/1)), interpolation=cv2.INTER_LINEAR)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6,6))

# Chuyển ảnh sang ảnh grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# # Áp dụng Gaussian Blur để loại bỏ nhiễu
blur = cv2.GaussianBlur(gray, (5, 5), 1)

# # # Phát hiện cạnh bằng thuật toán Canny
# edged = cv2.Canny(blur, 110, 165)
# cv2.imshow("edged",edged)
# dilated = cv2.dilate(edged, kernel)
# # Tạo ảnh trắng mới
# mask = np.zeros_like(img, dtype=np.uint8)

# contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cv2.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv2.FILLED)

# # Lấy phần giao giữa ảnh gốc và ảnh trắng chỉ có các cạnh viền
# result1 =cv2.bitwise_not( cv2.bitwise_and(img, mask))

# # Hiển thị ảnh kết quả
# cv2.imshow('Result1', result1)
# result1 = cv2.cvtColor(result1, cv2.COLOR_BGR2GRAY)
# cv2.imshow('Result2', result1)
# # # Tìm các đường viền trong ảnh
# # contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# # contours = imutils.grab_contours(contours)


# # # Vẽ hình vuông lên các đường viền có kích thước lớn hơn ngưỡng

# thresh = cv2.threshold(result1, 0,100,
# 	cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
# cv2.imshow("thesh by threshold",thresh)

# cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
# 	cv2.CHAIN_APPROX_SIMPLE)


# morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
# morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
ret, thresh4 = cv2.threshold(gray, 175, 255, cv2.THRESH_BINARY_INV)  #180 với answer 100 vs exam
cv2.imshow("thesh by threshold",thresh4)
boxes = split_image(thresh4)
cv2.imshow("box1",boxes[1])
# counting the number of pixels

# # loop over the answers
for j in range(10*3):
    number_of_white_pix = np.sum(boxes[j] == 255)
    print(number_of_white_pix)
row_sellected = []
# loop over the questions
for i in range(0, questions):
    user_answer = None
    col_sellected = [] 
    # loop over the answers
    for j in range(answers):
        pixels = np.sum(boxes[j + i * answers] == 255)
        #print(j, pixels)
        col_sellected.append(pixels)

    # col_sellected = [1 if x > sum(col_sellected)/answers and x > 50 else 0 for x in col_sellected]  
    row_sellected.append(col_sellected)
    #print( user_answer)
print(row_sellected)
array = np.array(row_sellected)
# Xác định phần tử lớn nhất của mỗi cột
max_per_column = np.max(array, axis=0)

# Tạo mảng kết quả với điều kiện gán 1 cho phần tử lớn nhất và 0 cho các phần tử khác
result = np.where(array == max_per_column, 1, 0)
print(result)
# boxes = split_image(morph)
# #cv2.imshow("box",boxes[57])
# score = 0

# # loop over the questions
# for i in range(0, questions):
#     user_answer = None
    
#     # loop over the answers
#     for j in range(answers):
#         pixels = cv2.countNonZero(boxes[j + i * answers])
#         # if the current answer has a larger number of 
#         # non-zero (white) pixels then the previous one
#         # we update the `user_answer` variable
#         if user_answer is None or pixels > user_answer[1]: #nếu chưa có đáp án hoặc đáp án mới có độ pixel lớn hơn thì nhận làm kết quả
#             user_answer = (j, pixels)

#     print( user_answer)
# # get contours
# result = img.copy() 
# centers = []
# contours = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# contours = contours[0] if len(contours) == 2 else contours[1]
# print("count:", len(contours))
# print('')
# i = 1
# for cntr in contours:
#     (x, y, w, h) = cv2.boundingRect(cntr)
#     ar = w / float(h)
#     if w >= 8 and h >= 8 and ar >= 0.5 and ar <= 5:
		
#         M = cv2.moments(cntr)
#         cx = int(M["m10"] / M["m00"])
#         cy = int(M["m01"] / M["m00"])
#         centers.append((cx,cy))
#         cv2.circle(result, (cx, cy), 7, (0, 255, 0), -1)
#         pt = (cx,cy)
#         print("circle #:",i, "center:",pt)
#         i = i + 1
# print(i)
# # print list of centers
# #print(centers)

# # # save results
# # cv2.imwrite('omr_sheet_morph.png',morph)
# # cv2.imwrite('omr_sheet_result.png',result)
# # show results
# cv2.imshow("morph", morph)
# cv2.imshow("result", result)

# # questionCnts = []
# # count = 0
# # threshold = 70
# # for cnt in cnts:
# #     # Tính toán kích thước của hình vuông bao quanh đường viền
# #     x, y, w, h = cv2.boundingRect(cnt)
# #     size = max(w, h)
# #     # Nếu kích thước lớn hơn ngưỡng, vẽ hình vuông
# #     if size > threshold:
# #         cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

# # loop over the contours
# # for c in cnts:
# #     pass
# 	# compute the bounding box of the contour, then use the
# 	# bounding box to derive the aspect ratio
# 	# (x, y, w, h) = cv2.boundingRect(c)
	
# 	# ar = w / float(h)
# 	# # in order to label the contour as a question, region
# 	# # should be sufficiently wide, sufficiently tall, and
# 	# # have an aspect ratio approximately equal to 1
# 	# if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
# 	# 	questionCnts.append(c)
# # sort the question contours top-to-bottom, then initialize
# # the total number of correct answers
# # questionCnts = contours.sort_contours(questionCnts,
# # 	method="top-to-bottom")[0]
# #print(questionCnts)
# # Hiển thị kết quả
# cv2.imshow('Edges', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
