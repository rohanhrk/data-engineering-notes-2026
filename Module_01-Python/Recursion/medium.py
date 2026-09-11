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