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