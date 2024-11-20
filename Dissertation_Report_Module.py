import subprocess

def run_autopsy():
    autopsy_path = r"C:\Program Files\Autopsy-4.21.0\bin\autopsy64.exe"
    
    try:
        result = subprocess.run([autopsy_path], capture_output=True, text=True, shell=True)
        print("Output:", result.stdout)
        print("Error:", result.stderr)
        print("Return Code:", result.returncode)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except subprocess.CalledProcessError as e:
        print(f"CalledProcessError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_autopsy()