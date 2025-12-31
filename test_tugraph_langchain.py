import pandas as pd
from neo4j import GraphDatabase
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# --- TuGraph 配置 ---
URI = "bolt://172.27.128.1:7687"
AUTH = ("admin", "73@TuGraph")
DB_NAME = "default"

# --- LLM 配置 (硅基流动 SiliconFlow) ---
# 注意：API Key 留空，运行时环境将自动注入
API_KEY = "sk-jaeowvubagerozsqmytiuqdpvlvjgohuvwrrhchhuoeujeit" 
BASE_URL = "https://api.siliconflow.cn/v1"

class LocalMedicalKGQA:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        
        # 1. 初始化 LLM (使用硅基流动提供的模型)
        # 常用的模型名称如: "Qwen/Qwen2.5-7B-Instruct" 或 "deepseek-ai/DeepSeek-V3"
        self.llm = ChatOpenAI(
            model="Qwen/Qwen2.5-7B-Instruct", 
            temperature=0, 
            openai_api_key=API_KEY, 
            base_url=BASE_URL
        )

        # 2. 定义 Prompt 模板 (Text-to-Cypher)
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Task: Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}

Examples: Here is an examples of generated Cypher statements for a particular question:
{example}

Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.""",
            ),
            ("human", "{input}"),
        ])

        # 3. 构建完整的 Schema 上下文
        self.schema_info = """Node properties:
Disease {name: STRING}
Symptom {name: STRING}
Alias {name: STRING}
Part {name: STRING}
Department {name: STRING}
Complication {name: STRING}
Drug {name: STRING}
Age {name: STRING}
Infection {name: STRING}
Insurance {name: STRING}
Checklist {name: STRING}
Treatment {name: STRING}
Period {name: STRING}
Rate {name: STRING}

The relationships:
(:Disease)-[:Cure_Rate]->(:Rate)
(:Disease)-[:HAS_SYMPTOM]->(:Symptom)
(:Disease)-[:HAS_ALIAS]->(:Alias)
(:Disease)-[:IS_OF_PART]->(:Part)
(:Disease)-[:IS_OF_AGE]->(:Age)
(:Disease)-[:IS_INFECTIOUS]->(:Infection)
(:Disease)-[:In_Insurance]->(:Insurance)
(:Disease)-[:IS_OF_Department]->(:Department)
(:Disease)-[:HAS_Checklist]->(:Checklist)
(:Disease)-[:HAS_Complication]->(:Complication)
(:Disease)-[:HAS_Treatment]->(:Treatment)
(:Disease)-[:HAS_Drug]->(:Drug)
(:Disease)-[:Cure_Period]->(:Period)"""

        # 4. 定义 Few-shot 示例
        self.example_info = """# 头晕用什么药？
MATCH (:Symptom {name: "头晕"})<-[:HAS_SYMPTOM]-(d:Disease)-[:HAS_Drug]->(drug:Drug) RETURN drug.name AS result

# 感冒有哪些症状？
MATCH (d:Disease {name: "感冒"})-[:HAS_SYMPTOM]->(s:Symptom) RETURN s.name AS result

# 糖尿病挂什么科？
MATCH (d:Disease {name: "糖尿病"})-[:IS_OF_Department]->(dept:Department) RETURN dept.name AS result"""

        # 5. 创建链
        self.chain = self.prompt | self.llm
        print("[信息] 医疗问答链 (SiliconFlow Text-to-Cypher) 已就绪。")

    def _parse_query_to_cypher(self, question):
        """将自然语言转换为 Cypher 语句"""
        try:
            ai_msg = self.chain.invoke({
                "schema": self.schema_info,
                "example": self.example_info,
                "input": question
            })
            cypher = ai_msg.content.strip().replace("```cypher", "").replace("```", "").strip()
            return cypher
        except Exception as e:
            print(f"[错误] Cypher 生成失败: {e}")
            return None

    def execute_cypher(self, cypher):
        """在 TuGraph 中执行生成的 Cypher 并获取结果"""
        try:
            with self.driver.session(database=DB_NAME) as session:
                res = session.run(cypher)
                results = []
                for record in res:
                    for value in record.values():
                        results.append(str(value))
                return list(set(results)) # 去重
        except Exception as e:
            print(f"[错误] Cypher 执行失败: {e}\n语句: {cypher}")
            return None

    def answer(self, question):
        # 1. 生成 Cypher
        cypher = self._parse_query_to_cypher(question)
        if not cypher:
            return "抱歉，我无法将您的问题解析为有效的查询语句。"
        
        print(f"[生成的 Cypher]: {cypher}")

        # 2. 执行查询
        results = self.execute_cypher(cypher)
        
        # 3. 组织回答
        if results is None:
            return "数据库查询执行出错。"
        
        if not results:
            return "抱歉，我的知识库中暂未查到相关信息，或者您的问题超出了我的理解范围。"
        
        res_str = "、".join(results)
        return f"查询到如下信息：\n{res_str}"

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    handler = LocalMedicalKGQA()
    
    print("--- 欢迎使用医疗知识图谱问答助手 (SiliconFlow 版) ---")
    while True:
        user_input = input("\n请输入您的问题 (输入 'quit' 退出): ")
        if not user_input.strip():
            continue
        if user_input.lower() == 'quit':
            break
            
        response = handler.answer(user_input)
        print(f"助手回复: {response}")
    
    handler.close()