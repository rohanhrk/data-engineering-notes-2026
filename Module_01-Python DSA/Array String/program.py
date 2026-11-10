from typing import List;

# ============================================================================
# program 1 : 925. Long Pressed Name
# url : https://leetcode.com/problems/long-pressed-name/description/
# ============================================================================

def isLongPressedName(self, name: str, typed: str) -> bool:
    i = 0
    j = 0
    len_name = len(name)
    len_typed = len(typed)

    if name[i] != typed[j] or name[len_name - 1] != typed[len_typed - 1] or len_name > len_typed:
        return False
    i += 1
    j += 1

    while(i < len_name and j < len_typed):
        if name[i] == typed[j]:
            i += 1
            j += 1
        
        elif name[i - 1] == typed[j]:
            j += 1

        else:
            return False
    
    while i == len_name and j < len_typed and name[i - 1] == typed[j]:
        j += 1

    return i == len_name and j == len_typed

# ============================================================================
# program 2 : 11. Container With Most Water
# url :https://leetcode.com/problems/container-with-most-water/description/
# ============================================================================

def maxArea(self, height: List[int]) -> int:
    left_idx = 0
    right_idx = len(height) - 1

    max_amnt_of_water = -int(1e9)

    while left_idx < right_idx:
        ht = min(height[left_idx], height[right_idx])
        lt = right_idx - left_idx
        curr_water = ht * lt
        max_amnt_of_water = max(max_amnt_of_water, curr_water)

        if(height[left_idx] < height[right_idx]):
            left_idx += 1
        
        else:
            right_idx -= 1

    
    return max_amnt_of_water


# ============================================================================
# program 3 : 977. Squares of a Sorted Array
# url :https://leetcode.com/problems/squares-of-a-sorted-array/description/
# ============================================================================
def sortedSquares(self, nums: List[int]) -> List[int]:
    size = len(nums)
    ans = [0] * size

    st_idx = 0
    end_idx = size - 1
    k = size - 1

    while st_idx <= end_idx:
        sq1 = nums[st_idx] * nums[st_idx]
        sq2 = nums[end_idx] * nums[end_idx]

        if sq1 < sq2:
            ans[k] = sq2
            end_idx -= 1
        else:
            ans[k] = sq1
            st_idx += 1
        
        k -= 1

    return ans

# ============================================================================
# program 4 : 169. Majority Element
# url :https://leetcode.com/problems/majority-element/description/
# ============================================================================

def majorityElement(self, nums: List[int]) -> int:
    maj_elem = nums[0]
    count = 0

    for num in nums:
        if count == 0:
            maj_elem = num
            count = 1
        elif num == maj_elem:
            count += 1
        else:
            count -= 1

    return maj_elem


# ============================================================================
# program 5 : 229. Majority Element II
# url :https://leetcode.com/problems/majority-element-ii/description/
# ============================================================================

def majorityElement(self, nums: List[int]) -> List[int]:
    maj_ele1 = maj_ele2 = nums[0]
    count1 = count2 = 0


    for num in nums:
        if maj_ele1 == num:
            count1 += 1
        elif maj_ele2 == num:
            count2 += 1
        else:
            if count1 == 0:
                maj_ele1 = num
                count1 = 1
            elif count2 == 0:
                maj_ele2 = num
                count2 = 1
            else:
                count1 -= 1
                count2 -= 1

    res = []

    count1 = count2 = 0

    for num in nums:
        if num == maj_ele1:
            count1 += 1
        elif num == maj_ele2:
            count2 += 1
    
    if count1 > (len(nums) / 3):
        res.append(maj_ele1)
    if count2 > (len(nums) / 3):
        res.append(maj_ele2)

    return res


# ============================================================================
# program 6 : 556. Next Greater Element III
# url :https://leetcode.com/problems/next-greater-element-iii/description/
# ============================================================================

def getDipIndex(self, list):
    dip_idx = -1
    for i in range(len(list) - 2, -1, -1):
        if list[i] < list[i + 1]:
            dip_idx = i
            break
    return dip_idx

def getCeilIndex(self, list, dip_idx):
    ceil_idx = -1

    for i in range(len(list) - 1, dip_idx, -1):
        if list[i] > list[dip_idx]:
            ceil_idx = i
            break

    return ceil_idx

def swap(self, list, left_ptr, right_ptr):
    list[left_ptr], list[right_ptr] = list[right_ptr], list[left_ptr]

def reverse(self, list, left_ptr, right_ptr):
    list[left_ptr:] = list[left_ptr:][::-1]

