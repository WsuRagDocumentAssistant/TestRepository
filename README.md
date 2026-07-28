# task-executor

멀티프로세스 작업 실행기. 다른 쪽(producer)에서 큐에 작업을 넣으면, 워커 프로세스가
꺼내서 실행한다.

## 요구 사항

- Python >= 3.11

## 설치

```bash
pip install .
```

## 사용법

작업(task)은 인자 없이 호출 가능한 객체여야 하고, **pickle 가능해야 한다.**
Windows는 `spawn` 방식이므로 lambda나 지역 함수는 큐로 넘길 수 없다.
모듈 최상위에 정의된 함수/클래스를 사용한다.

```python
from multiprocessing import Queue

from taskexecutor import SHUTDOWN, WorkProcess


def my_task():            # 모듈 최상위 정의 (pickle 가능)
    print("작업 실행")


if __name__ == "__main__":   # Windows에서는 필수
    task_queue = Queue()

    worker = WorkProcess(task_queue)
    worker.start()

    # producer 쪽: 작업을 만들어 큐에 넣는다
    for _ in range(5):
        task_queue.put(my_task)

    # 더 이상 넣을 작업이 없으면 종료 신호를 보낸다.
    # 큐에 남아있는 작업은 모두 처리한 뒤 워커가 종료된다.
    worker.stop()
    worker.join()
```

### 종료에 대해

`WorkProcess`는 non-daemon 프로세스다. 종료 신호를 보내지 않으면 워커가 큐에서
계속 대기하므로 **부모 프로세스도 종료되지 않는다.** 반드시 `stop()`으로 마무리한다.

워커를 여러 개 띄웠다면 워커 수만큼 종료 신호가 필요하다. 신호 하나는 워커 하나만
꺼내 가기 때문이다.

```python
workers = [WorkProcess(task_queue) for _ in range(4)]
for w in workers:
    w.start()

...

for w in workers:
    w.stop()      # 워커 1개당 신호 1개
for w in workers:
    w.join()
```

`terminate()`는 실행 중인 작업을 중간에 끊고 큐에 남은 작업도 버리므로, 정상 종료
경로로 쓰지 않는다.

### 작업 실패

task 내부에서 예외가 발생하면 워커가 죽지 않고 traceback을 로그로 남긴 뒤 다음
작업으로 넘어간다.
