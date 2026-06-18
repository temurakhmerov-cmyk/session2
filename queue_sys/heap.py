class MinHeap:
    """
    Собственная реализация двоичной кучи (Min-Heap) для приоритетной очереди.
    Гарантирует стабильность (FIFO) для одинаковых приоритетов с помощью счетчика порядка вставки.
    """
    def __init__(self):
        self.heap = []      # Список для хранения элементов в виде кортежей (priority, order_id, item)
        self.counter = 0    # Счетчик порядка вставки для обеспечения стабильности (FIFO)

    def is_empty(self) -> bool:
        """Проверяет, пуста ли куча."""
        return len(self.heap) == 0

    def size(self) -> int:
        """Возвращает количество элементов в куче."""
        return len(self.heap)

    def peek(self):
        """
        Возвращает элемент с наивысшим приоритетом (минимальным значением priority)
        без удаления его из кучи. Возвращает None, если куча пуста.
        """
        if self.is_empty():
            return None
        return self.heap[0][2]

    def insert(self, item, priority: int):
        """
        Вставляет элемент в кучу с заданным приоритетом.
        """
        # Кортеж для сравнения: (приоритет, уникальный порядковый номер, сам объект)
        # Python сравнивает кортежи поэлементно: сначала priority, затем counter.
        entry = (priority, self.counter, item)
        self.counter += 1
        self.heap.append(entry)
        self._sift_up(len(self.heap) - 1)

    def extract_min(self):
        """
        Извлекает и возвращает элемент с наивысшим приоритетом (минимальным значением).
        Возвращает None, если куча пуста.
        """
        if self.is_empty():
            return None

        # Сохраняем корневой элемент (с минимальным приоритетом)
        root_item = self.heap[0][2]

        if len(self.heap) == 1:
            self.heap.pop()
        else:
            # Перемещаем последний элемент на место корня
            self.heap[0] = self.heap.pop()
            # Просеиваем его вниз для восстановления свойств кучи
            self._sift_down(0)

        return root_item

    def _sift_up(self, index: int):
        """Просеивание элемента вверх для восстановления свойств кучи."""
        parent_index = (index - 1) // 2
        
        # Пока мы не в корне и текущий элемент меньше родителя
        while index > 0 and self.heap[index] < self.heap[parent_index]:
            # Меняем местами с родителем
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            index = parent_index
            parent_index = (index - 1) // 2

    def _sift_down(self, index: int):
        """Просеивание элемента вниз для восстановления свойств кучи."""
        size = len(self.heap)
        
        while True:
            left_child = 2 * index + 1
            right_child = 2 * index + 2
            smallest = index

            # Сравниваем с левым сыном
            if left_child < size and self.heap[left_child] < self.heap[smallest]:
                smallest = left_child

            # Сравниваем с правым сыном
            if right_child < size and self.heap[right_child] < self.heap[smallest]:
                smallest = right_child

            # Если минимальный элемент - не текущий, меняем их местами и продолжаем
            if smallest != index:
                self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
                index = smallest
            else:
                break

    def get_array(self):
        """
        Возвращает плоский список элементов кучи (без служебной информации о счетчике)
        в том порядке, в котором они хранятся в массиве двоичного дерева.
        Полезно для визуализации.
        """
        return [{"priority": entry[0], "order": entry[1], "item": entry[2]} for entry in self.heap]

    def clear(self):
        """Очищает кучу."""
        self.heap = []
        self.counter = 0
