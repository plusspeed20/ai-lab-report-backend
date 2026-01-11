"""
极简版本：AI实验报告评价API（Vercel Serverless Function版本）
这个版本不处理复杂的AI逻辑，只作为桥梁调用外部AI服务。
"""
import os
import json
from http.server import BaseHTTPRequestHandler
import urllib.request

# 配置：使用环境变量中的DeepSeek API密钥，如果未设置则使用模拟模式
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "mock_mode")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def handler(event, context):
    """Vercel Serverless Function 主处理函数"""
    # 1. 解析请求
    try:
        # Vercel 会将请求体作为 event 的 'body' 字段传入
        body = json.loads(event.get('body', '{}'))
        report_data = body.get('report_data', {})
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'message': '无效的JSON请求体'})
        }

    # 2. 根据模式进行处理
    if DEEPSEEK_API_KEY == "mock_mode":
        # 模拟模式：返回固定的示例数据
        return mock_evaluation(report_data)
    else:
        # 真实模式：转发请求到DeepSeek API
        return call_deepseek_api(report_data)

def mock_evaluation(report_data):
    """生成模拟评价数据"""
    experiment_name = report_data.get('experiment_name', '未知实验').lower()
    
    # 根据实验名称返回不同的模拟数据
    if '单摆' in experiment_name or '重力' in experiment_name:
        score = 88
        feedback = "实验步骤清晰，数据记录完整，但误差分析可更深入。"
    elif '电路' in experiment_name or '谐振' in experiment_name:
        score = 92
        feedback = "谐振曲线测量精确，图表规范，分析透彻。"
    elif '化学' in experiment_name or '合成' in experiment_name:
        score = 76
        feedback = "原理描述正确，但产率计算和产物表征部分需要完善。"
    else:
        score = 85
        feedback = "报告结构完整，符合基本规范，有提升空间。"

    result = {
        'success': True,
        'data': {
            'comprehensive_score': score,
            'dimension_scores': {'format': score+2, 'data': score, 'logic': score-3, 'analysis': score-5},
            'strengths': ['报告格式规范', '实验目的明确'],
            'weaknesses': ['数据分析深度可加强', '结论部分略显简略'],
            'specific_suggestions': [feedback, '建议补充更多参考文献'],
            'evaluation_rationale': '基于实验报告的基本要素进行评价。',
            'is_mock': True
        },
        'message': 'AI评价完成（模拟模式）'
    }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(result, ensure_ascii=False)
    }

def call_deepseek_api(report_data):
    """调用真实的DeepSeek API（如果你有真实的API密钥）"""
    # 这里是调用真实API的逻辑，因为你目前是mock_mode，我们先不实现
    # 当你有真实API密钥后，可以在这里添加代码
    return mock_evaluation(report_data)

# 为了兼容性，保留旧的类定义（Vercel的某些环境可能需要）
class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 模拟Vercel的事件格式
        event = {'body': post_data.decode('utf-8')}
        response = handler(event, {})
        
        self.send_response(response['statusCode'])
        for key, value in response['headers'].items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response['body'].encode('utf-8') if isinstance(response['body'], str) else response['body'])

# 本地测试用
if __name__ == "__main__":
    # 本地测试代码
    test_event = {
        'body': json.dumps({
            'report_data': {
                'experiment_name': '单摆测重力加速度',
                'purpose': '测试目的',
                'procedure': '测试步骤'
            }
        })
    }
    result = handler(test_event, {})
    print(json.dumps(json.loads(result['body']), indent=2, ensure_ascii=False))