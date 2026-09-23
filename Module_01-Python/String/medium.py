# ============================================================================
# program 1 : 6. Zigzag Conversion
# url : https://leetcode.com/problems/zigzag-conversion/description/
# ============================================================================
def convert(self, s: str, numRows: int) -> str:
    row = 0
    stored_res = [""]*numRows
    idx = 0

    while idx < len(s):
        if row % 2 == 0:
            col = 0
            while col < numRows and idx < len(s):
                stored_res[col] += s[idx]
                col += 1
                idx += 1     
        elif row % 2 != 0:
            col = numRows - 2
            while col > 0 and idx < len(s):
                stored_res[col] += s[idx]
                col -= 1
                idx += 1
        
        row += 1
    
    res = ""
    for str in stored_res:
        res += str
    
    return res

# ===============================================================
# program 2: 5. Longest Palindromic Substring
# URL: https://leetcode.com/problems/longest-palindromic-substring/description/
# ===============================================================

def longestPalindrome(self, s: str) -> str:
    rows = len(s)
    cols = len(s)

    matrix = [[False for _ in range(cols)] for _ in range(rows)]
    long_len = 0
    long_pal_str = ""

    for gap in range(rows):
        row = 0
        col = gap

        while row < rows and col < cols:
            if gap == 0:
                matrix[row][col] = True
            elif gap == 1 and s[row] == s[col]:
                matrix[row][col] = True
            elif s[row] == s[col] and matrix[row + 1][col - 1]:
                matrix[row][col] = True
            else:
                matrix[row][col] = False
            
            if matrix[row][col] and col - row + 1 > long_len:
                long_len = col - row + 1
                long_pal_str = s[row:col + 1]

            row += 1
            col += 1
    
    return long_pal_str

