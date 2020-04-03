

class ReadWriter:
    def __init__(self):
        self.reader = sys.stdin.buffer
        self.writer = sys.stdout.buffer
    
    def read(self, *args):
        data = self.reader.read(*args)
        return data.decode("utf-8")

    def readline(self, *args):
        data = self.reader.readline(*args)
        return data.decode("utf-8")

    def write(self, out):
        self.writer.write(out.encode())
        self.writer.flush()

class JsonRpcStream():
    def __init__(self):
        self.stream = ReadWriter()

    def get_header_content_length(self, line):
        if line.startswith('Content-Length: '):
            value = line.split('Content-Length: ')
            value = value.strip()
            return int(value)

    def receive(self):
        line = self.stream.readline()
        length = self.get_header_content_length(line)
        while line != '\r\n':
            line = self.stream.readline()
        content = self.stream.read(length)
        return json.loads(content)

class LanguageServer():
    def __init__(self):
        self.workspace = {}
        self.conn = JsonRpcStream()
        self.running = True

    def run(self):
        while self.running:
            request = self.conn.receive()
            self.handle(request)
        
    def handle(self, request):
        handler = {
            "initialize": self.oninitialize,
            "textDocument/didChange": self.onChange,
            "textDocument/didOpen": self.OnOpen,
            "textDocument/didClose": self.onClose
        }.get(request['method'])

        if "id" not in request:
            handler(request)
            return
        else:
            
            

def main():
    languageServer = LanguageServer()
    languageServer.run()

main()