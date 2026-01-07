import threading
import time

class ThreadKraken:
    def __init__(self):
        """
        Initializes the ThreadKraken class.
        - `threads`: Dictionary to store registered worker threads.
        - `blackboard`: Shared data storage.
        - `lock`: Synchronization lock to ensure thread-safe access to `blackboard`.
        - `stop_flags`: Dictionary to store stop event flags for each thread.
        """
        self.threads = {}
        self.blackboard = {}
        self.lock = threading.Lock()
        self.stop_flags = {}

    def register_thread(self, target, name, *args, **kwargs):
        """
        Registers a new thread with a target function.
        - `target`: The function that the thread will execute.
        - `name`: Unique name to identify the thread.
        - `args, kwargs`: Additional arguments passed to the target function.
        """

        stop_flag = threading.Event()
        thread = threading.Thread(target=target, name=name, args=(stop_flag, *args), kwargs=kwargs, daemon=True)
        self.threads[name] = thread
        self.stop_flags[name] = stop_flag

    def start_threads(self):
        """
        Starts all registered threads.
        """
        for thread in self.threads.values():
            thread.start()


    def start_thread(self, name):
        """
        Starts a specific registered thread by name.
        """
        if name in self.threads:
            self.threads.get(name).start()

    def stop_thread(self, name):
        """
        Stops a specific thread by setting its stop flag.
        - `name`: Name of the thread to stop.
        """
        if name in self.stop_flags:
            self.stop_flags[name].set()
            print(f"Stopping thread: {name}")
            t = self.threads.get(name)
            if t:
                t.join(timeout=2)
            # Cleanup registries
            self.threads.pop(name, None)
            self.stop_flags.pop(name, None)

    def stop_all_threads(self):
        """
        Stops all threads by setting their stop flags and clearing the registry.
        """
        # Signal all threads to stop
        for name, stop_flag in list(self.stop_flags.items()):
            stop_flag.set()
            print(f"Stopping thread: {name}")
        # Join all threads with a timeout
        for name, thread in list(self.threads.items()):
            thread.join(timeout=2)
        # Cleanup registries
        self.threads.clear()
        self.stop_flags.clear()

    def write_blackboard(self, key, value):
        """
        Thread-safe write operation to the blackboard.
        - `key`: Identifier for the data.
        - `value`: The data to store.
        """
        with self.lock:
            self.blackboard[key] = value

    def read_blackboard(self, key):
        """
        Thread-safe read operation from the blackboard.
        - `key`: Identifier for the data to retrieve.
        """
        with self.lock:
            return self.blackboard.get(key, None)

    def add_blackboard_listener(self, condition, callback, check_interval=1):
        """
        Runs a listener thread that continuously checks the condition and executes the callback when the condition is met.
        - `condition`: A boolean function that determines when to trigger the callback.
        - `callback`: The function to execute when the condition is met.
        - `check_interval`: Time in seconds between condition checks (default: 1 sec).
        """

        def listener(stop_flag):
            while not condition() and not stop_flag.is_set():
                time.sleep(check_interval)
            if not stop_flag.is_set():
                callback()

        name = f"Listener-{len(self.threads)}"
        stop_flag = threading.Event()
        listener_thread = threading.Thread(target=listener, args=(stop_flag,), daemon=True, name=name)
        listener_thread.start()
        self.threads[name] = listener_thread
        self.stop_flags[name] = stop_flag
        return name


# Example Worker Thread Function
# def worker(stop_flag, kraken, thread_id):
#     """
#     Example worker function that writes data to the blackboard in a loop.
#     - `stop_flag`: Event flag to signal when the thread should stop.
#     - `kraken`: Instance of `ThreadKraken` for accessing the blackboard.
#     - `thread_id`: Unique identifier for the worker thread.
#     """
#     for i in range(5):
#         if stop_flag.is_set():
#             print(f"Worker-{thread_id} stopping.")
#             break
#         kraken.write_blackboard(f"thread-{thread_id}", f"Iteration {i}")
#         time.sleep(1)
#         print(f"{threading.current_thread().name} wrote: Iteration {i}")
