import os
import json
from datetime import datetime
from typing import Dict, Any, List
import requests

class AIEvaluator:
    """AI评价器 - 封装大模型API调用"""
    
    def __init__(self):
        # 配置你的大模型API（这里以DeepSeek为例）
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.model = "deepseek-chat"
        
        # 如果没有API Key，使用模拟模式（开发用）
        self.mock_mode = not self.api_key
        
        if self.mock_mode:
            print("⚠️ 警告：使用模拟模式，请设置DEEPSEEK_API_KEY环境变量使用真实AI")
    
    def evaluate_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """评价实验报告"""
        
        if self.mock_mode:
            return self._generate_mock_evaluation(report_data)
        
        # 真实API调用
        return self._call_ai_api(report_data)
    
    def _call_ai_api(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用真实AI API"""
        
        # 构建提示词
        prompt = self._build_evaluation_prompt(report_data)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位严谨的大学实验课教师，专门评价学生的实验报告。请严格按照评分标准进行评价，并给出具体的改进建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # 较低的温度以获得更稳定的输出
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            ai_response = response.json()
            ai_text = ai_response["choices"][0]["message"]["content"]
            
            # 解析AI返回的JSON
            return self._parse_ai_response(ai_text, report_data)
            
        except Exception as e:
            print(f"AI API调用失败: {str(e)}")
            # 失败时返回模拟数据
            return self._generate_mock_evaluation(report_data)
    
    def _build_evaluation_prompt(self, report_data: Dict[str, Any]) -> str:
        """构建评价提示词"""
        
        # 提取报告内容
        experiment_name = report_data.get("experiment_name", "未知实验")
        purpose = report_data.get("purpose", "")
        procedure = report_data.get("procedure", "")
        analysis = report_data.get("analysis", "")
        conclusion = report_data.get("conclusion", "")
        
        prompt = f"""请评价以下实验报告，并严格按照JSON格式返回结果。

【实验报告信息】
实验名称：{experiment_name}
提交时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【报告内容】
1. 实验目的：{purpose}
2. 实验步骤：{procedure}
3. 结果分析：{analysis}
4. 实验结论：{conclusion}

【评价要求】
请从以下维度进行评价（每项满分25分，总分100分）：
1. 格式规范：结构是否完整，格式是否符合学术规范
2. 数据准确：数据记录是否完整，计算是否正确
3. 逻辑严谨：分析过程是否逻辑清晰，推理是否合理
4. 分析深度：是否深入分析，是否提出有价值的见解

【输出格式】
你必须返回一个合法的JSON对象，格式如下：
{{
  "comprehensive_score": 85,
  "dimension_scores": {{
    "format": 90,
    "data": 80,
    "logic": 85,
    "analysis": 85
  }},
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["不足1", "不足2"],
  "specific_suggestions": ["具体建议1", "具体建议2"],
  "evaluation_rationale": "一段简要的总体评价"
}}

请现在开始评价："""
        
        return prompt
    
    def _parse_ai_response(self, ai_text: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析AI返回的文本为结构化数据"""
        
        try:
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # 确保所有必要字段都存在
                required_fields = ["comprehensive_score", "dimension_scores", 
                                  "strengths", "weaknesses", "specific_suggestions"]
                for field in required_fields:
                    if field not in result:
                        result[field] = [] if field.endswith('s') else 0
                
                return result
            else:
                raise ValueError("未找到JSON响应")
                
        except Exception as e:
            print(f"解析AI响应失败: {str(e)}，使用模拟数据")
            return self._generate_mock_evaluation(original_data)
    
    def _generate_mock_evaluation(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成模拟评价数据（开发用）"""
        
        # 基于实验名称生成不同的评价
        experiment_name = report_data.get("experiment_name", "").lower()
        
        if "单摆" in experiment_name or "重力" in experiment_name:
            return {
                "comprehensive_score": 88,
                "dimension_scores": {
                    "format": 92,
                    "data": 90,
                    "logic": 85,
                    "analysis": 85
                },
                "strengths": [
                    "实验目的明确，步骤记录详实",
                    "数据记录表格设计合理，多次测量减少偶然误差"
                ],
                "weaknesses": [
                    "误差分析部分可以更加深入",
                    "结论可以更紧密地结合实验数据"
                ],
                "specific_suggestions": [
                    "建议补充系统误差（如空气阻力、摆角影响）的讨论",
                    "在结论中引用具体的g值计算结果",
                    "可以尝试用不同摆长验证T²与L的线性关系"
                ],
                "evaluation_rationale": "报告整体完成度较高，基础扎实，但在深度分析和理论联系方面有提升空间。",
                "is_mock": True  # 标记为模拟数据
            }
        elif "合成" in experiment_name or "化学" in experiment_name:
            return {
                "comprehensive_score": 76,
                "dimension_scores": {
                    "format": 85,
                    "data": 70,
                    "logic": 80,
                    "analysis": 69
                },
                "strengths": [
                    "实验原理描述准确",
                    "反应装置绘制规范"
                ],
                "weaknesses": [
                    "产率计算过程缺失关键步骤",
                    "产物表征数据不完整"
                ],
                "specific_suggestions": [
                    "请补充产率的详细计算公式与计算过程",
                    "应列出产物的熔点、IR特征峰等表征数据",
                    "建议讨论可能影响产率的因素"
                ],
                "evaluation_rationale": "实验基本步骤正确，但在数据记录和分析深度方面需要加强。",
                "is_mock": True
            }
        else:
            # 默认评价
            return {
                "comprehensive_score": 82,
                "dimension_scores": {
                    "format": 88,
                    "data": 85,
                    "logic": 80,
                    "analysis": 75
                },
                "strengths": [
                    "报告结构完整，符合规范",
                    "实验步骤描述清晰"
                ],
                "weaknesses": [
                    "数据分析可以更加深入",
                    "结论部分略显简略"
                ],
                "specific_suggestions": [
                    "建议增加对实验误差的系统分析",
                    "结论部分可以扩展实际应用意义的讨论"
                ],
                "evaluation_rationale": "基础扎实，符合实验报告基本要求，有提升空间。",
                "is_mock": True
            }

def evaluate_experiment_report(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """评价实验报告的主函数"""
    evaluator = AIEvaluator()
    return evaluator.evaluate_report(report_data)

# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_report = {
        "experiment_name": "单摆测重力加速度",
        "purpose": "通过测量单摆周期计算重力加速度",
        "procedure": "1. 调整摆长 2. 测量周期 3. 计算g值",
        "analysis": "测得g=9.81m/s²，与理论值接近",
        "conclusion": "实验成功测得重力加速度"
    }
    
    result = evaluate_experiment_report(test_report)
    print(json.dumps(result, indent=2, ensure_ascii=False))