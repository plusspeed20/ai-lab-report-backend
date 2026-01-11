from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# 将 utils 目录添加到 Python 路径，以便导入我们的模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 尝试导入我们写好的评价函数
try:
    from utils.ai_evaluator import evaluate_experiment_report
    AI_EVALUATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import AI evaluator, using mock mode. Error: {e}")
    AI_EVALUATOR_AVAILABLE = False

app = FastAPI(title="AI实验报告评价系统API")

# 设置CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应替换为具体前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI实验报告评价系统API正在运行", "status": "healthy"}

@app.post("/api/evaluate_report")
async def evaluate_report(report_data: dict):
    """
    评价实验报告的主接口
    接收JSON格式的报告数据，返回AI评价结果
    """
    try:
        if AI_EVALUATOR_AVAILABLE:
            result = evaluate_experiment_report(report_data)
        else:
            # 模拟模式
            from utils.ai_evaluator import AIEvaluator
            evaluator = AIEvaluator()
            result = evaluator._generate_mock_evaluation(report_data)
            result["is_mock"] = True
            
        return {
            "success": True,
            "message": "AI评价完成",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评价过程中出错: {str(e)}")

@app.get("/api/test/hello")
def test_hello():
    """测试接口，验证服务是否正常运行"""
    return {"message": "Hello from Vercel Python FastAPI!"}