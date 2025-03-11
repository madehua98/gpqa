import json

file_name = '/Users/dehua/code/gpqa/text_files/question_all1.json'
with open(file_name, 'r', encoding='utf-8') as file:
    datas = json.load(file)

current_video = ''
for data in datas:
    if data["video_key"] == current_video:
        current_data_id += 1
    else:
        current_data_id = 1
        current_video = data["video_key"]

    data_new = data
    data_new["data_id"] = f"{current_video}_{current_data_id}"
