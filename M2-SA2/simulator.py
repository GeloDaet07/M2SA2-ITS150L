from models import Process, MemoryBlock

class MemorySimulator:
    def __init__(self, total_memory, ch_interval, sc_interval, process_inputs, logger_func):
        self.total_memory_size = total_memory
        self.ch_time = ch_interval
        self.sc_time = sc_interval
        self.process_inputs = process_inputs

        self.logger = logger_func if logger_func else print

        self.memory_blocks = []
        self.process_list = []
        self.num_processes = len(self.process_inputs)
        self.processes_completed = 0
        self.timeline = 0

        self._initialize_memory()
        self._initialize_processes()

    def _initialize_memory(self):
        initial_block = MemoryBlock(0, self.total_memory_size - 1, self.total_memory_size)
        self.memory_blocks.append(initial_block)

    def _initialize_processes(self):
        for i, p_input in enumerate(self.process_inputs):
            process = Process(pid=i+1, size=p_input['size'], burst_time=p_input['burst'])
            self.process_list.append(process)

    def _get_process_by_pid(self, pid):
        for p in self.process_list:
            if p.pid == pid:
                return p
        return None

    def _sort_blocks(self):
        self.memory_blocks.sort(key=lambda block: block.start)

    def first_fit(self, process):
        self._sort_blocks()
        
        for i, block in enumerate(self.memory_blocks):
            if block.is_free and block.size >= process.size:
                if block.size > process.size:
                    new_hole = MemoryBlock(
                        start=block.start + process.size,
                        end=block.end,
                        size=block.size - process.size
                    )
                    self.memory_blocks.insert(i + 1, new_hole)
                    block.end = block.start + process.size - 1
                    block.size = process.size
                
                block.is_free = False
                block.pid = process.pid
                process.is_allocated = True
                process.allocated_block_index = i
                
                self.logger(f"Time {self.timeline} - Allocated Process {process.pid} to Block [{block.start}-{block.end}]")
                return True
        return False

    def free_memory(self, process):
        block_to_free = None
        for block in self.memory_blocks:
            if not block.is_free and block.pid == process.pid:
                block_to_free = block
                break
        
        if block_to_free is None: return

        self.logger(f"Time {self.timeline} - Process {process.pid} FINISHED. Freed Block [{block_to_free.start}-{block_to_free.end}]")
        
        block_to_free.is_free = True
        block_to_free.pid = -1
        process.is_allocated = False
        process.is_finished = True
        process.remaining_time = 0
        self.processes_completed += 1

    def coalesce(self):
        self.logger("- Running Coalescing (CH)")
        self._sort_blocks()
        i = 0
        while i < len(self.memory_blocks) - 1:
            current = self.memory_blocks[i]
            next_block = self.memory_blocks[i+1]
            if current.is_free and next_block.is_free:
                current.end = next_block.end
                current.size = current.end - current.start + 1
                self.memory_blocks.pop(i + 1)
            else:
                i += 1

    def compact(self):
        self.logger("- Running Compaction (SC)")
        new_blocks_list = []
        current_address = 0
        
        for block in self.memory_blocks:
            if not block.is_free:
                process = self._get_process_by_pid(block.pid)
                old_start = block.start
                block.start = current_address
                block.end = block.start + block.size - 1
                new_blocks_list.append(block)
                if process:
                    process.allocated_block_index = len(new_blocks_list) - 1
                
                self.logger(f"Compacted PID {block.pid}: Moved from {old_start} to {block.start}")
                current_address = block.end + 1

        if current_address < self.total_memory_size:
            free_block = MemoryBlock(
                start=current_address,
                end=self.total_memory_size - 1,
                size=self.total_memory_size - current_address
            )
            new_blocks_list.append(free_block)
        self.memory_blocks = new_blocks_list

    def step(self):
        if self.processes_completed >= self.num_processes:
            return False 

        self.timeline += 1
        self.logger(f"\n##### time = {self.timeline} #####")

        for p in self.process_list:
            if p.is_allocated and not p.is_finished:
                p.remaining_time -= 1
                if p.remaining_time == 0:
                    self.free_memory(p)

        for p in self.process_list:
            if not p.is_allocated and not p.is_finished:
                self.logger(f"Time {self.timeline}: Attempting to allocate Process {p.pid} (Size: {p.size})")
                self.first_fit(p)
        
        if self.ch_time > 0 and self.timeline % self.ch_time == 0:
            self.coalesce()
            
        if self.sc_time > 0 and self.timeline % self.sc_time == 0:
            self.compact()
            
        return True