class Solution(object):
    def minLength(self, s):
        """
        :type s: str
        :rtype: int
        """
        stack = []
        
        for char in s:
            
            if not stack:
                stack.append(char)
                continue
            
            
            top = stack[-1]
            
            
            if char == 'B' and top == 'A':
                stack.pop() 
                
            
            elif char == 'D' and top == 'C':
                stack.pop() 
                
            
            else:
                stack.append(char)
        
        
        return len(stack)