from typing import List

def jump(nums: List[int]) -> int:
    n = len(nums)
    if n == 1:
        return 0
    
    jumps = 0       
    current_end = 0    
    farthest = 0   
    
    for i in range(n - 1):
        farthest = max(farthest, i + nums[i])
        
        if i == current_end:
            jumps += 1          
            current_end = farthest
            
            if current_end >= n - 1:
                return jumps
    
    return jumps


print("Пример 1:")
nums1 = [2, 3, 1, 1, 4]
print(f"nums = {nums1}")
print(f"Минимальное количество прыжков: {jump(nums1)}")
print()

print("Пример 2:")
nums2 = [2, 3, 0, 1, 4]
print(f"nums = {nums2}")
print(f"Минимальное количество прыжков: {jump(nums2)}")
print()

test_cases = [
    ([1, 2, 3, 4, 5], 3),
    ([5, 4, 3, 2, 1], 1),
    ([1, 1, 1, 1, 1], 4),
    ([0], 0),
    ([2, 1], 1),
    ([7, 0, 9, 6, 9, 6, 1, 7, 9, 0, 1, 2, 9, 0, 3], 2),
]

print("Дополнительные тесты:")
for i, (nums, expected) in enumerate(test_cases):
    result = jump(nums)
    print(f"Тест {i+1}: nums={nums}")
    print(f"  Ожидалось: {expected}, Получилось: {result}")
    print(f"  Результат: {'✓' if result == expected else '✗'}")
    print()