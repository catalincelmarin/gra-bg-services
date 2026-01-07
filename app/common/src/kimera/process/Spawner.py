import asyncio
import multiprocessing
import os
import signal
import threading
import time

import setproctitle
from threading import Lock, Thread

from kimera.Bootstrap import Bootstrap
from kimera.helpers.Helpers import Helpers


class Spawner:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Spawner, cls).__new__(cls)
                    cls._instance.processes = {}
                    cls._instance.threads = {}
                    cls._instance.kill_threads = {}
                    cls._instance.shutdown_signals = {}  # Store events for graceful stopping
        return cls._instance

    def thread_loop(self, name, coro, params=None, perpetual=True):
        if not params:
            params = {}
        name = f"thread-{name}"
        if name in self.threads and self.threads[name].is_alive():
            print(f"Thread {name} is already running")
            return

        def p_loop(p_coro, _params, _stop_event):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.create_task(self._graceful_task_wrapper(p_coro, _params, _stop_event))
            loop.run_forever()

        def f_loop(f_coro, _params,*args, **kwargs):
            Helpers.sysPrint("CALLING","F_CORO")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Run the event loop to completion
                loop.run_until_complete(f_coro(**_params))
            finally:
                loop.close()



        use_loop = p_loop if perpetual else f_loop

        # Create a stop signal forFalse this process
        stop_event = threading.Event()
        self.shutdown_signals[name] = stop_event

        # Create and start the process
        thread = threading.Thread(target=use_loop, args=(coro, params, stop_event))
        thread.start()
        if not perpetual:
            return None
        else:
            return thread

    def loop(self, name, coro, params=None, perpetual=True):
        if not params:
            params = {}
        if name in self.processes and self.processes[name].is_alive():
            print(f"Process {name} is already running with PID {self.processes[name].pid}")
            return

        def p_loop(p_coro, _params, _stop_event, *args, **kwargs):
            _boot = Bootstrap()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.create_task(self._graceful_task_wrapper(p_coro, _params, _stop_event))
            loop.run_forever()

        def f_loop(f_coro, _params, *args, **kwargs):
            _boot = Bootstrap()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(f_coro(**_params))

        use_loop = p_loop if perpetual else f_loop
        stop_event = None
        # Create a stop signal forFalse this process
        if perpetual:
            stop_event = multiprocessing.Event()
            self.shutdown_signals[name] = stop_event

        # Create and start the process
        process = multiprocessing.Process(target=use_loop, args=(coro, params, stop_event))
        process.start()
        setproctitle.setproctitle(name)
        self.processes[name] = process

        print(f"Started loop process {name} with PID {process.pid}")
        if process.pid:
            return process.pid

        return None

    async def _graceful_task_wrapper(self, coro, params, stop_event):
        """Wrap a coroutine to stop gracefully when the event is set."""
        task = None
        while not stop_event.is_set():
            if not task:
                task = asyncio.create_task(coro(**params))
            await asyncio.sleep(0.1)
        task.cancel()

    def start(self, name, target,daemon=True, *args):
        """Start a new process for the given name, if not already running."""
        if name in self.processes and self.processes[name].is_alive():
            print(f"Process {name} is already running with PID {self.processes[name].pid}")
            return

        # Create a stop signal for this process
        stop_event = multiprocessing.Event()
        self.shutdown_signals[name] = stop_event

        # Create and start the process
        process = multiprocessing.Process(target=target, args=(*args, stop_event))
        process.daemon = daemon
        process.start()
        self.processes[name] = process
        setproctitle.setproctitle(name)
        print(f"Started process {name} with PID {process.pid}")
        if process.pid:
            return process.pid
        else:
            return None

    def stop(self, name):
        """Stop the process by name, if it’s running."""
        process = self.processes.get(name)
        stop_event = self.shutdown_signals.get(name)

        if stop_event:
            stop_event.set()  # Signal the process to stop gracefully

        if process and process.is_alive():
            # Wait for the process to exit

            process.terminate()  # Force termination if still alive
            timeout = 3  # Timeout duration in seconds
            start_time = time.time()
            Helpers.sysPrint("ATTEMPT","STOP")
            while process.is_alive():
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    # If the process is still alive after the timeout, force kill it
                    print(f"Process {name} did not stop gracefully within {timeout} seconds. Force terminating...")
                    os.kill(process.pid, signal.SIGKILL)  # Force kill the process

                time.sleep(0.1)

            if not process.daemon:
                killer = threading.Thread(target=process.join,args=())
                killer.start()
                killer.join(timeout=3)
            print(f"Stopped process {name} with PID {process.pid}")
            del self.processes[name]
            del self.shutdown_signals[name]
            return not process.is_alive()
        else:
            print(f"No running process found for {name}")
            return True

    def restart(self, name, target, *args):
        """Restart the process by stopping and starting it again."""
        self.stop(name)
        self.start(name, target, *args)

    def monitor(self):
        """Monitor all processes and restart any that have died."""
        for name, process in list(self.processes.items()):
            if not process.is_alive():
                print(f"Process {name} with PID {process.pid} has stopped. Restarting...")
                target = process._target  # Retrieve the original target function
                args = process._args[:-1]  # Remove the Event from args
                self.start(name, target, *args)

    def ps(self):
        """List all active processes."""
        for name, process in self.processes.items():
            status = "running" if process.is_alive() else "stopped"
            print(f"Process {name}: PID {process.pid}, Status: {status}")

    def cleanup(self):
        """Stop all processes gracefully."""
        print("Stopping all processes...")
        for name in list(self.processes.keys()):
            self.stop(name)
        print("All processes stopped.")
