
def _binary_search(
    array: list[int],
    low: int,
    high: int,
    target
    ) -> int:
    mid = (low + high) // 2
    
    if target == array[mid]:
        return mid
    
    if target > array[mid]:
        return _binary_search(array, mid + 1, high, target)
    else:
        return _binary_search(array, low, mid - 1, target)

        
def binary_search(array: list[int], target: int):
    return _binary_search(array, 0, len(array) - 1, target)



array = [1, 2, 3, 7, 8]
found = binary_search(array, 8)
print("FOUND AT INDEX: ", found)
