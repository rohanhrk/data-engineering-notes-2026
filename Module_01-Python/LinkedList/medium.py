class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# ============================================================================
# program 1 : 148. Sort List
# url : https://leetcode.com/problems/sort-list/
# ============================================================================
def getMidNode(self, head):
    if head == None or head.next == None:
        return head
    slow = fast = head

    while fast.next != None and fast.next.next != None:
        slow = slow.next
        fast = fast.next.next
    
    return slow

def mergeSortList(self, left, right):
    dummy = ListNode(-1)
    prev = dummy

    curr1 = left
    curr2 = right

    while curr1 != None and curr2 != None:
        if curr1.val <= curr2.val:
            prev.next = curr1
            curr1 = curr1.next
        else:
            prev.next = curr2
            curr2 = curr2.next
        
        prev = prev.next
    
    if curr1 != None:
        prev.next = curr1
    if curr2 != None:
        prev.next = curr2
    
    head = dummy.next
    dummy.next = None

    return head

def sortList(self, head: ListNode | None) -> ListNode | None:
    if head == None or head.next == None:
        return head

    mid = self.getMidNode(head)
    newH = mid.next
    mid.next = None

    left_list = self.sortList(head)
    right_list = self.sortList(newH)

    return self.mergeSortList(left_list, right_list)