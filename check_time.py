import json
import re

# 时间格式验证函数
def is_valid_time_format(time_str):
    # 匹配时间格式：单一时刻或者时间段
    time_pattern = r'^(?:([0-5]?\d):([0-5]?\d))$|^(?:([0-5]?\d):([0-5]?\d)-([0-5]?\d):([0-5]?\d))$'
    
    # 使用正则表达式进行匹配
    return bool(re.match(time_pattern, time_str))

# 读取JSONL文件
def process_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            
            for k, item in data.items():
                # 获取answer_location
                for d in item:
                    answer_location = d.get('answer_location', "")
                    
                    # 仅检查answer_location不为'Whole video'的情况
                    if answer_location != "Whole video":
                        # 检查是否为有效时间格式
                        if is_valid_time_format(answer_location):
                            pass
                            #print(f"Valid time found: {answer_location}")
                        else:
                            print(f"Invalid time format: {answer_location}")
                    else:
                        pass
                        #print(f"Skipping 'Whole video' for location: {answer_location}")

# 测试
file_path = '/Users/dehua/code/gpqa/outputs/all_data_v3.jsonl'  # 请替换为实际的文件路径
process_jsonl(file_path)