def nextGreaterElement(self, n: int) -> int:
    num_as_str = str(n) # convert integer to string
    num_as_list = list(num_as_str) # conver string to a list
    
    # find dip index -> dip_idx
    dip_idx = self.getDipIndex(num_as_list)

    if dip_idx == -1:
        return -1

    # find first ceil index of dip index and swap both the value
    ceil_idx = self.getCeilIndex(num_as_list, dip_idx)
    self.swap(num_as_list, dip_idx, ceil_idx)

    # reverse from dip_idx + 1 to end
    self.reverse(num_as_list, dip_idx + 1, len(num_as_list) - 1)

    # return result
    list_as_str = "".join(num_as_list)
    list_as_number = int(list_as_str)

    return list_as_number if list_as_number <= (2 ** 31) - 1 else -1


# ============================================================================
# program 7 : 905. Sort Array By Parity
# url : https://leetcode.com/problems/sort-array-by-parity/description/
# ============================================================================
def swap(self, nums, left_ptr, right_ptr):
    temp = nums[left_ptr]
    nums[left_ptr] = nums[right_ptr]
    nums[right_ptr] = temp
    
def sortArrayByParity(self, nums: List[int]) -> List[int]:
    even_ptr = -1 # pointing to last even number
    odd_ptr = -1 # pointing to last odd number
    curr_ptr = 0 # poiting to number which is not resolved

    while curr_ptr < len(nums):
        if nums[curr_ptr] % 2 == 0:
            # encountered even number
            even_ptr += 1
            self.swap(nums, even_ptr, curr_ptr)
        else:
            odd_ptr += 1

        curr_ptr += 1

    return nums

# ============================================================================
# program 8 : 628. Maximum Product of Three Numbers
# url : https://leetcode.com/problems/maximum-product-of-three-numbers/description/
# ============================================================================
def product(self, num1, num2, num3):
    return num1 * num2 * num3

def maximumProduct(self, nums: List[int]) -> int:
    max1 = max2 = max3 = -int(1e9)
    min1 = min2 = int(1e9)

    for num in nums:
        # 1. maximize the value of max1, max2, max3 in each iteration
        if(num > max1):
            max3 = max2
            max2 = max1
            max1 = num
        elif(num > max2):
            max3 = max2
            max2 = num
        elif(num > max3):
            max3 = num
        
        # 2. minimize the value of min1 and min2
        if(num < min1):
            min2 = min1
            min1 = num
        elif(num < min2):
            min2 = num

    pot_cand1 = self.product(max1, max2, max3)
    pot_cand2 = self.product(max1, min1, min2)

    return max(pot_cand1, pot_cand2)

# ============================================================================
# program 9 : 769. Max Chunks To Make Sorted
# url : https://leetcode.com/problems/max-chunks-to-make-sorted/description/
# ============================================================================

def maxChunksToSorted(self, arr: List[int]) -> int:
    current_max = -int(1e9)             # maintain a current max till current index which will help us to tell 
                                        #wheather we need to create a chunks at current index

    number_of_chunks = 0                # store number of chunks

    for idx in range(len(arr)):
        current_max = max(current_max, arr[idx])

        # When current max become equal to current index
        # we can create a chunks of it
        if(current_max == idx):
            number_of_chunks += 1

    return number_of_chunks

# ============================================================================
# program 10 : 768. Max Chunks To Make Sorted II
# url : https://leetcode.com/problems/max-chunks-to-make-sorted-ii/description/
# ============================================================================

def maxChunksToSorted(self, arr: List[int]) -> int:
    size = len(arr)
    current_max_arr = [0] * size
    right_min_arr = [int(1e9)] * (size + 1)
    number_of_chunks = 0

    current_max_arr[0] = arr[0]
    right_min_arr[size - 1] = arr[size - 1]

    for idx in range(1, size):
        current_max_arr[idx] = max(current_max_arr[idx - 1], arr[idx])

    for idx in range(size - 2, 0, -1):
        right_min_arr[idx] = min(right_min_arr[idx + 1], arr[idx])

    for idx in range(0, size):
        if(current_max_arr[idx] <= right_min_arr[idx + 1]):
            number_of_chunks += 1

    return number_of_chunks


# ============================================================================
# program 11 : 345. Reverse Vowels of a String
# url : https://leetcode.com/problems/reverse-vowels-of-a-string/
# ============================================================================
def isVowel(self, list, idx):
    return list[idx].lower() in "aeiou"

def swap(self, list, lidx, ridx):
    list[lidx], list[ridx] = list[ridx], list[lidx]

def reverseVowels(self, s: str) -> str:
    str_as_list = list(s)
    st_idx = 0
    end_idx = len(s) - 1

    while st_idx < end_idx:
        # 1. Move starting index till we get vowel
        
        while st_idx < end_idx and not self.isVowel(str_as_list, st_idx):
            st_idx += 1

        # 2. Move ending index till we get vowel
        while st_idx < end_idx and not self.isVowel(str_as_list, end_idx):
            end_idx -= 1

        # 3. If no vowel found in any of the index -> break the loop
        if st_idx >= end_idx:
            break

        # 4. swap the value of both index
        self.swap(str_as_list, st_idx, end_idx)

        st_idx += 1
        end_idx -= 1
    
    s = "".join(str_as_list)
    return s

