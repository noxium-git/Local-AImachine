import os
import sys
import time
import socket
import shutil
import subprocess
import app

OLLAMA_HOST = '127.0.0.1'
OLLAMA_PORT = 11434
OLLAMA_COMMAND = ['ollama', 'serve']
AUTO_START_OLLAMA = os.environ.get('BETTEN_AUTO_START_OLLAMA', 'true').lower() in ('1', 'true', 'yes')
MODEL = os.environ.get('BETTEN_MODEL', 'godmoded/llama3-lexi-uncensored:latest')


def is_port_open(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def start_ollama():
    if shutil.which('ollama') is None:
        print('Error: Ollama is not installed or not in PATH.')
        print('Install Ollama first, then run this script again.')
        return None

    print('Starting Ollama server locally...')
    try:
        process = subprocess.Popen(OLLAMA_COMMAND, stdout=sys.stdout, stderr=sys.stderr)
        return process
    except OSError as e:
        print(f'Error launching Ollama: {e}')
        return None


def wait_for_ollama(timeout=30):
    for _ in range(timeout):
        if is_port_open(OLLAMA_HOST, OLLAMA_PORT):
            return True
        time.sleep(1)
    return False


def is_model_installed():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        return MODEL in result.stdout
    except Exception:
        return False


def main():
    print('Launching Betten AI locally...')

    if not is_port_open(OLLAMA_HOST, OLLAMA_PORT):
        print('Ollama is not running on http://127.0.0.1:11434')
        if AUTO_START_OLLAMA:
            print('Starting Ollama automatically...')
            ollama_proc = start_ollama()
            if ollama_proc is None:
                sys.exit(1)

            print('Waiting for Ollama to become available...')
            if not wait_for_ollama(30):
                print('Ollama did not start in time. Check your installation and model setup.')
                sys.exit(1)
        else:
            answer = input('Start Ollama server now? [Y/n]: ').strip().lower() or 'y'
            if answer not in ('y', 'yes'):
                print('Please start Ollama manually before running Betten AI.')
                sys.exit(1)

            ollama_proc = start_ollama()
            if ollama_proc is None:
                sys.exit(1)

            print('Waiting for Ollama to become available...')
            if not wait_for_ollama(30):
                print('Ollama did not start in time. Check your installation and model setup.')
                sys.exit(1)
    else:
        ollama_proc = None
        print('Ollama server already running.')

    if not is_model_installed():
        print(f'Warning: model "{MODEL}" is not installed locally. Run `ollama pull {MODEL}` first.')

    print('Starting Betten AI app...')
    try:
        app.main()
    except Exception as e:
        print(f'Betten AI exited with error: {e}')
    finally:
        if ollama_proc:
            print('Stopping Ollama server...')
            ollama_proc.terminate()
            ollama_proc.wait(timeout=10)

    print('Starting Betten AI app...')
    try:
        app.main()
    except Exception as e:
        print(f'Betten AI exited with error: {e}')
    finally:
        if ollama_proc:
            print('Stopping Ollama server...')
            ollama_proc.terminate()
            ollama_proc.wait(timeout=10)


if __name__ == '__main__':
    main()
