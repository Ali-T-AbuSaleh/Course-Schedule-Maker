import heapq
from copy import deepcopy


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

    def parse_to_list(self):
        return deepcopy([val for key, val in self._heap])

    def __len__(self) -> int:
        return len(self._heap)

    def __iadd__(self, other) -> 'MinHeap':
        for elem in other._heap:
            self.push(*elem)
        return self


class MaxHeap(MinHeap):
    def __init__(self, max_size=float('inf')):
        super().__init__(max_size)

    def push(self, key, data):
        super().push(-key, data)

    def pop(self):
        key, data = super().pop()
        return -key, data

    def get_max(self):
        key, data = super().get_min()
        return -key, data
