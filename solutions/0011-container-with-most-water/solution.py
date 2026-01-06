class Solution(object):
    def maxArea(self, height):
        mw = 0 
        i = 0 
        j = len(height)-1
        while(i<j):
            h=min(height[i],height[j])
            b=j-i
            cw=h*b
            mw=max(cw,mw)

            if height[i] < height[j]:
                i += 1
            else:
                j -= 1
                
        return mw

        """
        :type height: List[int]
        :rtype: int
        """
        