# **kg\_hw3: 医疗知识图谱构建与大模型集成测试**

本项目是一个关于医疗知识图谱（Knowledge Graph）构建与问答（QA）的实验性工程。主要涵盖了从数据爬取、结构化提取到大模型（LLM）驱动的 Text-to-Cypher 转换等核心环节，并在 Neo4j 和 TuGraph 两个图数据库平台上进行了适配调试。

## **📁 文件功能说明**

| 文件名 | 功能描述 |
| :---- | :---- |
| **spider.py** | **医疗数据爬取**：用于从指定网站或接口爬取原始的医疗文本数据，为图谱构建提供语料支撑。 |
| **extract.py** | **结构化数据提取测试**：用于测试大模型在不同 temperature 和 prompt 策略下，提取疾病结构化数据的准确度与稳定性。 |
| **test\_neo4j\_langchain.py** | **Neo4j 接口调试**：基于 LangChain 框架调试 Neo4j 与大模型的连接，实现从自然语言到 Cypher 语句的转化。 |
| **test\_tugraph\_langchain.py** | **TuGraph 接口调试**：在 TuGraph 平台图数据库上接入大模型，实现针对 TuGraph 语法的 Cypher 语句生成与查询。 |

## **🛠️ 技术栈**

* **大模型驱动**: [SiliconFlow (硅基流动)](https://siliconflow.cn/) / 通义千问 (Qwen)  
* **开发框架**: [LangChain](https://github.com/langchain-ai/langchain) / [Kor](https://github.com/eyurtsev/kor)  
* **图数据库**: [TuGraph](https://github.com/TuGraph-family/tugraph-db) & [Neo4j](https://neo4j.com/)  
* **编程语言**: Python 3.9+  
* **数据处理**: Pandas

## **📝 核心实验内容**

1. **Prompt 工程优化**：通过 extract.py 探索最优的提示词模板，减少大模型在医疗实体识别时的幻觉。  
2. **多数据库适配**：分别针对 Neo4j 和 TuGraph 两种主流图数据库的查询协议进行大模型接口封装。  
3. **自然语言交互**：通过 Text-to-Cypher 技术，使用户能够通过自然语言直接查询图数据库中的医疗事实。

## **🚀 快速开始**

### **1\. 安装依赖**

pip install pandas neo4j langchain langchain-openai requests kor

### **2\. 配置环境**

在使用 test\_\*.py 脚本前，请确保在脚本中配置了正确的：

* 图数据库连接地址 (Bolt URI)  
* 数据库账号与密码  
* 大模型 API Key 及 Base URL

## **🤝 贡献与反馈**

本项目为 kg\_hw3 作业/实验内容，如有疑问请通过 Issue 或邮件联系。