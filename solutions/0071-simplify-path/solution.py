class Solution(object):
    def simplifyPath(self, path):
        stack = []
        s = path.split('/')
        for ch in s:
            if ch == "" or ch == ".":
                continue
            elif ch == "..":
                if stack:
                    stack.pop()
            else:
                stack.append(ch)
    
        return '/' + '/'.join(stack)



        """
        :type path: str
        :rtype: str
        """
        