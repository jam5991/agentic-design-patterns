"""
Initial Program for OpenEvolve Evolution
=========================================
This is a simple sorting function that OpenEvolve will attempt to optimize.
The algorithm starts as a basic bubble sort and can be evolved into more
efficient implementations.

This file contains the code that will be evolved by OpenEvolve.
Mark sections with # @evolve comments to indicate which parts can be modified.
"""


# EVOLVE-BLOCK-START
def sort_numbers(arr: list[int]) -> list[int]:
    """
    Sort a list of numbers in ascending order.
    
    This is the target function for evolution. OpenEvolve will attempt
    to improve its performance while maintaining correctness.
    
    Args:
        arr: A list of integers to sort
        
    Returns:
        A new list with elements sorted in ascending order
    """
    # Basic bubble sort - initial implementation to be evolved
    result = arr.copy()
    n = len(result)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    
    return result
# EVOLVE-BLOCK-END


if __name__ == "__main__":
    # Test the sorting function
    test_data = [64, 34, 25, 12, 22, 11, 90]
    sorted_data = sort_numbers(test_data)
    print(f"Original: {test_data}")
    print(f"Sorted: {sorted_data}")
