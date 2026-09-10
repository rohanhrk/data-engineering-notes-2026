from array import List

# ===============================================================
# program 1: 11. Container With Most Water
# URL: https://leetcode.com/problems/container-with-most-water/description/?envType=problem-list-v2&envId=array
# ===============================================================
def maxArea(self, height: List[int]) -> int:
    left = 0
    right = len(height) - 1
    max_water = 0

    while left < right:
        l = right - left 
        b = 1
        h = min(height[left], height[right])

        max_water = max(max_water, l * b * h)

        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_water


# ===============================================================
# program 2: 15. 3Sum
# URL: https://leetcode.com/problems/3sum/?envType=problem-list-v2&envId=array
# ===============================================================
def threeSum(self, nums: list[int]) -> list[list[int]]:
    nums.sort()

    result = []

    for i in range(0, len(nums) - 2):
        if i != 0 and nums[i] == nums[i - 1]:
            continue

        left = i + 1
        right = len(nums) - 1

        while left < right:
            if left != i + 1 and nums[left] == nums[left - 1]:
                left += 1
                continue
            
            sum = nums[i] + nums[left] + nums[right]

            if sum == 0:
                smallAns = [nums[i], nums[left], nums[right]]
                result.append(smallAns)

                left += 1
                right -= 1
            elif sum > 0:
                right -= 1
            else:
                left += 1
    

    return result

# ===============================================================
# program 3: 16. 3Sum Closest
# URL: https://leetcode.com/problems/3sum-closest/description/?envType=problem-list-v2&envId=array
# ===============================================================

def threeSumClosest(self, nums: List[int], target: int) -> int:
    nums.sort()

    closest_sum = float("inf")

    for i in range(0, len(nums) - 2):
        if i != 0 and nums[i] == nums[i - 1]:
            continue

        left = i + 1
        right = len(nums) - 1

        while left < right:
            if left != i + 1 and nums[left] == nums[left - 1]:
                left += 1
                continue
            
            sum = nums[i] + nums[left] + nums[right]
            if abs(sum - target) < abs(target - closest_sum):
                closest_sum = sum

            if sum == target:
                left += 1
                right -= 1
            elif sum > target:
                right -= 1
            else:
                left += 1
    
    return closest_sum

# ===============================================================
# program 4: 18. 4Sum
# URL: https://leetcode.com/problems/4sum/description/?envType=problem-list-v2&envId=array
# ===============================================================

def twoSum(self, nums, idx, target, k):
    left = idx
    right = len(nums) - 1
    result = []

    while left < right:
        if left != idx and nums[left] == nums[left - 1]:
            left += 1
            continue

        sum = nums[left] + nums[right]

        if sum == target:
            smallAns = [nums[left], nums[right]]
            result.append(smallAns)

            left += 1
            right -= 1
        elif sum < target:
            left += 1
        else:
            right -= 1

    return result

def fourSum_rec(self, nums, idx, target, k):
    if k == 2:
        return self.twoSum(nums, idx, target, k)

    result = []
    for i in range(idx, len(nums) - k + 1):
        if i != idx and nums[i] == nums[i - 1]:
            continue
        list = self.fourSum_rec(nums, i + 1, target - nums[i], k - 1)
        for l in list:
            l.append(nums[i])
            result.append(l)
    return result

def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
    nums.sort()

    return self.fourSum_rec(nums, 0, target, 4)     

# ===============================================================
# program 5: 31. Next Permutation
# URL: https://leetcode.com/problems/next-permutation/?envType=problem-list-v2&envId=array
# ===============================================================
def getDipIdx(self, nums):
    dip_idx = -1

    for i in range(len(nums) - 2, -1, -1):
        if nums[i] < nums[i + 1]:
            dip_idx = i
            break

    return dip_idx