# ============================================================================
# program 12 : 795. Number of Subarrays with Bounded Maximum
# url : https://leetcode.com/problems/number-of-subarrays-with-bounded-maximum/description/
# ============================================================================

def numSubarrayBoundedMax(self, nums: List[int], left: int, right: int) -> int:
    st_window_idx = 0
    end_window_idx = 0
    prev_ans = 0
    ans = 0

    while end_window_idx < len(nums):
        # Case 1: if left <= nums[end_window_idx"] <= right
        if nums[end_window_idx] >= left and nums[end_window_idx] <= right:
            ans += (end_window_idx - st_window_idx + 1)
            prev_ans = (end_window_idx - st_window_idx + 1)

        # Case 2: if left < nums[end_window_idx"]
        elif nums[end_window_idx] < left:
            ans += prev_ans

        # Case 3: if nums[end_window_idx"] > right
        else:
            prev_ans = 0
            st_window_idx = end_window_idx + 1

        end_window_idx += 1

    return ans

# ============================================================================
# program 13 : 238. Product of Array Except Self
# url : https://leetcode.com/problems/product-of-array-except-self/
# ============================================================================
def productExceptSelf(self, nums: List[int]) -> List[int]:
    left_prod = [1] * len(nums)
    right_prod = [1] * len(nums)
    ans = [0] * len(nums)

    for i in range(1, len(nums)):
        left_prod[i] = left_prod[i - 1] * nums[i - 1]

    ans[len(nums) - 1] = left_prod[len(nums) - 1] * right_prod[len(nums) - 1]
    
    for i in range(len(nums) - 2, -1, -1):
        right_prod[i] = right_prod[i + 1] * nums[i + 1]
        ans[i] = left_prod[i] * right_prod[i]

    return ans

# ============================================================================
# program 14 : 118. Pascal's Triangle
# url : https://leetcode.com/problems/pascals-triangle/description/
# ============================================================================
def generate(self, numRows: int) -> List[List[int]]:
    ans = []

    for row in range(numRows):
        smallAns = []
        for col in range(row + 1):
            if col == 0 or col == row:
                smallAns.append(1)
                continue
            
            smallAns.append(ans[row - 1][col - 1] + ans[row - 1][col])
        
        ans.append(smallAns)

    return ans

# ============================================================================
# program 15 : 849. Maximize Distance to Closest Person
# url : https://leetcode.com/problems/maximize-distance-to-closest-person/description/
# ============================================================================
def maxDistToClosest(self, seats: List[int]) -> int:
    dist_idx = -int(1e9)
    max_closest_dist = -int(1e9)

    # solving distance between Alax and a person from left side to right
    for i in range (len(seats)):
        if seats[i] == 1:
            # occupied -> mark as -1
            seats[i] = -1
            dist_idx = i
            continue

        seats[i] = abs(dist_idx - i)

    # Now solving distance between Alax and a person from right side to left
    # Additionally, we are solving cloest distance (min) and also maximize the distance 
    # which will be our answer

    dist_idx = int(1e9) # reset the value dist_idx
    
    for i in range (len(seats) - 1, -1, -1):
        if seats[i] == -1:
            # occupied
            dist_idx = i
            continue

        seats[i] = min(seats[i], abs(dist_idx - i))
        max_closest_dist = max(max_closest_dist, seats[i])

    return max_closest_dist

# ============================================================================
# program 16 : 41. First Missing Positive
# url : https://leetcode.com/problems/first-missing-positive/description/
# ============================================================================
def firstMissingPositive(self, nums: List[int]) -> int:
    is_one_present_flag = False
    unmarked_idx = len(nums) + 1 # assuming all element is present

    # 1. Travel on list and replace out of ranged value as 1
    # and also marked the flag value as True if found 1 in the list
    for i in range(len(nums)):
        if 0 >= nums[i] or nums[i] > len(nums):
            nums[i] = 1
        elif nums[i] == 1:
            is_one_present_flag = True
        else:
            continue
    
    # 2. Return 1 if 1 is not found in the list
    if not is_one_present_flag:
        return 1

    # 3. Travel on list and go to nums[elem], mark by negative sign
    for idx, elem in enumerate(nums):
        nums[abs(elem) - 1] = -abs(nums[abs(elem) - 1])

    # 4. Iterate on the updated list and find unmarked index, unmarked_idx + 1 is result
    # otherwise n + 1 is result

    for idx in range(len(nums)):
        if  nums[idx] > 0:
            unmarked_idx = idx + 1
            break
        
    return unmarked_idx