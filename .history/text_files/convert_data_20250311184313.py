import json

"""
json转成jsonl
"""
# file_name = '/Users/dehua/code/gpqa/text_files/question_all1.json'
# with open(file_name, 'r', encoding='utf-8') as file:
#     datas = json.load(file)

# current_video = ''
# data_news = []
# data_dict = {}

# for data in datas:
#     if data["video_key"] == current_video:
#         current_data_id += 1
#     else:
#         current_data_id = 1
#         current_video = data["video_key"]
#         data_dict[current_video] = []
#     data_new = data
#     data_new["data_id"] = f"{current_video}_{current_data_id}"
#     data_dict[current_video].append(data_new)

# jsonl_file = '/Users/dehua/code/gpqa/text_files/questions_all.jsonl'
# with open(jsonl_file, 'w', encoding='utf-8') as file:
#     for k, v in data_dict.items():
#         file.write(json.dumps({k:v}, ensure_ascii=False))
#         file.write('\n')

"""
jsonl转uuid的格式
"""
import uuid
import json

def generate_16_digit_uuid():
    # 生成标准UUID然后取其前16个字符
    return str(uuid.uuid4()).replace('-', '')[:16]

jsonl_file = '/Users/dehua/code/gpqa/text_files/long_video_all.jsonl'
jsonl_file_new = '/Users/dehua/code/gpqa/text_files/long_video_all_new.jsonl'
data_dicts = []

with open(jsonl_file, 'r', encoding='utf-8') as file:
    for line in file.readlines():
        data = json.loads(line)
        for k, v in data.items():
            data_dict = {
                "uuid": generate_16_digit_uuid(),
                "video_key": k,
                "data": v
            }
            print(data_dict)
            data_dicts.append(data_dict)
print(data_dicts)
with open(jsonl_file_new, 'w', encoding='utf-8') as file:
    for data_dict in data_dicts:
        file.write(json.dumps(data_dict) + '\n')