class Solution(object):
    def moveZeroes(self, nums):
        j = 0 
        for i in range(len(nums)):
            if nums[i]!=0:
                nums[j]=nums[i]
                j += 1
        for k in range(j,len(nums)):
            nums[k] = 0
        """
        :type nums: List[int]
        :rtype: None Do not return anything, modify nums in-place instead.
        """
        