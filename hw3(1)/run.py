import sys
from byterun.pyvm2 import VirtualMachine

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py your_script.py [args...]")
        sys.exit(1)

    filename = sys.argv[1]
    sys.argv = sys.argv[1:]  # Чтобы скрипт мог использовать свои аргументы

    with open(filename, "rb") as f:
        source = f.read()

    code = compile(source, filename, "exec")

    vm = VirtualMachine()
    vm.run_code(code)

if __name__ == "__main__":
    main()
