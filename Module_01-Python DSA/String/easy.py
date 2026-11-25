# ============================================================================
# program 1 : 67. Add Binary
# url : https://leetcode.com/problems/add-binary/description/?envType=problem-list-v2&envId=string
# ============================================================================
def addBinary(self, a: str, b: str) -> str:
    carry = 0
    idx1 = len(a) - 1
    idx2 = len(b) - 1
    res = ""

    while idx1 >= 0 or idx2 >= 0 or carry != 0:
        sum = carry

        if idx1 >= 0:
            sum += int(a[idx1])
        
        if idx2 >= 0:
            sum += int(b[idx2])
        
        quo = sum // 2 # quotient
        rem = sum % 2 # remainder

        res = str(rem) + res
        carry = quo
        idx1 -= 1
        idx2 -= 1
    
    
    return res

# ============================================================================
# program 2 : 14. Longest Common Prefix
# url : https://leetcode.com/problems/longest-common-prefix/?envType=problem-list-v2&envId=string
# ============================================================================
def longestCommonPrefix(self, strs: list[str]) -> str:
    pref = ""
    min_len = float("inf")
    outer_idx = 0
    is_common = True

    for str in strs:
        min_len = min(min_len, len(str))
    
    while outer_idx < min_len:
        inner_idx = 1
        while inner_idx < len(strs):
            if strs[inner_idx][outer_idx] != strs[inner_idx - 1][outer_idx]:
                is_common = False
                break
            inner_idx += 1
        
        if not is_common:
            break

        pref += strs[0][outer_idx]
        outer_idx += 1

    return pref

# ============================================================================
# program 3 : 168. Excel Sheet Column Title
# url : https://leetcode.com/problems/excel-sheet-column-title/?envType=problem-list-v2&envId=string
# ============================================================================
def convertToTitle(self, columnNumber: int) -> str:
    res = ""

    while columnNumber != 0:
        columnNumber -= 1

        rem = columnNumber % 26

        res += chr(ord('A') + rem)

        columnNumber = columnNumber // 26

    return res[::-1]