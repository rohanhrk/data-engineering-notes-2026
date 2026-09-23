from array import List

# ============================================================================
# program 1 : 39. Combination Sum
# url : https://leetcode.com/problems/combination-sum/
# ============================================================================
def combinationSum_rec(self, candidates, idx, target, smallAns, ans) :
    if target == 0:
        base = [ele for ele in smallAns]
        ans.append(base)
        return

    for i in range(idx, len(candidates)):
        if target - candidates[i] >= 0:
            smallAns.append(candidates[i])
            self.combinationSum_rec(candidates, i, target - candidates[i], smallAns, ans)
            smallAns.pop()

def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
    smallAns = []
    ans = []
    self.combinationSum_rec(candidates, 0, target, smallAns, ans)
    return ans


# ============================================================================
# program 2 : 40. Combination Sum II
# url : https://leetcode.com/problems/combination-sum-ii/
# ============================================================================
def combinationSum2_rec(self, candidates, idx, target, smallAns, ans):
    if target == 0:
        base = [ele for ele in smallAns]
        ans.append(base)
        return 

    visited = [False] * 51
    for i in range(idx, len(candidates)):
        if not visited[candidates[i]] and target - candidates[i] >= 0:
            smallAns.append(candidates[i])
            visited[candidates[i]] = True
            
            self.combinationSum2_rec(candidates, i + 1, target - candidates[i], smallAns, ans)

            smallAns.pop()

def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
    candidates.sort()
    smallAns = []
    ans = []
    self.combinationSum2_rec(candidates, 0, target, smallAns, ans)
    
    return ans

# ============================================================================
# program 3 : 46. Permutations
# url : https://leetcode.com/problems/permutations/description/
# ============================================================================
def permute_rec(self, nums, smallAns, ans, visited):
    if len(smallAns) == len(nums):
        base = [ele for ele in smallAns]
        ans.append(base)

    for i in range(len(nums)):
        if not visited[i]:
            visited[i] = True
            smallAns.append(nums[i])
            self.permute_rec(nums, smallAns, ans, visited)
            smallAns.pop()
            visited[i] = False
def permute(self, nums: List[int]) -> List[List[int]]:
    smallAns = []
    ans = []
    visited = [False]*len(nums)
    self.permute_rec(nums, smallAns, ans, visited)

    return ans

# ============================================================================
# program 4 : 47. Permutations II
# url : https://leetcode.com/problems/permutations-ii/
# ============================================================================
# visited_so_far_idx -> picked index so far in the smallAns
# visited_so_far_num_each_level -> track each level number to restrict dublicate number 
def permuteUnique_rec(self, nums, smallAns, ans, visited_so_far_idx):
    if len(nums) == len(smallAns):
        base = [ele for ele in smallAns]
        ans.append(base)
        return

    visited_so_far_num_each_level = [False] * 21
    for i in range(len(nums)):
        if not visited_so_far_idx[i] and not visited_so_far_num_each_level[nums[i] + 10]:
            visited_so_far_idx[i] = True
            visited_so_far_num_each_level[nums[i] + 10] = True
            smallAns.append(nums[i])
            self.permuteUnique_rec(nums, smallAns, ans, visited_so_far_idx)
            visited_so_far_idx[i] = False
            smallAns.pop()

def permuteUnique(self, nums: List[int]) -> List[List[int]]:
    smallAns = []
    ans = []
    visited_so_far_idx = [False] * len(nums)
    self.permuteUnique_rec(nums, smallAns, ans, visited_so_far_idx)

    return ans


# ============================================================================
# program 5 : 17. Letter Combinations of a Phone Number
# url : https://leetcode.com/problems/letter-combinations-of-a-phone-number/description/
# ============================================================================
keys = ["0", "1", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"] # digits to letters mapping like 2 -> abc
def letterCombinations_rec(self, digits, length):
    if length == 0:
        return [""]

    currChar = digits[length - 1]
    digit = ord(currChar) - ord('0') # '2' - '0' = 2
    letters = self.keys[digit]
    
    recRes = self.letterCombinations_rec(digits, length - 1)
    myRes = []
    for letter in letters:
        for str in recRes:
            str += letter
            myRes.append(str)
    
    return myRes
def letterCombinations(self, digits: str) -> list[str]:
    return self.letterCombinations_rec(digits, len(digits))

# ============================================================================
# program 6 : 38. Count and Say
# url : https://leetcode.com/problems/count-and-say/description/
# ============================================================================
def countAndSay(self, n: int) -> str:
    if n == 1:
        return "1"

    recRes = self.countAndSay(n - 1)
    myRes = ""
    
    ch = recRes[0]
    count = 1
    for i in range(1,len(recRes)):
        if ch != recRes[i]:
            myRes += str(count) + ch
            ch = recRes[i]
            count = 1
            continue
        
        count += 1
    
    myRes += str(count) + ch

    return myRes