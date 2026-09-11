from array import List

# ===============================================================
# Program 1: 45. Jump Game II
# URL: https://leetcode.com/problems/jump-game-ii/description/
# ===============================================================
def jump_memo(self, nums, src_idx, dest_idx, dp):
    for src_idx in range(dest_idx, -1, -1):
        if src_idx == dest_idx:
            dp[src_idx] = 0
            continue

        min_jump_to_reach_dest = float("inf")
        for jump in range(1, nums[src_idx] + 1):
            if src_idx + jump < len(nums):
                min_jump_to_reach_dest = min(min_jump_to_reach_dest, dp[src_idx + jump])

        dp[src_idx] = min_jump_to_reach_dest + 1
    return dp[0]
def jump(self, nums: List[int]) -> int:
    cols = len(nums)
    dp = [-1] * cols
    
    return self.jump_memo(nums, 0, len(nums) - 1, dp)