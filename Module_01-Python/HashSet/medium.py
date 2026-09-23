# ===============================================================
# Program 1: 3. Longest Substring Without Repeating Characters
# URL: https://leetcode.com/problems/longest-substring-without-repeating-characters/
# ===============================================================
def lengthOfLongestSubstring(self, s: str) -> int:
    st = 0
    end = 0
    long_len = 0
    ch_set = set()
    
    while end < len(s):
        if s[end] in ch_set:
            long_len = max(long_len, end - st)

            while st < end and s[end] in ch_set:
                ch_set.remove(s[st])
                st += 1
        
        ch_set.add(s[end])
        end += 1
    
    long_len = max(long_len, end - st)
    return long_len