class Solution:
    def combinationSum(self, candidates: list[int], target: int) -> list[list[int]]:
        return_list = []
        for i in range(candidates):

            if target % candidates[i] == 0:
                a = 5
            for j in range(i, candidates):
                a = 5

a = Solution()
candidates = [2,3,6,7]
target = 7
a.combinationSum(candidates, target)