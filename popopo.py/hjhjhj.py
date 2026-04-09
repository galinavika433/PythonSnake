def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]  # текущий элемент для вставки
        j = i - 1
        # Сдвигаем элементы, которые больше key, вправо
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

# Пример использования
data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = insertion_sort(data)
print("Отсортированный массив:", sorted_data)
