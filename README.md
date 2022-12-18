
> An automated file download script/package for Espanso Text Expander

![Language](https://img.shields.io/badge/language-python3-grenn)
![Platforms](https://img.shields.io/badge/platforms-Linux-blue)

# Description
This tool allow us to automate file download in the post-exploitation stages using Espanso.

#### What is a Espanso?
Espanso is a cross-platform Text Expander written in Rust. You can visit the [espanso website](https://espanso.org) for more information.
## Key Features
- Automate file download over HTTP/S or SMB.
- Download files into Linux or Windows machines from the revershell.
- One request web/smb server (actually for smb is a one session server). No port will stay listening.



# Purpose
I was always wondering about a way to automate the download of files on my target machine, because it was too heavy for me to search for the script/exploit I wanted to download locally, start a web/smb server and execute the download command on target (you can call me lazy, but I prefer to call it optimizing efforts).

The challenge was to start a web/smb server in my attacking machine from a revershell and download the file in one single command. Here is an example of the proposed solution:

![example](images/example.gif)

# How does it works?
Simple, write `:afd` in your revershell and a form will appear to indicate the file to download, the download method and the interface/IP through which to download the file. After filling the form, the download command will appear in your revershell waiting for you to hit enter.

It will be after filling the form when the web/smb server will be started and stopped automatically after the download request.

- web server: After a get request, the server will shut down, except for the certutil.exe request, which would be exactly 2 requests (that's how certutil.exe works).
- smb server: We use impacket smb server. In this case, because impacket smb server doesn't show the get file request in screen's info, the smb server will shut down when the client disconnects.

# Installation
First, make sure you have installed Python 3 and openssl. Then, you need to install Espanso by following this link:
- https://espanso.org/docs/install/linux/

Once installed, run the following command to install the afd package:
```bash
espanso install afd-package --git https://github.com/pablocastelao/afd --external
```
Move to Espanso's package `afd-package` folder:
1. Execute the following command and copy `Package` path:
  ```cmd
 espanso path 
  ```
2. Move to `Package` path and then to `afd-package` folder:
```cmd
cd <PACKAGE_PATH>
cd afd-package
```
- Automatic command for Linux:
```bash
cd $(espanso path | grep "Packages:" |awk -F: '{ print $2 }')
cd afd-package
```

Install Python3 requeriments:
```bash
pip3 install -r requirements.txt
```


# Documentation
- Type `:afd` in your revershell to run the tool.
- Download methods available:
	- wget
	- curl
	- certutil.exe
	- Invoke-WebRequest
	- Invoke-Expression
	- smb (net use;copy)
	- smbclient
- `files.txt` is the txt where we are going to write the files that we want to appear in the form. This files will have the following syntax:
`
<FILE_NICKNAME>:<FULL_PATH>
`
For example, if I want to add linpeas.sh script, I can write `linpeas:/opt/privilege-escalation-awesome-scripts-suite/linPEAS/linpeas.sh` in `files.txt` and the word `linpeas` will appear in the form. I can also write `1:/opt/privilege-escalation-awesome-scripts-suite/linPEAS/linpeas.sh` if I want, but the word that will appear in the form will be `1`.
- You can also download temporary files (like a specific exploit that we are going to use just once). To do that, we can especify the full file path  and a temporary entry will be added in `files.txt`. After the download, this entry will be removed.
- SMB server comes with default username and password settings. If you want to change them, you can open `afd.py` file and modify them. Same with HTTP/S server port.
- By default, web server will run over HTTP.
- Protocol HTTPS not supported for certutil and PowerShell download commands right now.






