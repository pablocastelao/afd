import os
import sys
import signal
import pathlib
import subprocess
from afd import check_file, delete_tmp_file

file = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
_path = str(pathlib.Path(__file__).parent.resolve())
PATH = pathlib.Path(_path)

if __name__ == "__main__":
    _path_file = check_file(file)
    if _path_file == False:
        exit()
    delete_tmp_file(file)
    path = os.path.dirname(_path_file)
    app = subprocess.Popen("cd "+path+";"+sys.executable+" "+str(PATH/"smbserver.py")+" share . -smb2support -username "+user+" -password "+password, stdout = subprocess.PIPE, universal_newlines = True, shell=True, preexec_fn=os.setsid)
    try:
        for line in app.stdout:
            if "Closing down connection" in line.strip():
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        pass

    os.killpg(os.getpgid(app.pid), signal.SIGTERM)