def getNextGreater(self, nums, dip_idx):
    next_dip_greater = dip_idx

    for i in range(len(nums) - 1, dip_idx, -1):
        if nums[i] > nums[dip_idx]:
            next_dip_greater = i
            break

    return next_dip_greater

def swap(self, nums, left_idx, right_idx):
    nums[left_idx], nums[right_idx] = nums[right_idx], nums[left_idx]

def reverse(self, nums, left_idx, right_idx):
    while left_idx < right_idx:
        self.swap(nums, left_idx, right_idx)
        left_idx += 1
        right_idx -= 1
        
def nextPermutation(self, nums: List[int]) -> None:
    """
    Do not return anything, modify nums in-place instead.
    """
    
    dip_idx = self.getDipIdx(nums)
    if dip_idx == -1:
        nums.sort()
        return
    
    next_dip_greater = self.getNextGreater(nums, dip_idx)
    self.swap(nums, dip_idx, next_dip_greater)
    self.reverse(nums, dip_idx + 1, len(nums) - 1)
    
# ===============================================================
# program 6: 33. Search in Rotated Sorted Array
# URL: https://leetcode.com/problems/search-in-rotated-sorted-array/description/?envType=problem-list-v2&envId=array
# ===============================================================
def search(self, nums: List[int], target: int) -> int:
    tar_idx = -1
    left = 0
    right = len(nums) - 1

    while left <= right:
        mid = left + int((right - left) / 2)

        if nums[mid] == target:
            tar_idx = mid
            break
        elif nums[mid] < nums[right]:
            # right side is sorted
            if target > nums[mid] and target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
        else:
            # left side sorted
            if target >= nums[left] and target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1

    return tar_idx

# ===============================================================
# program 7: 34. Find First and Last Position of Element in Sorted Array
# URL: https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/description/?envType=problem-list-v2&envId=array
# ===============================================================
def getLeftMostTarIdx(self, nums, target, left, right):
    left_most = right

    while left <= right:
        mid = left + int((right - left)/2)

        if target <= nums[mid]:
            if target == nums[mid]:
                left_most = mid
            right = mid - 1
        else:
            left = mid + 1
    
    return left_most

def getRightMostTarIdx(self, nums, target, left, right):
    right_most = left

    while left <= right:
        mid = left + int((right - left)/2)

        if target >= nums[mid]:
            if target == nums[mid]:
                right_most = mid
            left = mid + 1
        else:
            right = mid - 1
    
    return right_most

def searchRange(self, nums: List[int], target: int) -> List[int]:
    left_idx = 0
    right_idx = len(nums) - 1
    st_tar_idx = -1
    end_tar_idx = -1

    while left_idx <= right_idx:
        mid = left_idx + int((right_idx - left_idx)/2)

        if nums[mid] == target:
            st_tar_idx = mid
            end_tar_idx = mid

            break
        elif nums[mid] > target:
            right_idx = mid - 1
        else:
            left_idx = mid + 1

    if st_tar_idx != -1:
        st_tar_idx = self.getLeftMostTarIdx(nums, target, 0, st_tar_idx)
    if end_tar_idx != -1:
        end_tar_idx = self.getRightMostTarIdx(nums, target, end_tar_idx, len(nums) - 1)
    
    return [st_tar_idx, end_tar_idx]


# ===============================================================
# program 8: 36. Valid Sudoku
# URL: https://leetcode.com/problems/valid-sudoku/
# ===============================================================
def isValidSudoku(self, board: List[List[str]]) -> bool:
    rows = len(board)
    cols = len(board[0])
    track = set()

    for row in range(rows):
        for col in range(cols):
            if board[row][col] != '.':
                number = board[row][col]

                if f"{number} in row {row}" in track or f"{number} in col {col}" in track or f"{number} in subBox {int(row/3)},{int(col/3)}" in track:
                    return False
                
                track.add(f"{number} in row {row}")
                track.add(f"{number} in col {col}")
                track.add(f"{number} in subBox {int(row/3)},{int(col/3)}")

    return True
