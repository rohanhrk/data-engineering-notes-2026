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

# ============================================================================
# program 2 : 143. Reorder List
# url : https://leetcode.com/problems/reorder-list/description/
# ============================================================================

def get_mid_node(self, head):
    slow = fast = head

    while fast.next != None and fast.next.next != None:
        slow = slow.next
        fast = fast.next.next

    return slow

def reverse(self, head):
    prev = None
    curr = head

    while curr != None:
        forw = curr.next

        curr.next = prev

        prev = curr
        curr = forw
    
    return prev
    
def reorderList(self, head: ListNode | None) -> None:
    """
    Do not return anything, modify head in-place instead.
    """
    if head == None or head.next == None:
        return head

    mid_node = self.get_mid_node(head)

    # break the linkage and make new head
    new_head = mid_node.next
    mid_node.next = None

    # reverse new head list
    new_head = self.reverse(new_head)

    dummy_node = ListNode(-1)
    prev = dummy_node
    curr1 = head
    curr2 = new_head

    while curr1 != None and curr2 != None:
        prev.next = curr1
        prev = curr1
        curr1 = curr1.next

        prev.next = curr2
        prev = curr2
        curr2 = curr2.next

    if curr1 != None:
        prev.next = curr1
        prev = curr1

        curr1 = curr1.next

    if curr2 != None:
        prev.next = curr2
        prev = curr2
        curr2 = curr2.next