# ----------------------------------------------------
# Q1. Second Largest
# url: https://www.geeksforgeeks.org/problems/second-largest3735/1
# ----------------------------------------------------
def getSecondLargest(self, arr):
    max1 = float("-inf")
    max2 = float("-inf")
    
    for ele in arr:
        if ele == max1:
            continue
        
        if ele > max1:
            max2 = max1
            max1 = ele
        elif ele > max2:
            max2 = ele
    
    return max2 if max2 != float("-inf") else -1

# ----------------------------------------------------
# Q2. Array Leaders
# url: https://www.geeksforgeeks.org/problems/leaders-in-an-array-1587115620/1
# ----------------------------------------------------
def leaders(self, arr):
    # code here
    size = len(arr)
    result = []
    result.append(arr[size - 1])
    
    # Maintain the maximum value as of now from right 
    for i in range(size - 2, -1, -1):
        if arr[i] >= result[len(result) - 1]:
            result.append(arr[i])
            
    result = result[::-1]
    
    return result

# ----------------------------------------------------
# Q3. Move all negative elements to end
# url: https://www.geeksforgeeks.org/problems/move-all-negative-elements-to-end1813/1
# ----------------------------------------------------
def segregateElements(self, arr):
    # code here
    positive=[]
    negative=[]
    for i in arr:
        if i<0:
            negative.append(i)
        else:
            positive.append(i)
    arr[:]=positive+negative
    return arr


# ----------------------------------------------------
# Q4. Minimum distance in an Array
# url: https://www.geeksforgeeks.org/problems/minimum-distance-between-two-numbers/1
# ----------------------------------------------------

def minDist(self, arr, x, y):
    x_idx = -1
    y_idx = -1
    x_found = False
    y_found = False
    min_dist = float("inf")

    for idx, ele in enumerate(arr):
        if ele == x:
            x_idx = idx
            x_found = True
            
        elif ele == y:
            y_idx = idx
            y_found = True
        
        if y_found and x_found:
            min_dist = min(min_dist, abs(x_idx -  y_idx))
        
    return min_dist if min_dist != float("inf") else -1


# ----------------------------------------------------
# Q5. Alternate Positive Negative
# url: https://www.geeksforgeeks.org/problems/array-of-alternate-ve-and-ve-nos1401/1
# ----------------------------------------------------

def rearrange(self,arr):
    # code here
    p_idx = 0
    n_idx = 0
    curr_idx = 0
    
    positive = []
    negative = []
    
    
    for ele in arr:
        if ele < 0:
            negative.append(ele)
        else:
            positive.append(ele)
            
    p_size = len(positive)
    n_size = len(negative)
    
    
    while(p_idx < p_size and n_idx < n_size):
        arr[curr_idx] = positive[p_idx]
        curr_idx += 1
        
        arr[curr_idx] = negative[n_idx]
        curr_idx += 1
        
        p_idx += 1
        n_idx += 1
    
    while p_idx < p_size:
        arr[curr_idx] = positive[p_idx]
        p_idx += 1
        curr_idx += 1
        
    while(n_idx < n_size):
        arr[curr_idx] = negative[n_idx]
        n_idx += 1
        curr_idx += 1
        
    return arr

# ----------------------------------------------------
# Q6. Third Largest
# url: https://www.geeksforgeeks.org/problems/third-largest-element/1
# ----------------------------------------------------

def thirdLargest(self,arr):
    # code here
    max1 = max2 = max3 = -1
    
    for ele in arr:
        if ele > max1:
            max3 = max2
            max2 = max1
            max1 = ele
        elif ele > max2:
            max3 = max2
            max2 = ele
        elif ele > max3:
            max3 = ele
    
    return max3

# ----------------------------------------------------
# Q7. Floor and Ceil in Unsorted
# url: https://www.geeksforgeeks.org/problems/ceil-the-floor2802/1
# ----------------------------------------------------
def getFloorAndCeil(self, x: int, arr: list) -> list:
    # code here
    floor = float("-inf")
    ceil = float("inf")
    
    result = []
    
    for ele in arr:
        # Floor of x is the largest element which is smaller than or equal to x. 
        #  Floor of x doesn’t exist if x is smaller than smallest element of arr[].
        if ele <= x:
            floor = max(floor, ele)
        
        # Ceil of x is the smallest element which is greater than or equal to x. 
        # Ceil of x doesn’t exist if x is greater than greatest element of arr[].
        if ele >= x:
            ceil = min(ceil, ele);
            
    if floor == float("-inf"):
        floor = -1
    if ceil == float("inf"):
        ceil = -1
    
    result.append(floor)
    result.append(ceil)
    
    return result

# ----------------------------------------------------
# Q8. First and Second Smallests
# url: https://www.geeksforgeeks.org/problems/find-the-smallest-and-second-smallest-element-in-an-array3226/1
# ----------------------------------------------------
def minAnd2ndMin(self, arr):
    # code here
    min1 = float("inf")
    min2 = float("inf")
    result = []
    
    for ele in arr:
        if ele < min1:
            min2 = min1
            min1 = ele
        elif ele != min1 and ele < min2:
            min2 = ele
    
    if min1 == float("inf") or min2 == float("inf"):
        result.append(-1)
        return result
        
    result.append(min1)
    result.append(min2)
    
    return result

# ----------------------------------------------------
# Q9. Longest Common Prefix of Strings
# url: https://www.geeksforgeeks.org/problems/longest-common-prefix-in-an-array5129/1
# ----------------------------------------------------
def longestCommonPrefix(self, arr):
    # code here
    
    ans = ""
    flag = True
    min_len = float("inf")
    
    for str in arr:
        min_len = min(min_len, len(str))
    
    for i in range(min_len):
        for str in arr:
            if str[i] != arr[0][i]:
                flag = False
                break
        
        if not flag:
            break
    
        ans += arr[0][i]
    return ans

# ----------------------------------------------------
# Q10. String Rotated by 2 Places
# url: https://www.geeksforgeeks.org/problems/check-if-string-is-rotated-by-two-places-1587115620/1
# ----------------------------------------------------
def isRotated(self,s1,s2):
    #code here
    s1_size = len(s1)
    s2_size = len(s2)

    # 1. Validate if both strings have valid size
    if s1_size < 2 or s2_size < 2 or s1_size != s2_size:
        return False
    
    if s1_size == 2:
        if s1 in s2:
            return True
        else:
            return False

    # 2. return false if 2nd half strings not present in S2      
    slice1 = s1[2:]
    slice2 = s1[0:s1_size - 2]
    
    if slice1 not in s2 and slice2 not in s2:
        return False
        
    flag1 = True
    flag2 = True
    
    
    # 3. Checking whether we can obtained S2 by rotating clockwise s1 by 2 places
    s1_idx = 0
    s2_idx = s2_size - 2
    
    while s1_idx < 2 and s2_idx < s2_size:
        if s1[s1_idx] != s2[s2_idx]:
            flag1 = False
            break
        s1_idx += 1
        s2_idx += 1
    
    # 4. Checking whether we can obtained S2 by rotating anti-clockwise s1 by 2 places
    s1_idx = s1_size - 2
    s2_idx = 0
    while s1_idx < s1_size and s2_idx < 2:
        if s1[s1_idx] != s2[s2_idx]:
            flag2 = False
            break
        s1_idx += 1
        s2_idx += 1
    
    
    return True if flag1 or flag2 else False