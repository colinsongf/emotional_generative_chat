# coding=utf-8

'''

方法就是二分查找，但是很烧脑

'''

# https://leetcode-cn.com/problems/search-in-rotated-sorted-array/

class Solution(object):
  def search(self, nums, target):
    """
    :type nums: List[int]
    :type target: int
    :rtype: int
    """
    i = 0
    j = len(nums) - 1
    while i <= j:
      idx = (i + j) // 2
      if nums[idx] == target:
        return idx
      c = nums[idx]
      '''
      中点位于左边升序数组
        目标值小于中点,目标值大于等于左端点 - 目标值在左边升序数组的中点的左边
        否则 - 目标值位于左边升序数组的中点的右边或右边升序数组
      中点位于右边升序数组
        目标值大于中点，目标值小于左端点 - 目标值在右边升序数组的中点的右边
        否则 - 目标值位于左边升序数组或右边升序数组的中点的左边
      '''
      if c >= nums[0]:
        if target < c and target >= nums[0]:
          j = idx - 1
        else:
          i = idx + 1
      else:
        if target > c and target < nums[0]:
          i = idx + 1
        else:
          j = idx - 1
    return -1