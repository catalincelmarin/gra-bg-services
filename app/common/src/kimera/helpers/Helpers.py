from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.web import JsonLexer

import json
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Helpers:
    @staticmethod
    def print(*arguments):
        for arg in arguments:
            if arg is None:
                continue
            if type(arg).__name__ in ["str"]:
                s = arg.split(" ")
                for i in s:
                    if i.isdigit():
                        print(bcolors.WARNING + str(i) + bcolors.ENDC, end=' ', flush=True)
                    else:
                        try:
                            nr = float(i)
                            print(bcolors.WARNING + str(i) + bcolors.ENDC, end=' ', flush=True)
                        except:
                            nr = i
                            print(nr, end=' ')
            elif type(arg).__name__ in ["int","float"]:
                print(bcolors.WARNING + str(arg) + bcolors.ENDC, end=' ', flush=True)
            else:
                try:
                    arg.keys()
                except:
                    print(repr(arg), end=' ', flush=True)
                    return
                if type(arg).__name__ != "list":
                    if arg is not None and "_id" in arg.keys():
                        del arg["_id"]
                    for i in arg.keys():
                        el = arg[i]
                        if type(el).__name__ == "datetime":
                            arg[i] = el.strftime("%Y-%M-%D %H:%M:%S.%s")
                        if type(el).__name__ == "time":
                            arg[i] = el.strftime("%H:%M:%S.%s")

                colorful = highlight(
                    json.dumps(arg, indent=2),
                    lexer=JsonLexer(),
                    formatter=TerminalFormatter(),
                )
                print(colorful, flush=True)

    @staticmethod
    def sysPrint(subject, info=""):
        if str(info) != "":
            info = " : " +  bcolors.OKGREEN + str(info) + bcolors.ENDC

        print(bcolors.OKBLUE + bcolors.BOLD + str(subject) + bcolors.ENDC + bcolors.ENDC + info, flush=True)

    @staticmethod
    def errPrint(message,file="",line=0):
        print(bcolors.FAIL + bcolors.BOLD + "ERROR in" + file + "(" + str(line) + ")"  " : " + bcolors.ENDC + bcolors.ENDC + str(message), flush=True)

    @staticmethod
    def warnPrint(message):
        print(bcolors.WARNING + bcolors.BOLD + "WARN : " + bcolors.ENDC + bcolors.ENDC + str(message), flush=True)

    @staticmethod
    def tracePrint(exc, message="", **kwargs):
        """
        Print a nicely formatted, colored error with stacktrace.

        Parameters:
        - exc: the exception instance
        - message: optional context message
        """
        import traceback

        header = f"ERROR"
        if message:
            header += f"{message}"
        
        print(bcolors.FAIL + bcolors.BOLD + header + bcolors.ENDC + bcolors.ENDC, flush=True)

        # Exception line
        print(bcolors.FAIL + f"{type(exc).__name__}: {exc}" + bcolors.ENDC, flush=True)

        # Stacktrace
        tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
        for ln in tb_lines:
            ln = ln.rstrip("\n")
            print(bcolors.WARNING + ln + bcolors.ENDC, flush=True)

    @staticmethod
    def infoPrint(message):
        print(bcolors.OKCYAN + bcolors.BOLD + "INFO : " + bcolors.ENDC + bcolors.ENDC + str(message), flush=True)

        
    @staticmethod
    def sigPrint(message):
        print(bcolors.OKCYAN + bcolors.BOLD + "SIGNAL : " + bcolors.ENDC + bcolors.ENDC + str(message), flush=True)