from array import List

# ----------------------------------------------------
# Q1. 1. Two Sum
# url: https://leetcode.com/problems/two-sum/description/?envType=problem-list-v2&envId=array
# ----------------------------------------------------
def isPresentInDictionary(self, map, num):
    if num in map:
        return True
    return False

def twoSum(self, nums: List[int], target: int) -> List[int]:
    number_idx_dict = {} # number vs index of that number
    result = []

    for i in range(len(nums)):
        if self.isPresentInDictionary(number_idx_dict, target - nums[i]):
            result.append(number_idx_dict.get(target - nums[i]))
            result.append(i)
            break

        number_idx_dict[nums[i]] = i
    
    print(number_idx_dict)
    return result

# ----------------------------------------------------
# Q2. 14. Longest Common Prefix
# url: https://leetcode.com/problems/longest-common-prefix/description/?envType=problem-list-v2&envId=array
# ----------------------------------------------------
def longestCommonPrefix(self, strs: List[str]) -> str:
    min_len = float("inf")
    result = ""
    matched = True # assuming prefix is smallest string amongst string in the string

    # finding minimum string length amongst strings in the list
    for str in strs:
        min_len = min(min_len, len(str))

    for idx in range(min_len):
        ch = strs[0][idx] # get the character at current index of first string in the list
        
        for str in strs:
            if str[idx] != ch:
                matched = False
                break
        
        if not matched:
            break

        result += ch

    return result

# ----------------------------------------------------
# Q3. 26. Remove Duplicates from Sorted Array
# url: https://leetcode.com/problems/remove-duplicates-from-sorted-array/?envType=problem-list-v2&envId=array
def removeDuplicates(self, nums: List[int]) -> int:
    unique_count = 0
    unique_set = set()

    for i in range(len(nums)):
        if nums[i] not in unique_set:
            nums[unique_count] = nums[i]
            unique_count += 1
            unique_set.add(nums[i])

    return unique_count

# ----------------------------------------------------
# Q4. 26. Remove Duplicates from Sorted Array
# url: https://leetcode.com/problems/remove-element/description/?envType=problem-list-v2&envId=array
def swap(self, nums, st_idx, end_idx):
    nums[st_idx], nums[end_idx] = nums[end_idx], nums[st_idx]
    
def removeElement(self, nums: List[int], val: int) -> int:
    k = len(nums)
    occ_val = 0

    for i in range(len(nums)):
        if nums[i] == val:
            k -= 1
            occ_val += 1
        elif occ_val > 0:
            self.swap(nums, i - occ_val, i)

    return k

# ----------------------------------------------------
# Q5. 35. Search Insert Position
# url: https://leetcode.com/problems/search-insert-position/?envType=problem-list-v2&envId=array

def searchInsert(self, nums: List[int], target: int) -> int:
    left = 0
    right = len(nums) - 1

    while left <= right:
        mid = left + int((right - left) / 2)
        print(f"l:{left}, r:{right}, m:{mid}")

        if nums[mid] == target:
            return mid
        elif target > nums[mid]:
            left = mid + 1
        elif target < nums[mid]:
            right = mid - 1

    return left

# ----------------------------------------------------
# Q6. 66. Plus One
# url: https://leetcode.com/problems/plus-one/?envType=problem-list-v2&envId=array

def plusOne(self, digits: List[int]) -> List[int]:
    c = 0
    result = []

    for i in range(len(digits) - 1, -1, -1):
        sum = 0
        if i == len(digits) - 1:
            sum += digits[i] + 1
        else:
            sum +=  digits[i] + c
        
        rem = sum % 10 #reminder
        div = int(sum / 10) # divident

        c = div
        result.append(rem)
    
    if c != 0:
        result.append(c)
    
    result = result[::-1]

    return result