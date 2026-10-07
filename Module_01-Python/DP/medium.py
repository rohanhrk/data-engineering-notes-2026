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

# ===============================================================
# Program 5: 91. Decode Ways
# URL: https://leetcode.com/problems/decode-ways/
# ===============================================================
def numDecodings_memo(self, s, idx, dp):
    if idx == len(s):
        dp[idx] = 1
        return dp[idx]

    one = 0
    two = 0

    if s[idx] == '0':
        dp[idx] = 0
        return dp[idx]
    
    if dp[idx] != -1:
        return dp[idx]
        
    one = self.numDecodings_memo(s, idx + 1, dp)

    if idx <= len(s) - 2:
        num = int(s[idx]) * 10 + int(s[idx + 1])
        if num >= 10 and num <= 26:
            two = self.numDecodings_memo(s, idx + 2, dp)
    
    dp[idx] = one + two
    return dp[idx] 
def numDecodings(self, s: str) -> int:
    dp = [-1 for _ in range(len(s) + 1)]
    return self.numDecodings_memo(s, 0, dp)

# ===============================================================
# program 6: 120. Triangle
# URL: https://leetcode.com/problems/triangle/
# ===============================================================
def minimumTotal_memo(self, triangle, sr, sc, dr, dirs, dp):
    if sr == dr:
        dp[sr][sc] = triangle[sr][sc]
        return dp[sr][sc]

    if dp[sr][sc] != float("-inf"):
        return dp[sr][sc]

    min_path_sum = float("inf")
    for dir in dirs:
        nr = sr + dir[0]
        nc = sc + dir[1]

        if nr >= 0 and nr <= dr and nc >= 0 and nc < len(triangle[nr]):
            min_path_sum = min(min_path_sum, self.minimumTotal_memo(triangle, nr, nc, dr, dirs, dp))
    
    dp[sr][sc] = min_path_sum + triangle[sr][sc]
    return dp[sr][sc]

def minimumTotal(self, triangle: list[list[int]]) -> int:
    dirs = [[1, 0], [1, 1]]
    rows = len(triangle)
    dp = [[float("-inf") for _ in range(len(triangle[row]))] for row in range(rows)]
    return self.minimumTotal_memo(triangle, 0, 0, rows - 1, dirs, dp)

# ===============================================================
# program 7: 97. Interleaving String
# URL: https://leetcode.com/problems/interleaving-string/
# ===============================================================
# 1 -> True, 0 -> False, -1 -> Unknown
def isInterleave_tabu(self, s1, IDX1, s2, IDX2, s3, IDX3, dp):
    for idx3 in range(len(s3), IDX3 - 1, -1):
        for idx2 in range(len(s2), IDX2 - 1, -1):
            for idx1 in range(len(s1), IDX1 - 1, -1):
                if idx3 == len(s3):
                    dp[idx1][idx2][idx3] = 1
                    continue

                if idx1 < len(s1) and idx2 < len(s2) and s1[idx1] != s3[idx3] and s2[idx2] != s3[idx3]:
                    dp[idx1][idx2][idx3] = 0
                    continue

                flag = False
                
                if idx1 < len(s1) and s1[idx1] == s3[idx3]:
                    flag = dp[idx1 + 1][idx2][idx3 + 1] == 1 or flag
                if idx2 < len(s2) and s2[idx2] == s3[idx3]:
                    flag = self.isInterleave_memo(s1, idx1, s2, idx2 + 1, s3, idx3 + 1, dp) == 1 or flag
                
                dp[idx1][idx2][idx3] = 1 if flag else 0
    
    return dp[IDX1][IDX2][IDX3]

def isInterleave_memo(self, s1, idx1, s2, idx2, s3, idx3, dp):
    if idx3 == len(s3):
        dp[idx1][idx2][idx3] = 1
        return dp[idx1][idx2][idx3]

    if idx1 < len(s1) and idx2 < len(s2) and s1[idx1] != s3[idx3] and s2[idx2] != s3[idx3]:
        dp[idx1][idx2][idx3] = 0
        return dp[idx1][idx2][idx3]

    if dp[idx1][idx2][idx3] != -1:
        return dp[idx1][idx2][idx3]

    flag = False
    
    if idx1 < len(s1) and s1[idx1] == s3[idx3]:
        flag = self.isInterleave_memo(s1, idx1 + 1, s2, idx2, s3, idx3 + 1, dp) == 1 or flag
    if idx2 < len(s2) and s2[idx2] == s3[idx3]:
        flag = self.isInterleave_memo(s1, idx1, s2, idx2 + 1, s3, idx3 + 1, dp) == 1 or flag
    
    dp[idx1][idx2][idx3] = 1 if flag else 0
    return dp[idx1][idx2][idx3] 

def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
    len1 = len(s1)
    len2 = len(s2)
    len3 = len(s3)

    dp = [[[-1 for _ in range(len(s3) + 1)] for _ in range(len(s2) + 1)] for _ in range(len(s1) + 1)]

    if len1 + len2 != len3:
        return False

    return self.isInterleave_tabu(s1, 0, s2, 0, s3, 0, dp) == 1