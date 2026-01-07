class Solution(object):
    def clearDigits(self, s):

        stack = [] 
        for char in s: 
            if char.isdigit():
                if stack:
                    stack.pop()
            else:
                stack.append(char)
        return "".join(stack)
        """
        :type s: str
        :rtype: str
        """
        