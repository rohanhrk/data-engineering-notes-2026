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