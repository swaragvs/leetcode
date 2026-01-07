class Solution(object):
    def isValid(self, s):
        stack = []
        
        for char in s:
            if char == '(' or char == '{' or char == '[':
                stack.append(char)
            else:
                if len(stack) == 0:
                    return False
                top = stack[-1]
                if char == ')' and top == '(':
                    stack.pop()
                elif char == '}' and top == '{':
                    stack.pop()
                elif char == ']' and top == '[':
                    stack.pop()
                else:
                    return False
        
        
        if len(stack) == 0:
            return True
        else:
            return False