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

# ===============================================================
# Program 4: 72. Edit Distance
# URL: https://leetcode.com/problems/edit-distance/
# ===============================================================
def minDistance_memo(self, word1, len1, word2, len2, dp):
    if len1 == 0 or len2 == 0:
        if len1 == 0 and len2 == 0:
            dp[len1][len2] = 0
            return dp[len1][len2]
        elif len1 == 0:
            dp[len1][len2] = len2
            return dp[len1][len2]
        else:
            dp[len1][len2] = len1
            return dp[len1][len2]

    if dp[len1][len2] != -1:
        return dp[len1][len2]
        
    min_dist = float("inf")
    if word1[len1 - 1] == word2[len2 - 1]:
        min_dist = self.minDistance_memo(word1, len1 - 1, word2, len2 - 1, dp)
        dp[len1][len2] = min_dist
        return dp[len1][len2]
    
    inset = self.minDistance_memo(word1, len1, word2, len2 - 1, dp)
    delete = self.minDistance_memo(word1, len1 - 1, word2, len2, dp)
    replace = self.minDistance_memo(word1, len1 - 1, word2, len2 - 1, dp)

    min_dist = min(inset, delete, replace) + 1
    dp[len1][len2] = min_dist
    return dp[len1][len2]
def minDistance(self, word1: str, word2: str) -> int:
    len1 = len(word1)
    len2 = len(word2)

    dp = [[-1 for _ in range(len2 + 1)] for _ in range(len1 + 1)]
    return self.minDistance_memo(word1, len(word1), word2, len(word2), dp)