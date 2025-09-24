import heapq

class MinHeap:
    def __init__(self, max_size=float('inf')):
        self._heap = []
        self._max_size = max_size

    def push(self, key, data):
        def normal_push():
            heapq.heappush(self._heap, (key, data))

        normal_push()
        if len(self) > self._max_size:
            self.pop()

    def pop(self):
        return heapq.heappop(self._heap)

    def get_min(self) -> tuple:
        return self._heap[0]

    def __len__(self) -> int:
        return len(self._heap)

    def __iadd__(self, other) -> 'MinHeap':
        for elem in other._heap:
            self.push(*elem)
        return self


class MaxHeap:
    def __init__(self, max_size=float('inf')):
        self._max_size = max_size
        self.min_heap = MinHeap(max_size)

    def push(self, key, data):
        self.min_heap.push(-key, data)

    def pop(self):
        key, data = self.min_heap.pop()
        return -key, data

    def get_max(self):
        key, data = self.min_heap.get_min()
        return -key, data

    def __len__(self):
        return self.min_heap.__len__()

    def __add__(self, other):
        return self.min_heap + other.min_heap
