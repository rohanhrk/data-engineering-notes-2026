# ============================================================================
# program 1 : 49. Group Anagrams
# url : https://leetcode.com/problems/group-anagrams/description/
# ============================================================================
def getCommonString(self, string):
    freq = [0] * 26
    commonStr = ""

    for ch in string:
        freq[ord(ch) - ord('a')] += 1

    for i in range(len(freq)):
        if freq[i] != 0:
            commonStr += chr(i + ord('a'))
            commonStr += str(freq[i])
    print(commonStr)
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

# ============================================================================
# program 2 : 128. Longest Consecutive Sequence
# url : https://leetcode.com/problems/longest-consecutive-sequence/
# ============================================================================
def longestConsecutive(self, nums: list[int]) -> int:
    max_conse_len = 0
    map = {} # num vs freq

    for ele in nums:
        map[ele] = map.get(ele, 0) + 1
    
    for ele in nums:
        if ele not in map:
            continue
        
        map.pop(ele)

        left_elem = ele - 1
        right_elem = ele + 1

        while left_elem in map:
            map.pop(left_elem)
            left_elem -= 1
        
        while right_elem in map:
            map.pop(right_elem)
            right_elem += 1

        max_conse_len = max(max_conse_len, right_elem - left_elem - 1)
    
    return max_conse_len