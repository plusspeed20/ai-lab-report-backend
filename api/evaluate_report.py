from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_evaluator import evaluate_experiment_report

# 允许的请求来源（CORS配置）
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1:5500",  # 本地Live Server常用端口
    "http://localhost:5500",
    "https://你的前端域名.vercel.app"  # 后续替换为你的实际前端域名
]

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理预检请求"""
        self.handle_cors()
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        """处理提交报告的评价请求"""
        try:
            self.handle_cors()
            
            # 1. 获取请求数据
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # 支持表单数据和JSON数据
            if self.headers.get('Content-Type', '').startswith('application/json'):
                data = json.loads(post_data)
            else:
                # 如果是表单数据，这里需要更复杂的解析
                # 为简化，我们先支持JSON
                data = json.loads(post_data)
            
            # 2. 调用AI评价引擎
            print(f"收到评价请求，实验名称: {data.get('experiment_name', '未知')}")
            ai_result = evaluate_experiment_report(data)
            
            # 3. 返回成功响应
            response = {
                "success": True,
                "message": "AI评价完成",
                "data": ai_result,
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except json.JSONDecodeError as e:
            self.send_error_response(400, f"JSON解析错误: {str(e)}")
        except KeyError as e:
            self.send_error_response(400, f"缺少必要字段: {str(e)}")
        except Exception as e:
            print(f"服务器内部错误: {str(e)}")
            self.send_error_response(500, f"服务器内部错误: {str(e)}")
    
    def send_error_response(self, code, message):
        """发送错误响应"""
        response = {
            "success": False,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.send_response(code)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def handle_cors(self):
        """处理CORS"""
        origin = self.headers.get('Origin', '')
        if origin in ALLOWED_ORIGINS or origin.endswith('.vercel.app'):
            self.send_header('Access-Control-Allow-Origin', origin)
    
    def send_cors_headers(self):
        """发送CORS头部"""
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Max-Age', '86400')

def handler(request, context):
    """Vercel Serverless函数入口（适配Vercel）"""
    from io import StringIO
    import sys
    
    class VercelHandler(Handler):
        def __init__(self, request):
            self.request = request
            self.headers = request['headers']
            self.path = request['path']
            self.method = request['method']
            self.body = request.get('body', '')
            self.status_code = 200
            self.response_headers = {}
        
        def send_response(self, code):
            self.status_code = code
        
        def send_header(self, key, value):
            self.response_headers[key] = value
        
        def end_headers(self):
            pass
        
        def do_GET(self):
            # 处理GET请求（示例）
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "API is running"}
            self.response_body = json.dumps(response)
        
        def do_POST(self):
            # 调用父类的POST处理
            self.headers = {k.lower(): v for k, v in self.headers.items()}
            super().do_POST()
    
    # 创建处理器并处理请求
    handler_instance = VercelHandler(request)
    
    if request['method'] == 'GET':
        handler_instance.do_GET()
    elif request['method'] == 'POST':
        handler_instance.do_POST()
    elif request['method'] == 'OPTIONS':
        handler_instance.do_OPTIONS()
    
    return {
        'statusCode': handler_instance.status_code,
        'headers': handler_instance.response_headers,
        'body': getattr(handler_instance, 'response_body', '{}')
    }

# 为本地测试保留
if __name__ == "__main__":
    from datetime import datetime
    import sys
    
    class TestHandler(Handler):
        def __init__(self):
            pass
        
        def log_message(self, format, *args):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")
    
    print("本地测试服务器启动中...")
    # 这里可以添加本地测试代码