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

# jsonl_file = '/Users/dehua/code/gpqa/text_files/questions_all.jsonl'
# with open(jsonl_file, 'w', encoding='utf-8') as file:
#     for k, v in data_dict.items():
#         file.write(json.dumps({k:v}, ensure_ascii=False))
#         file.write('\n')