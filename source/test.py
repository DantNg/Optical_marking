import numpy as np

# Tạo mảng 2 chiều
array = np.array([[1, 20, 3],
                  [4, 5, 6],
                  [7, 8, 9]])

# Xác định phần tử lớn nhất của mỗi hàng
max_per_row = np.max(array, axis=1)

# Tạo mảng kết quả với điều kiện gán 1 cho phần tử lớn nhất và 0 cho các phần tử khác
result = np.where(array == max_per_row.reshape(-1, 1), 1, 0)

print(result)
