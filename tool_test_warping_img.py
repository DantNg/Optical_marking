# import the necessary packages
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True,
# 	help="path to the input image")
# args = vars(ap.parse_args())
# define the answer key which maps the question number
# to the correct answer
ANSWER_KEY = {0: 1, 1: 4, 2: 0, 3: 3, 4: 1}
# load the image, convert it to grayscale, blur it
# slightly, then find edges
# image = cv2.imread(args["image"])
image = cv2.imread(r'image\test11.jpg')
print(image.shape[:2])

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 1)
edged = cv2.Canny(blurred,20, 250)
# cv2.imshow("gray",gray)
# cv2.imshow("blurred",blurred)
cv2.imshow("edge",edged)
# find contours in the edge map, then initialize
# the contour that corresponds to the document
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)

cnts = imutils.grab_contours(cnts)


docCnt = None
# ensure that at least one contour was found
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
				break
	
# apply a four point perspective transform to both the
# original image and grayscale image to obtain a top-down
# birds eye view of the paper
paper = four_point_transform(image, docCnt.reshape(4, 2))
warped = four_point_transform(gray, docCnt.reshape(4, 2))
print(warped.shape[:2])
height = 551
width = 384
image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
print(image.shape[:2])
# id_part = four_point_transform(gray, idCnt.reshape(4, 2))
# qid_part = four_point_transform(gray, qidCnt.reshape(4, 2))
# cv2.imshow("paper",paper)
cv2.imshow("Anh sau khi chinh",warped)
# cv2.imshow("Anh sbd",id_part)
# cv2.imshow("Anh ma de",qid_part)
cv2.imwrite('warped_image.jpg',warped)



## tìm đường viền ứng với 3 ô sbd, mã đề và phần trả lời
blurred = cv2.GaussianBlur(warped, (5, 5), 2)
edged = cv2.Canny(blurred, 100, 250)
cv2.imshow("edge2",edged)
# find contours in the thresholded image, then initialize
# the list of contours that correspond to questions
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)

cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

questionCnts = []
count = 0
# loop over the contours
for c in cnts:
	# compute the bounding box of the contour, then use the
	# bounding box to derive the aspect ratio
	(x, y, w, h) = cv2.boundingRect(c)
	#cv2.rectangle(warped, (x, y), (x+w, y+h), (0, 255, 0), 2)
	ar = w / float(h)
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	# if our approximated contour has four points,
	# then we can assume we have found the paper
	if len(approx) == 4:
		if count == 0:
			docCnt = approx
		elif count == 1:
			idCnt = approx
		elif count == 2:
			questionIDCnt = approx
		count=count+1
	# in order to label the contour as a question, region
	# should be sufficiently wide, sufficiently tall, and
	# have an aspect ratio approximately equal to 1
	if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
		questionCnts.append(c)
# sort the question contours top-to-bottom, then initialize
# the total number of correct answers
# questionCnts = contours.sort_contours(questionCnts,
# 	method="top-to-bottom")[0]
print(count)
paper = four_point_transform(warped, docCnt.reshape(4, 2))
# id_frame = four_point_transform(warped, idCnt.reshape(4, 2))
# qid_frame = four_point_transform(warped, questionIDCnt.reshape(4, 2))
cv2.imshow("answer_frame",paper)
# cv2.imshow("id_frame",id_frame)
# cv2.imshow("qid_frame",qid_frame)



# apply Otsu's thresholding method to binarize the warped
# piece of paper
thresh = cv2.threshold(paper, 0, 255,
	cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
cv2.imshow("thesh1",thresh)
edges = cv2.Canny(paper, 120, 160)
cv2.imshow("thesh2",edges)
correct = 0
# each question has 5 possible answers, to loop over the
# question in batches of 5
for (q, i) in enumerate(np.arange(0, len(questionCnts), 4)):
	# sort the contours for the current question from
	# left to right, then initialize the index of the
	# bubbled answer
	cnts = contours.sort_contours(questionCnts[i:i + 4])[0]
	bubbled = None
# loop over the sorted contours
	for (j, c) in enumerate(cnts):
		# construct a mask that reveals only the current
		# "bubble" for the question
		mask = np.zeros(thresh.shape, dtype="uint8")
		cv2.drawContours(mask, [c], -1, 255, -1)
		# apply the mask to the thresholded image, then
		# count the number of non-zero pixels in the
		# bubble area
		mask = cv2.bitwise_and(thresh, thresh, mask=mask)
		total = cv2.countNonZero(mask)
		# if the current total has a larger number of total
		# non-zero pixels, then we are examining the currently
		# bubbled-in answer
		if bubbled is None or total > bubbled[0]:
			bubbled = (total, j)
# # initialize the contour color and the index of the
# 	# *correct* answer
# 	color = (0, 0, 255)
# 	k = ANSWER_KEY[q]
# 	# check to see if the bubbled answer is correct
# 	if k == bubbled[1]:
# 		color = (0, 255, 0)
# 		correct += 1
# 	# draw the outline of the correct answer on the test
# 	cv2.drawContours(paper, [cnts[k]], -1, color, 3)
# 	# grab the test taker
score = (correct / 5.0) * 100
print("[INFO] score: {:.2f}%".format(score))
cv2.putText(paper, "{:.2f}%".format(score), (10, 30),
	cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
cv2.imshow("Original", image)
#cv2.imshow("Exam", paper)
cv2.waitKey(0)