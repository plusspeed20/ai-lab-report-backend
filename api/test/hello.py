from http.server import BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello from Vercel Python!')

# 下面的代码是为了在Vercel上运行
def handler(request, context):
    # 这是一个简单的适配器，让Vercel可以调用我们的Handler
    class VercelHandler(Handler):
        def __init__(self, *args, **kwargs):
            pass
    return {'statusCode': 200, 'body': 'Hello from Vercel Python!'}