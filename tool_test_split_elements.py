import cv2
import numpy as np
import imutils
from imutils.perspective import four_point_transform
# Đọc ảnh đầu vào
EXAM_ID_LOCATION =[(73,253),(330,369)]
img = cv2.imread('warped_image.jpg')
height, width = img.shape[:2]
print(height, width)
img = cv2.resize(img, (384,551), interpolation=cv2.INTER_AREA)
# Chia đôi ảnh theo chiều ngang
left_img = img[275:525,72:163]
right_img = img[275:525,247:335]
id_img = img[45:235,237:318]
qid_img = img[45:235,330:375]
cv2.imshow("left",left_img)
cv2.imshow("right",right_img)
cv2.imshow("id",id_img)
cv2.imshow("qid",qid_img)

cv2.imwrite('question_id.jpg',qid_img)
cv2.imwrite("cot_1_fix.jpg", left_img)
cv2.imwrite('student_id.jpg',id_img)
cv2.imwrite("cot_2_fix.jpg", right_img)

cv2.waitKey(0)
cv2.destroyAllWindows()
