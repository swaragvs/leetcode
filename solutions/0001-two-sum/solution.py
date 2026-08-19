class Solution(object):
    def twoSum(self, nums, target):
        seen = {}
        
        for i in range(len(nums)):
            needed = target - nums[i] 
            if needed in seen:
                return [seen[needed],i]
            
            seen[nums[i]] = i
        
        # for i in range(len(nums)):
        #     m = i
        #     for j in range(i+1,len(nums)):
        #         n = j
        #         if nums[m]+nums[n]==target:
        #             return [m,n]
        
        
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        