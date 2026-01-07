class Solution(object):
    def reverseVowels(self, s):
        s_list = list(s)
        vowels = set("aeiouAEIOU")

        i = 0
        j = len(s_list) - 1

        while i < j:
           
            if s_list[i] not in vowels:
                i += 1
            
            elif s_list[j] not in vowels:
                j -= 1
            
            else:
                s_list[i], s_list[j] = s_list[j], s_list[i]
                i += 1
                j -= 1

        return "".join(s_list)