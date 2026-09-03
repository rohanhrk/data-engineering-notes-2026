# ----------------------------------------------------
# Q1. Rotate Array by One
# url: https://www.geeksforgeeks.org/problems/cyclically-rotate-an-array-by-one2614/1
# ----------------------------------------------------
def swap(self, arr, left_idx, right_idx):
    arr[left_idx], arr[right_idx] = arr[right_idx], arr[left_idx]

def reverse(self, arr, st_idx, end_idx):
    while st_idx < end_idx:
        self.swap(arr, st_idx, end_idx)
        st_idx += 1
        end_idx -= 1

def rotate(self, arr):
    size = len(arr)
    
    # 1. Reverse array 0 -> size - 2
    self.reverse(arr, 0, size - 2)
    
    # 2. Reverse whole array -> Ans
    self.reverse(arr, 0, size - 1)