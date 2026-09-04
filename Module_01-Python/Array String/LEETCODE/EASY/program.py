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