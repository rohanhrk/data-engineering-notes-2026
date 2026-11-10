class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# ===============================================================
# program 1: 938. Range Sum of BST
# URL: https://leetcode.com/problems/range-sum-of-bst/description/
# ===============================================================

def rangeSumBST(self, root: TreeNode | None, low: int, high: int) -> int:
    if root == None:
        return 0
        
    if root == None:
        return 0
    
    sum = root.val if low <= root.val <= high else 0
    if root.val > low:
        sum += self.rangeSumBST(root.left, low, high)
    
    if root.val < high:
        sum += self.rangeSumBST(root.right, low, high)
    
    return sum