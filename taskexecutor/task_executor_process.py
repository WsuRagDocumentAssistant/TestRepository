import logging
import traceback

from multiprocessing.queues import Queue # 타입 힌트용
from multiprocessing import Queue
from multiprocessing import Process


from .exception import FuncExecutorException
# class Task:
#     def __init__(self, works):
#         self._works = works

#     def __call__(self):
#         for work in self._works:
#             work()

logger = logging.getLogger(__name__)

# 큐에 이 값을 넣으면 워커가 루프를 빠져나온다.
# 워커 1개당 1개가 필요하다 (신호 하나는 워커 하나만 꺼내 간다).
SHUTDOWN = None

# ------------------------
# Worker Process
# ------------------------

class WorkProcess(Process):
    def __init__(self, task_queue: Queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = Queue()

    def stop(self):
        """워커에게 종료를 요청한다.

        큐에 이미 쌓여있는 작업은 모두 처리한 뒤에 종료된다.
        호출 후 join()으로 실제 종료를 기다린다.
        """
        self.task_queue.put(SHUTDOWN)

    def run(self):
        # spawn 방식에서는 자식이 새 인터프리터로 시작하므로
        # 로깅 설정이 상속되지 않는다. 여기서 직접 잡아준다.
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="[%(processName)s] %(levelname)s %(message)s",
            )

        logger.info("Worker Start")

        while True:
            task = self.task_queue.get()   # 작업이 올 때까지 대기

            if task is SHUTDOWN:           # 종료 신호
                logger.info("Worker Stop")
                break

            try:
                result = task()
                self.result_queue.put(result)
            except Exception:
                # 작업 하나가 실패해도 워커는 계속 살아있어야 한다.
                logger.exception("Task Failed")
                error = FuncExecutorException(
                    getattr(task, "__name__", repr(task)),
                    traceback.format_exc(),
                self.result_queue(error)
    )
            else:
                logger.info("Task Finished")
