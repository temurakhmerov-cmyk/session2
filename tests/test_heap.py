import unittest
from queue_sys.heap import MinHeap

class TestMinHeap(unittest.TestCase):
    def setUp(self):
        self.heap = MinHeap()

    def test_empty_heap(self):
        """Тест поведения пустой кучи."""
        self.assertTrue(self.heap.is_empty())
        self.assertEqual(self.heap.size(), 0)
        self.assertIsNone(self.heap.peek())
        self.assertIsNone(self.heap.extract_min())

    def test_single_element(self):
        """Тест кучи с одним элементом."""
        self.heap.insert("Job A", 2)
        self.assertFalse(self.heap.is_empty())
        self.assertEqual(self.heap.size(), 1)
        self.assertEqual(self.heap.peek(), "Job A")
        self.assertEqual(self.heap.extract_min(), "Job A")
        self.assertTrue(self.heap.is_empty())

    def test_multiple_elements_ordered(self):
        """Тест правильности порядка извлечения при разных приоритетах."""
        self.heap.insert("Job Low", 3)
        self.heap.insert("Job High", 1)
        self.heap.insert("Job Medium", 2)

        self.assertEqual(self.heap.size(), 3)
        self.assertEqual(self.heap.peek(), "Job High")

        # Извлечение должно идти в порядке возрастания приоритета (1, затем 2, затем 3)
        self.assertEqual(self.heap.extract_min(), "Job High")
        self.assertEqual(self.heap.extract_min(), "Job Medium")
        self.assertEqual(self.heap.extract_min(), "Job Low")
        self.assertTrue(self.heap.is_empty())

    def test_heap_stability_fifo(self):
        """Тест стабильности кучи (FIFO для одинаковых приоритетов)."""
        # Вставляем три задачи с одинаковым приоритетом 2 в разное время
        self.heap.insert("Job 1", 2)
        self.heap.insert("Job 2", 2)
        self.heap.insert("Job 3", 2)

        # Они должны извлекаться строго в порядке добавления (Job 1 -> Job 2 -> Job 3)
        self.assertEqual(self.heap.extract_min(), "Job 1")
        self.assertEqual(self.heap.extract_min(), "Job 2")
        self.assertEqual(self.heap.extract_min(), "Job 3")
        self.assertTrue(self.heap.is_empty())

    def test_mixed_priorities_stability(self):
        """Смешанный тест: разные приоритеты и одинаковые приоритеты."""
        self.heap.insert("Medium 1", 2)
        self.heap.insert("High 1", 1)
        self.heap.insert("Medium 2", 2)
        self.heap.insert("Low 1", 3)
        self.heap.insert("High 2", 1)

        # Ожидаемый порядок извлечения:
        # 1. High 1 (приоритет 1, добавлен первым)
        # 2. High 2 (приоритет 1, добавлен вторым)
        # 3. Medium 1 (приоритет 2, добавлен первым)
        # 4. Medium 2 (приоритет 2, добавлен вторым)
        # 5. Low 1 (приоритет 3)
        self.assertEqual(self.heap.extract_min(), "High 1")
        self.assertEqual(self.heap.extract_min(), "High 2")
        self.assertEqual(self.heap.extract_min(), "Medium 1")
        self.assertEqual(self.heap.extract_min(), "Medium 2")
        self.assertEqual(self.heap.extract_min(), "Low 1")
        self.assertTrue(self.heap.is_empty())

if __name__ == "__main__":
    unittest.main()
