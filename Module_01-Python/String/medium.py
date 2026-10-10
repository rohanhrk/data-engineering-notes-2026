from array import List
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

# ===============================================================
# program 3: 49. Group Anagrams
# URL: https://leetcode.com/problems/group-anagrams/
# ===============================================================
def getCommonString(self, string):
    freq = [0] * 26
    commonStr = ""

    for ch in string:
        freq[ord(ch) - ord('a')] += 1

    for i in range(len(freq)):
        if freq[i] != 0:
            commonStr += chr(i + ord('a'))
            commonStr += str(freq[i])
    return commonStr
def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
    map = {}
    ans = []
    for str in strs:
        commonStr = self.getCommonString(str)
        map.setdefault(commonStr, [])
        map.get(commonStr).append(str)

    for list in map.values():
        ans.append(list)

    return ans

# ===============================================================
# program 4: 424. Longest Repeating Character Replacement
# URL: https://leetcode.com/problems/longest-repeating-character-replacement/
# ===============================================================
def characterReplacement(self, s: str, k: int) -> int:
    start_idx = end_idx = 0
    maxFreqCount = 0
    maxFreqChar = ""
    freq = [0]*26
    max_ss = 0

    while end_idx < len(s):
        end_ch = s[end_idx]
        freq[ord(end_ch) - ord('A')] += 1

        if freq[ord(end_ch) - ord('A')] > maxFreqCount:
            maxFreqCount = freq[ord(end_ch) - ord('A')]
            maxFreqChar = end_ch
        
        if (end_idx - start_idx + 1) - maxFreqCount > k:
            start_ch = s[start_idx]
            freq[ord(start_ch) - ord('A')] -= 1
            start_idx += 1

            if start_ch == maxFreqChar:
                maxFreqCount -= 1
            
        max_ss = max(max_ss, end_idx - start_idx + 1)
        end_idx += 1
    
    return max_ss

# ===============================================================
# program 5: 131. Palindrome Partitioning
# URL: https://leetcode.com/problems/palindrome-partitioning/
# ===============================================================
def isPalindrome(self, str):
    if len(str) <= 1:
        return str

    rows = cols = len(str)
    gap = 0
    dp = [[False for _ in range(cols)] for _ in range(rows)]

    while gap < rows:
        row = 0
        col = gap

        while row < rows and col < cols:
            if gap == 0:
                dp[row][col] = True
            elif gap == 1:
                dp[row][col] = True if str[row] == str[col] else False
            else:
                dp[row][col] = True if str[row] == str[col] and dp[row + 1][col - 1] else False

            row += 1
            col += 1
        gap += 1
    
    return dp[0][cols - 1]

def partition_rec(self, s, length):
    if length == 0:
        return [[]]

    myRes = []
    for cut in range(len(s) - 1, -1, -1):
        if self.isPalindrome(s[cut:length]):
            recRes = self.partition_rec(s, cut)
            for list in recRes:
                list.append(s[cut:length])
                myRes.append(list)
    return myRes
def partition(self, s: str) -> list[list[str]]:
    return self.partition_rec(s, len(s))