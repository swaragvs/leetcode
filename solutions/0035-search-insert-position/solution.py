class Solution(object):
    def searchInsert(self, nums, target):
        left = 0
        right = len(nums) - 1 
        middle = (left + right) // 2

        while  left <= right:
            middle = (left + right) // 2

            if target == nums[middle]:
                return middle

            if target > nums[middle]:
                left = middle + 1
                
            else:
                right = middle - 1
        
                
        
        return left
        


        """
        :type nums: List[int]
        :type target: int
        :rtype: int
        """
        