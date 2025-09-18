import heapq


class MinHeap:
    def __init__(self):
        self._heap = []

    def push(self, key, data):
        heapq.heappush(self._heap, (key, data))

    def pop(self):
        return heapq.heappop(self._heap)

    def get_min(self):
        return self._heap[0]

    def __len__(self):
        return len(self._heap)

    def __add__(self, other):
        return self._heap + other._heap


class MaxHeap:
        def __init__(self):
            self.min_heap = MinHeap()

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


