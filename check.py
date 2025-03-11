import json

# Function to check if a string contains Chinese characters
def contains_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)

# Function to process the JSONL file
def process_jsonl(input_jsonl_file_path):
    output = []

    with open(input_jsonl_file_path, 'r', encoding='utf-8') as file:
        # Read each line from the JSONL file
        for line in file:
            # Parse the JSON data from the current line
            data = json.loads(line.strip())
            

            for key, items in data.items():
                for item in items:
                    question = item.get('question', '')
                    answer = item.get('answer', '')
                    distractors = item.get('distractors', [])
                    
                    # Check if any of question, answer, or distractors contain Chinese
                    if contains_chinese(question) or contains_chinese(answer) or any(contains_chinese(d) for d in distractors):
                        output.append(item)
    
    return output

# Example usage
input_jsonl_file_path = '/Users/dehua/code/gpqa/outputs/all_data_v3.jsonl'  # Replace with the path to your input JSONL file

output = process_jsonl(input_jsonl_file_path)

# Output the result (or process further)
for data in output:
    print(data)
    print('\n')