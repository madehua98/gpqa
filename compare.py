import json

file1 = "/Users/dehua/code/gpqa/outputs/all_data_v2_translation.jsonl"
file2 = "/Users/dehua/code/gpqa/text_files/all_data_v2_translation.jsonl"

# 读取第一个文件并以uuid为键创建字典
data1 = {}
with open(file1, 'r', encoding='utf-8') as f1:
    for line in f1.readlines():
        line = json.loads(line)
        uuid = line.get("uuid")  # 假设每行有一个 'uuid' 键
        if uuid:
            data1[uuid] = line

# 读取第二个文件并根据uuid进行匹配更新
new_datas = []
with open(file2, 'r', encoding='utf-8') as f2:
    for line in f2.readlines():
        line = json.loads(line)
        uuid = line.get("uuid")  # 假设每行有一个 'uuid' 键
        if uuid and uuid in data1:
            new_data = line
            new_data["English"] = data1[uuid].get("modifications", "")  # 更新 'English' 字段
            new_datas.append(new_data)

# 写入新的文件
new_file = "/Users/dehua/code/gpqa/outputs/all_data_v2_translation_new.jsonl"
with open(new_file, 'w', encoding='utf-8') as f3:
    for data in new_datas:
        f3.write(json.dumps(data, ensure_ascii=False))
        f3.write("\n")