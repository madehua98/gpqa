import json

def convert_jsonl_to_dict_and_save(jsonl_file_path, output_json_file_path):
    result = {}
    
    with open(jsonl_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line.strip())  # Load each line as a dictionary
            chinese_text = data.get('Chinese')  # Get the Chinese text
            english_text = data.get('English')  # Get the English text
            
            if chinese_text and english_text:
                result[chinese_text] = english_text  # Add to result dictionary
    
    # Save the result as a JSON file
    with open(output_json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)
    return result
# Example usage
jsonl_file_path = '/Users/dehua/code/gpqa/outputs/all_data_v2_translation_new.jsonl'  # Replace with your actual file path
output_json_file_path = '/Users/dehua/code/gpqa/outputs/zh2en_v2.json'  # Specify the output JSON file path

dictionary = convert_jsonl_to_dict_and_save(jsonl_file_path, output_json_file_path)

print(f"Data has been converted and saved to {output_json_file_path}")


import json

def translate_chinese_to_english(jsonl_file_path, dictionary, output_json_file_path):
    updated_data = []

    with open(jsonl_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line.strip())  # Parse each line as a dictionary
            
            # Iterate through the keys (like "1iznvcAGjdg") and their corresponding list of data
            for key, items in data.items():
                for item in items:
                    # Translate the 'question' if it matches a key in the dictionary
                    if item.get('question') in dictionary:
                        item['question'] = dictionary[item['question']]
                    
                    # Translate the 'answer' if it matches a key in the dictionary
                    if item.get('answer') in dictionary:
                        item['answer'] = dictionary[item['answer']]
                    
                    # Translate each 'distractor' if it matches a key in the dictionary
                    item['distractors'] = [dictionary.get(d, d) for d in item.get('distractors', [])]
                
                # Append the updated data to the result list
                updated_data.append({key: items})

    # Save the updated data to a new JSON file
    with open(output_json_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(updated_data, output_file, ensure_ascii=False, indent=4)

# Example usage
jsonl_file_path = '/Users/dehua/code/gpqa/outputs/all_data.jsonl'  # Replace with the path to your input JSONL file
output_json_file_path = 'updated_data.json'  # Specify the path for the output JSON file
import json

def translate_chinese_to_english(jsonl_file_path, dictionary, output_jsonl_file_path):
    with open(jsonl_file_path, 'r', encoding='utf-8') as file, open(output_jsonl_file_path, 'w', encoding='utf-8') as output_file:
        for line in file:
            data = json.loads(line.strip())  # Parse each line as a dictionary
            
            # Iterate through the keys (like "1iznvcAGjdg") and their corresponding list of data
            for key, items in data.items():
                for item in items:
                    # Translate the 'question' if it matches a key in the dictionary
                    if item.get('question') in dictionary:
                        item['question'] = dictionary[item['question']]
                    
                    # Translate the 'answer' if it matches a key in the dictionary
                    if item.get('answer') in dictionary:
                        item['answer'] = dictionary[item['answer']]
                    
                    # Translate each 'distractor' if it matches a key in the dictionary
                    item['distractors'] = [dictionary.get(d, d) for d in item.get('distractors', [])]
                
                # Write the updated data to the output file in JSONL format
                output_file.write(json.dumps({key: items}, ensure_ascii=False) + '\n')

# Example usage
jsonl_file_path = '/Users/dehua/code/gpqa/outputs/all_data_v2.jsonl'  # Replace with the path to your input JSONL file
output_jsonl_file_path = '/Users/dehua/code/gpqa/outputs/all_data_v3.jsonl'  # Specify the path for the output JSONL file

template = "/Users/dehua/code/gpqa/outputs/zh2en_v2.json"
with open(template, 'r', encoding='utf-8') as f:
    dictionary = json.load(f)


translate_chinese_to_english(jsonl_file_path, dictionary, output_jsonl_file_path)

print(f"Data has been translated and saved to {output_jsonl_file_path}")

