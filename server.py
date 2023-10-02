import os
import socketserver


class MyWebServer(socketserver.BaseRequestHandler):

    CONTENT_TYPES = {
        '.html': "text/html",
        '.css': "text/css",
        '.js': "text/js"
    }#listing file types

    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print(f"Got a request of: {self.data}\n")

        method, path = self.parse_request()#breaks up, to get method and path

        if method != 'GET':
            self.send_response(405, "Method Not Allowed")
            return #405 response if method other than get, POST, PUT, DELETE- return 405

        #constructs the file path by adding ./www
        local_path = self.resolve_local_path(path)

        if not local_path or not self.is_path_within_base_directory(local_path):#check if the path exists in the directory
            self.send_response(404, "Not Found")
            return

        if os.path.isdir(local_path):
            if not path.endswith('/'):#if path is directory
                self.send_response(301, "Moved Permanently", location=path + '/')
                return
            local_path = os.path.join(local_path, 'index.html')#if a directoy add index.html

        self.send_file(local_path)

    def parse_request(self):#gets method and path
        request_line = self.data.splitlines()[0]
        return request_line.split(' ')[0:2]

    def resolve_local_path(self, path):#makes a filepath
        return os.path.abspath(os.path.join('./www', path.lstrip('/')))

    def is_path_within_base_directory(self, path):#
        return path.startswith(os.path.abspath('./www'))

    def send_file(self, path):#reads the file
        content_type = self.CONTENT_TYPES.get(os.path.splitext(path)[1], "text/plain")#checks the filetype by checking extension
        if os.path.exists(path):
            with open(path, 'r') as file:#reads the file
                content = file.read()
            self.send_response(200, "OK", content, content_type)#success
        else:
            self.send_response(404, "Not Found")#error

    def send_response(self, status_code, status_message, content="", content_type="text/html", location=None):
        response_headers = [
            f"HTTP/1.1 {status_code} {status_message}",
            f"Content-Type: {content_type}",
            f"Content-Length: {len(content)}"
        ]
        if location:#just use this to redirect 301 error
            response_headers.append(f"Location: {location}")
        response_headers.append("\r\n")
        response = "\r\n".join(response_headers) + content
        self.request.sendall(response.encode('utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    print(f"Serving on http://{HOST}:{PORT}")
    server.serve_forever()
