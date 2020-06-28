import redmimicry
import threading
import time


class SimpleBotTask(threading.Thread):

    def __init__(self, api, implant_id, f):
        threading.Thread.__init__(self)
        self.api = api
        self.implant_id = implant_id
        self.f = f

    def run(self):
        self.result = self.f(self.api, self.implant_id)


class SimpleBot(threading.Thread):

    polling_interval = 3

    def __init__(self, api: redmimicry.Api):
        threading.Thread.__init__(self)
        self.api = api
        self.active = True
        self.on_connect_functions = []
        self.on_connect_functions_lock = threading.Lock()
        self.known_implants = []
        self.known_implants_lock = threading.Lock()
        self.tasks = []
        self.tasks_lock = threading.Lock()
        self.results = []
        self.results_lock = threading.Lock()

    def __iter__(self):
        while self.active:
            if self.results_lock.acquire(False):
                for r in self.results:
                    yield r
                self.results.clear()
            self.results_lock.release()
            time.sleep(0.1)

    def stop(self):
        self.active = False
        self.api.stop()

    def on_connect(self, on_connect_function):
        with self.on_connect_functions_lock:
            self.on_connect_functions.append(on_connect_function)

    def run(self):
        while self.active:
            implants = self.api.list_implants()
            for implant in implants:
                with self.known_implants_lock:
                    if not implant["id"] in self.known_implants and implant["interrogated"]:
                        self.known_implants.append(implant["id"])
                        with self.on_connect_functions_lock:
                            for f in self.on_connect_functions:
                                with self.tasks_lock:
                                    task = SimpleBotTask(self.api, implant, f)
                                    task.start()
                                    self.tasks.append(task)
            time.sleep(self.polling_interval)
            with self.tasks_lock:
                done = []
                for t in self.tasks:
                    if not t.is_alive():
                        t.join()
                        done.append(t)
                        with self.results_lock:
                            self.results.append(t.result)
                for d in done:
                    self.tasks.remove(d)
