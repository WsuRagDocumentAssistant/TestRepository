from multiprocessing import Process, Queue

# class Task:
#     def __init__(self, works):
#         self._works = works

#     def __call__(self):
#         for work in self._works:
#             work()
    
# ------------------------
# Worker Process
# ------------------------

class WorkProcess(Process):
    def __init__(self, task_queue: Queue):
        super().__init__()
        self.task_queue = task_queue

    def run(self):
        print("Worker Start")

        while True:
            task = self.task_queue.get()   # 작업이 올 때까지 대기
            task()
            print("Task Finished")


