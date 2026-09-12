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