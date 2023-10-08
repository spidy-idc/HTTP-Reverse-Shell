This is an HTTP reverse shell designed in Python. It's a stealthy malware/reverse shell for pen-testing/red teaming. It can be converted to an exe and sent to the victim. When the victim clicks it, the Attacker will get full shell/cmd access to the victim's computer. It is a stealthy malware made with firewalls and other defensive measures in mind. It uses port 80 and HTTP for communication because as we know most corporates only allow HTTP Web outgoing traffic all other traffic is blocked. It has features like taking screenshots, uploading/downloading files, full cmd access, port scanning etc

Steps To Run:
1. Use pyinstaller to convert the victim_client.py to an exe and make sure to change the name of exe to `program.exe`
2. Start the attacker_server.py it'll by default run on port 80 you can change the port
3. Change all the http url IPs in victim_client.py to your HOST IP
4. Now start the attacker_server.py and then run program.exe in your testing PC.
5. You'll have a reverse Shell Now
