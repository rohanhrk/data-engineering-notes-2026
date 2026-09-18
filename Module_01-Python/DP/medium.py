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

# ===============================================================
# Program 2: 63. Unique Paths II
# URL: https://leetcode.com/problems/unique-paths-ii/description/
# ===============================================================
def uniquePathsWithObstacles_memo(self, matrix, sr, sc, dr, dc, dirs, dp):
    if sr == dr and sc == dc:
        dp[sr][sc] = 1
        return dp[sr][sc]

    if dp[sr][sc] != -1:
        return dp[sr][sc]

    ways = 0

    for dir in dirs:
        nr = sr + dir[0]
        nc = sc + dir[1]

        if nr >= 0 and nr <= dr and nc >= 0 and nc <= dc and matrix[nr][nc] != 1:
            ways += self.uniquePathsWithObstacles_memo(matrix, nr, nc, dr, dc, dirs, dp)

    dp[sr][sc] = ways
    return dp[sr][sc]

def uniquePathsWithObstacles(self, obstacleGrid: List[List[int]]) -> int:
    dirs = [[0, 1], [1, 0]]
    n, m = len(obstacleGrid), len(obstacleGrid[0])
    if obstacleGrid[0][0] == 1 or obstacleGrid[n - 1][m - 1]:
        return 0
    
    dp = [[-1 for col in range(m)] for row in range(n)]


    return self.uniquePathsWithObstacles_memo(obstacleGrid, 0, 0, n - 1, m - 1, dirs, dp)

# ===============================================================
# Program 3: 64. Minimum Path Sum
# URL: https://leetcode.com/problems/minimum-path-sum/description/
# ===============================================================
def minPathSum_memo(self, grid, sr, sc, dr, dc, dirs, dp):
    if sr == dr and sc == dc:
        dp[sr][sc] = grid[sr][sc]
        return dp[sr][sc]

    if dp[sr][sc] != 0:
        return dp[sr][sc]
    
    min_path_sum = int(1e8)
    for dir in dirs:
        nr = sr + dir[0]
        nc = sc + dir[1]

        if nr >= 0 and nr <= dr and nc >= 0 and nc <= dc:
            min_path_sum = min(self.minPathSum_memo(grid, nr, nc, dr, dc, dirs, dp), min_path_sum)

    dp[sr][sc] = min_path_sum + grid[sr][sc]
    return dp[sr][sc]

def minPathSum(self, grid: list[list[int]]) -> int:
    dirs = [[0, 1],[1, 0]]
    dp = [[0 for col in range(len(grid[0]))] for row in range(len(grid))]

    return self.minPathSum_memo(grid, 0, 0, len(grid) - 1, len(grid[0]) - 1, dirs, dp)