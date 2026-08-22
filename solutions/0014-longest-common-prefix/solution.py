class Solution(object):
    def longestCommonPrefix(self, strs):
        k = len(min(strs, key=len))
        s = ""

        for i in range(k):
            chars = []

            for j in range(len(strs)):
                chars.append(strs[j][i])

            if len(set(chars)) != 1:
                return s

            s += chars[0]

        return s













        """
        :type strs: List[str]
        :rtype: str
        """
        