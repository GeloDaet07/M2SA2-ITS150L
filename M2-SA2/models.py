class Process:
    def __init__(self, pid, size, burst_time):
        self.pid = pid
        self.size = size
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.is_allocated = False
        self.is_finished = False
        self.allocated_block_index = -1

class MemoryBlock:
    def __init__(self, start, end, size, is_free=True, pid=-1):
        self.start = start
        self.end = end
        self.size = size
        self.is_free = is_free
        self.pid = pid