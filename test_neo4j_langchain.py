import json
import os
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
# 确保与你的环境兼容，优先从 community 导入以通过 Pydantic 校验
try:
    from langchain_community.graphs import Neo4jGraph
except ImportError:
    from langchain_neo4j import Neo4jGraph

class LLMQuestionParser:
    def __init__(self):
        # --- 1. 基础配置 (硅基流动 API 与 数据库凭证) ---
        # 尝试从环境变量读取 SILICONFLOW_API_KEY
        # 建议在终端运行: set SILICONFLOW_API_KEY=你的密钥 (Windows)
        self.api_key = 'sk-jaeowvubagerozsqmytiuqdpvlvjgohuvwrrhchhuoeujeit' 
        
        # 硅基流动 API 标准配置
        self.base_url = "https://api.siliconflow.cn/v1"
        # 推荐使用其平台上的高性能模型，如 DeepSeek-V3 或 Pro 版
        self.model_name = "deepseek-ai/DeepSeek-V3"

        # 数据库连接信息 (保持原有配置)
        self.neo4j_url = "bolt://127.0.0.1:7687"
        self.username = "neo4j"
        self.password = "88888888" 
        
        # --- 2. 初始化 Neo4j 图连接 ---
        try:
            self.graph = Neo4jGraph(
                url=self.neo4j_url,
                username=self.username,
                password=self.password
            )
            # 强制刷新 Schema，使 LLM 能感知当前的医疗实体和关系
            self.graph.refresh_schema()
            print(f"Neo4j 图数据库连接成功，当前模型: {self.model_name}")
        except Exception as e:
            print(f"Neo4j 连接失败: {e}")
            raise RuntimeError("无法连接到 Neo4j，请检查服务状态或认证信息。")

        # --- 3. 初始化大语言模型 (硅基流动) ---
        if not self.api_key:
            print("警告: 未检测到 SILICONFLOW_API_KEY 环境变量。")
            
        try:
            self.llm = ChatOpenAI(
                model=self.model_name,
                openai_api_key=self.api_key,
                openai_api_base=self.base_url,
                temperature=0.1,  # 较低的温度有助于生成更稳定的 Cypher 代码
                max_retries=3
            )
        except Exception as e:
            print(f"LLM (SiliconFlow) 初始化失败: {e}")
            raise e

        # --- 4. 初始化 GraphCypherQAChain ---
        # 这一步会将 LLM 的自然语言理解力与 Neo4j 的图查询能力结合
        self.chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True, # 开启 verbose 可在控制台查看生成的 Cypher 过程
            allow_dangerous_requests=True,
            return_intermediate_steps=True
        )

    def parser_main(self, res_classify):
        """
        解析主函数：将自然语言问句解析为 Cypher 语句
        res_classify: 由分类器提供的实体识别结果
        """
        raw_question = res_classify.get('text', "")
        if not raw_question:
            return []
        
        try:
            # 执行图查询链
            result = self.chain.invoke({"query": raw_question})
            
            # 提取生成的中间 Cypher 语句
            cypher = ""
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    if isinstance(step, dict) and "query" in step:
                        cypher = step["query"]
                        break
            
            if cypher:
                # 返回符合原系统 AnswerSearcher 预期的格式
                return [{"question_type": "llm_generated", "sql": [cypher]}]
        except Exception as e:
            print(f"硅基流动 LLM 生成 Cypher 失败: {e}")
            
        return []

if __name__ == '__main__':
    # 模拟医疗问答测试
    try:
        parser = LLMQuestionParser()
        # 测试问题：识别出实体为疾病
        test_data = {
            "text": "糖尿病的常见症状有哪些？",
            "args": {"糖尿病": ["disease"]}
        }
        result = parser.parser_main(test_data)
        print("\n" + "="*50)
        print(f"SiliconFlow 转换结果:\n{result}")
        print("="*50)
    except Exception as e:
        print(f"初始化失败: {e}")