import pandas as pd
from openai import OpenAI
import time

# ================= 1. 配置区 =================
# 填入你的硅基流动 API Key
client = OpenAI(
    api_key="sk-jaeowvubagerozsqmytiuqdpvlvjgohuvwrrhchhuoeujeit", 
    base_url="https://api.siliconflow.cn/v1"
)

# 选择一个模型，例如 DeepSeek-V3 或 Qwen2.5
# 推荐使用 deepseek-ai/DeepSeek-V3 或 Qwen/Qwen2.5-7B-Instruct
MODEL_NAME = "deepseek-ai/DeepSeek-V3"

prompts = {
    "P1": "请从文本中提取疾病结构化数据，返回 JSON 格式：包含疾病名、主要症状、发病部位、传染性。",
    "P2": "你是一个医学专家，请从描述中提取以下字段：disease_name, symptoms (列表), site, infectious (布尔值或描述)。仅输出纯 JSON。",
    "P3": "执行以下步骤：1.识别疾病；2.列出核心症状；3.判断发病部位；4.判断传染性。将结果整理为 JSON 对象。"
}

# 定义 6 组测试配置
test_configs = [
    {"id": "Test_1", "p_key": "P1", "temp": 0.0},
    {"id": "Test_2", "p_key": "P2", "temp": 0.0},
    {"id": "Test_3", "p_key": "P3", "temp": 0.0},
    {"id": "Test_4", "p_key": "P1", "temp": 0.5},
    {"id": "Test_5", "p_key": "P1", "temp": 1.0},
    {"id": "Test_6", "p_key": "P2", "temp": 1.0}
]

# ================= 2. 函数区 =================
def call_siliconflow(prompt_text, input_text, temperature):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": f"待处理文本：\n{input_text}"},
            ],
            temperature=max(temperature, 0.01), # 部分模型不支持绝对 0，设为极小值
            # 硅基流动支持 JSON Mode
            response_format={'type': 'json_object'} 
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ================= 3. 执行区 =================
def main():
    # 读取原始数据
    try:
        df = pd.read_csv('疾病描述数据.csv')
    except Exception as e:
        print(f"读取 CSV 失败: {e}")
        return

    # 只取前两条进行测试
    test_samples = df.head(2) 
    all_results = []

    print(f"开始使用硅基流动 ({MODEL_NAME}) 进行测试...")

    for config in test_configs:
        p_content = prompts[config['p_key']]
        t_val = config['temp']
        
        for _, row in test_samples.iterrows():
            disease = row['diseaseName']
            desc = row['description']
            
            print(f"运行 [{config['id']}] - 样本: {disease} (Temp: {t_val})")
            
            result = call_siliconflow(p_content, desc, t_val)
            
            all_results.append({
                "实验ID": config['id'],
                "原疾病名": disease,
                "Temperature": t_val,
                "Prompt类型": config['p_key'],
                "提取结果": result
            })
            # 避免触发频率限制
            time.sleep(0.5)

    # 保存结果
    output_file = 'siliconflow_test_results.csv'
    pd.DataFrame(all_results).to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n测试完成！结果已保存至: {output_file}")

if __name__ == "__main__":
    main()