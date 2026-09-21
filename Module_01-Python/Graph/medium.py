# ============================================================================
# program 1 : 79. Word Search
# url : https://leetcode.com/problems/word-search/description/
# ============================================================================
def exist_dfs(self, board, sr, sc, word, idx, rows, cols, dirs):
    if idx == len(word):
        return True
    
    if board[sr][sc] != word[idx]:
        return False

    if idx == len(word) - 1:
        return True

    ch = board[sr][sc]
    board[sr][sc] = '1' # marked as visited
    flag = False
    for dir in dirs:
        nr = sr + dir[0]
        nc = sc + dir[1]

        if nr >= 0 and nr < rows and nc >= 0 and nc < cols and board[nr][nc] != '1':
            flag = flag or self.exist_dfs(board, nr, nc, word, idx + 1, rows, cols, dirs)

    board[sr][sc] = ch
    return flag
def exist(self, board: list[list[str]], word: str) -> bool:
    dirs = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    rows = len(board)
    cols = len(board[0])
    if rows == 1 and cols == 1 and len(word) == 1:
        return board[0][0] == word
    for sr in range(rows):
        for sc in range(cols):
            if board[sr][sc] == word[0] and self.exist_dfs(board, sr, sc, word, 0, rows, cols, dirs):
                return True

    return False