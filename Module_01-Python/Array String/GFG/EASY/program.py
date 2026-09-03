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

# ----------------------------------------------------
# Q11. String Duplicates Removal
# url: https://www.geeksforgeeks.org/problems/remove-all-duplicates-from-a-given-string4321/1
# ----------------------------------------------------
def removeDuplicates(self, s):
    # code here
    ch_set = set()
    result = ""
    
    for ch in s:
        if ch in ch_set:
            continue
        
        ch_set.add(ch)
        result += ch
        
    return result

# ----------------------------------------------------
# Q12. Most Frequent Character
# url: https://www.geeksforgeeks.org/problems/maximum-occuring-character-1587115620/1
# ----------------------------------------------------
def getMaxOccuringChar(self, s):
    # code here
    freq_char = [0] * 26
    max_freq_count = -float("inf")
    max_freq_char = ''
    
    for ch in s:
        freq_char[ord(ch) - ord('a')] += 1
        
        # If current current characters frequency is more than overall frequency 
        # update max_freq_count and max_freq_char
        if freq_char[ord(ch) - ord('a')] > max_freq_count:
            max_freq_count = freq_char[ord(ch) - ord('a')]
            max_freq_char = ch
        
        # If current current characters frequency is equal to overall frequency 
        # pick only lexicographically smaller character
        elif freq_char[ord(ch) - ord('a')] == max_freq_count and ch < max_freq_char:
            max_freq_char = ch
            
    return max_freq_char

# ----------------------------------------------------
# Q13. Replace Consecutive Two Same with One
# url: https://www.geeksforgeeks.org/problems/consecutive-elements2306/1
# ----------------------------------------------------
def removeDuplicates(self, s):
    # code here
    result = ""
    st_as_list = []
    
    for ch in s:
        if st_as_list and st_as_list[len(st_as_list) - 1] == (ch):
            continue
        st_as_list.append(ch)
        
    result = result.join(st_as_list)
    return result

# ----------------------------------------------------
# Q14. Panagram Checking
# url: https://www.geeksforgeeks.org/problems/pangram-checking-1587115620/1
# ----------------------------------------------------
def checkPangram(self,s):
    #code here
    char_set = set()
    
    for ch in s:
        if ch >= 'a' and ch <= 'z':
            char_set.add(ord(ch) - ord('a'))
        elif ch >= 'A' and ch <= 'Z':
            char_set.add(ord(ch) - ord('A'))

    return True if len(char_set) == 26 else False

# ----------------------------------------------------
# Q15. Run Length Encoding
# url: https://www.geeksforgeeks.org/problems/run-length-encoding/1
# ----------------------------------------------------
def encode(self, s: str) -> str:
    # code here
    count = 1
    ch = s[0]
    result = ""
    
    for i in range(1, len(s)):
        if s[i] != s[i - 1]:
            result += ch + str(count)
            ch = s[i]
            count = 1
            continue
        
        count += 1
    
    result += ch + str(count)
    
    return result
    
# ----------------------------------------------------
# Q16. Remaining String
# url: https://www.geeksforgeeks.org/problems/remaining-string3515/1
# ----------------------------------------------------
def printString(self, s, ch, count):
    # code here
    idx = 0
    res = ""
    
    for curr_c in s:
        if curr_c == ch:
            count -= 1
            
            if count == 0:
                idx += 1
                res = s[idx:]
                return res
            
        idx += 1
        
    return res

# ----------------------------------------------------
# Q17. Count Words in a String
# url: https://www.geeksforgeeks.org/problems/count-number-of-words1500/1
# ----------------------------------------------------
def countWords(self, s: str) -> int:
    # code here
    return len(s.split())