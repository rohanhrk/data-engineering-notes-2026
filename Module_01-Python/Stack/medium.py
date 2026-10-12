# ===============================================================
# program 1: 150. Evaluate Reverse Polish Notation
# URL: https://leetcode.com/problems/evaluate-reverse-polish-notation/
# ===============================================================
def addition(self, val1, val2):
    return val1 + val2

def substraction(self, val1, val2):
    return val1 - val2

def multiplication(self, val1, val2):
    return val1 * val2

def division(self, val1, val2):
    return int(val1 / val2)

def evalRPN(self, tokens: list[str]) -> int:
    stack = []

    for token in tokens:
        if token in ("+", "-", "*", "/"):
            val2 = stack.pop()
            val1 = stack.pop()
            val = 0

            if token == "+":
                val = self.addition(val1, val2)
            elif token == "-":
                val = self.substraction(val1, val2)
            elif token == "*":
                val = self.multiplication(val1, val2)
            else:
                val = self.division(val1, val2)
            
            stack.append(val)
        else:
            stack.append(int(token))
    
    return int(stack.pop())