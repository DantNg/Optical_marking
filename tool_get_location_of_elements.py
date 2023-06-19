import cv2

# Hàm callback được gọi khi có sự kiện nhấn chuột
def draw_rectangle(event, x, y, flags, params):
    global x_start, y_start, drawing, rectangle
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x_start, y_start = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # Vẽ hình chữ nhật
            img_copy = img.copy()
            cv2.rectangle(img_copy, (x_start, y_start), (x, y), (0, 255, 0), 1)
            cv2.imshow("image", img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        # Lưu tọa độ hình chữ nhật
        rectangle = (x_start, y_start, x, y)

# Load ảnh
img = cv2.imread("warped_image.jpg")
#new_imd = img[17:321,44:155]
#cv2.imshow("aa",new_imd)
#cv2.imwrite("cot_1_fix.jpg",new_imd)
# Khởi tạo biến
x_start, y_start, drawing = -1, -1, False
rectangle = None

# Hiển thị ảnh và gán hàm callback

print(img.shape[:2])
img = cv2.resize(img, (384,551), interpolation=cv2.INTER_AREA)
print(img.shape[:2])
cv2.imshow("image", img)
#cv2.rectangle(img, (44, 17), (155, 321), (0, 255, 255), thickness=1)
cv2.setMouseCallback("image", draw_rectangle)

# Chờ phím bấm
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s"):
        # Lưu hình chữ nhật và đóng cửa sổ
        if rectangle is not None:
            #print(rectangle)
            print("[({},{}),({},{})]".format(rectangle[1],rectangle[3],rectangle[0],rectangle[2]))
            small_image = img[rectangle[1]:rectangle[3], rectangle[0]:rectangle[2]]
            cv2.imshow("crop_img",small_image)
            # break

cv2.waitKey(0)
cv2.destroyAllWindows()
