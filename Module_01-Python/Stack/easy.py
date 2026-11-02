# ===============================================================
# program 1: 20. Valid Parentheses
# URL: https://leetcode.com/problems/valid-parentheses/
# ===============================================================
def isOpenBracket(self, bracket):
    isOpenBracket = bracket in {'(', '{', '['}
    return isOpenBracket
def isValid(self, s: str) -> bool:
    stack = []
    for ch in s:
        if self.isOpenBracket(ch):
            stack.append(ch)
        else:
            if len(stack) == 0:
                return False
            
            openBracket = stack.pop()
            if (ch == ')' and openBracket != '(') or (ch == '}' and openBracket != '{') or (ch == ']' and openBracket != '['):
                return False
            
    return len(stack) == 0