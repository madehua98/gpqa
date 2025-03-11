from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
)
from datetime import timedelta
import json
import os
import markdown

# ======== static and global variables ========
static_root_path = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=static_root_path)
app.secret_key = os.urandom(24)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=100)
PORT_NUM = 22005
subpath = "/gpqa/"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "welcome"

local_video_dir = "./examples/youtube_sampled"
res_dir = "./outputs"
# 检查目录是否存在，如果不存在则创建
if not os.path.exists(res_dir):
    os.makedirs(res_dir)
    print(f"目录 '{res_dir}' 已创建")
else:
    print(f"目录 '{res_dir}' 已存在")

text_files_dir = "text_files"


user_info_path = f"./{text_files_dir}/user_info_long_video.json"

need_deduplication_path = f"./{text_files_dir}/similar_questions_grouped.jsonl"
with open(need_deduplication_path, 'r', encoding='utf-8') as file:
    need_deduplication_datas = []
    for line in file.readlines():
        line = json.loads(line)
        need_deduplication_datas.append(line)


multiple_path = f"./{text_files_dir}/long_video_all_new.jsonl"
with open(multiple_path, 'r', encoding='utf-8') as file:
    multiple_datas = []
    for line in file.readlines():
        line = json.loads(line)
        multiple_datas.append(line)



# ======== textual static contents ========
with open(f"./templates/html_text_en/deduplication.txt", "r", encoding="utf-8") as file:
    deduplication = file.read()

with open(f"./templates/html_text_en/translation.txt", "r", encoding="utf-8") as file:
    multiple = file.read()


subscore_def_en_list = []
subscore_files = ["multiple.txt"]
for fname in subscore_files:
    with open(f"./templates/html_text_en/{fname}", "r", encoding="utf-8") as file:
        content = file.read()
    subscore_def_en_list.append(content)


# ======== user info ========
current_user_dict = {}
with open(user_info_path, "r", encoding="utf-8") as f:
    user_data = json.load(f)
users = list(user_data.keys())
print("users ", users)


s_idx_user_mapping = {}
for user in users:
    curr_user_dict = user_data.get(user)
    s_idx = curr_user_dict.get("s_idx", 0)
    s_idx_user_mapping[f"{s_idx}"] = curr_user_dict.get("username", user)


# ======== user login part ========
class User(UserMixin):
    def __init__(self, id):
        print("user init")
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        print("load user ", user_id)
        return User(user_id)
    else:
        print("user_id not in users_list")
    return None


# ======== webpage_v2 contents ========
@app.route(f"{subpath}", methods=["GET"])
def start():
    return redirect(url_for("welcome"))


@app.route(f"{subpath}welcome", methods=["GET", "POST"])
def welcome():
    session["current_idx"] = 0
    # session["pre_anno_answers"]={}
    session["admin"] = None
    session["s_idx_val"] = 0
    session["e_idx_val"] = len(need_deduplication_datas) - 1

    html_file = "welcome_distractor.html"
    deduplication_anno = deduplication
    multiple_anno = multiple

    # deduplication_anno = markdown.markdown(deduplication_anno)
    return render_template(html_file, deduplication_anno=deduplication_anno, multiple_anno=multiple_anno)



@app.route(f"{subpath}login_method_1", methods=["POST"])
def login_method_1():
    username = request.form["username"]
    ans_path = f""
    if username in users:
        print("user ", username)
        curr_user_dict = user_data.get(username)
        ans_path = f"{res_dir}/ans_{username}.jsonl"
    else:
        return redirect(url_for("welcome"))
    user = User(username)
    login_user(user)
    curr_user_dict = user_data.get(username)
    session["username"] = curr_user_dict.get("username", username)
    session["s_idx"] = curr_user_dict.get("s_idx", 0)
    session["e_idx"] = curr_user_dict.get("e_idx", len(need_deduplication_datas) - 1)
    session["current_idx"] = curr_user_dict.get("current_idx", 0)
    return redirect(url_for("display_type"))

@app.route(f"{subpath}login_method_2", methods=["POST"])
def login_method_2():
    username = request.form["username"]
    if username in users:
        print("user ", username)
        curr_user_dict = user_data.get(username)
    else:
        return redirect(url_for("welcome"))

    user = User(username)
    login_user(user)

    curr_user_dict = user_data.get(username)
    session["username"] = curr_user_dict.get("username", username)
    session["s_idx"] = curr_user_dict.get("s_idx", 0)
    session["e_idx"] = curr_user_dict.get("e_idx", len(multiple_datas) - 1)
    session["current_idx"] = curr_user_dict.get("current_idx", 0)
    return redirect(url_for("display"))


def load_questions_type(deduplication_file, vid_name):
    type_data_list = []
    if os.path.exists(deduplication_file):
        with open(deduplication_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    type_data_list.append(d)
                except json.JSONDecodeError:
                    continue
    current_question_types = {}
    for type_data in type_data_list:
        if vid_name in type_data.keys():
            current_question_types = type_data[vid_name]
    return current_question_types


def load_annotations(annotation_file, group_id):
    annotations = []
    if not os.path.exists(annotation_file):
        return annotations
    with open(annotation_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                video_annotations = json.loads(line)
                if group_id in video_annotations.keys():
                    annotations = video_annotations[group_id]
                    break
            except json.JSONDecodeError:
                continue
    if not annotations:
        annotations = [
        ]
    return annotations

def load_multiple_annotations(annotation_file, uuid):
    annotations = []
    annotation_flag = False
    modifications = None
    
    if not os.path.exists(annotation_file):
        return annotations, annotation_flag, modifications
        
    with open(annotation_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                annotation = json.loads(line)
                if uuid == annotation["uuid"]:
                    annotation_flag = True
                    if annotation.get("marked_question", False):
                        annotations = [uuid]  # 如果整个问题被标记删除
                    else:
                        annotations = annotation.get("delete_options", [])  # 获取被标记删除的选项
                    modifications = annotation.get("modifications")
                    break
            except json.JSONDecodeError:
                continue
                
    return annotations, annotation_flag, modifications


@app.route(f"{subpath}annotating", methods=["GET", "POST"])
def display():
    username = session.get("username")
    if not username:
        return redirect(url_for("welcome"))

    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(multiple_datas) - 1)
    datas_curr_user = multiple_datas[s_idx : e_idx + 1]
    
    multiple_file = f"{res_dir}/longvideo_{username}.jsonl"
    html_file = "display_longvideo.html"
    
    multiple_anno = multiple
    subscore_def = subscore_def_en_list
    
    current_idx = session.get("current_idx", 0)
    print("curr_idx in display ", current_idx)

    slice_start_idx = 0
    slice_end_idx = len(datas_curr_user) - 1

    if current_idx <= slice_end_idx:
        curr_multiple_data = datas_curr_user[current_idx]
        uuid = curr_multiple_data["uuid"]
        print("data in display ", f"{uuid}")

        # 加载标注和修改内容
        annotations, annotation_flag, modifications = load_multiple_annotations(multiple_file, uuid)

        # 处理标注状态 - 恢复到之前的逻辑
        all_annotations = {data["uuid"]: False for data in datas_curr_user}
        try:
            with open(multiple_file, 'r', encoding='utf-8') as file:
                for line in file:
                    try:
                        annotation = json.loads(line)
                        if annotation["uuid"] in all_annotations:
                            all_annotations[annotation["uuid"]] = True
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            print("Annotation file not found")

        
        return render_template(
            html_file,
            multiple_anno=multiple_anno,
            subscore_def=subscore_def,
            start_index=slice_start_idx,
            status_dict=all_annotations,
            question_dict=curr_multiple_data,
            end_index=slice_end_idx,
            uuid=uuid,
            username=username,
            annotation_flag=annotation_flag,
            current_idx=current_idx,
            annotations=annotations,
            modifications=modifications,
            _is_val=0,
        )

    else:
        current_idx = 0
        session["current_idx"] = current_idx
        session["video_question_idx"] = 0
        user_data[username]["current_idx"] = session["current_idx"]
        user_data[username]["video_question_idx"] = session["video_question_idx"]
        with open(user_info_path, "w", encoding="utf-8") as file:
            json.dump(user_data, file, indent=4, ensure_ascii=False)

        print("curr_video_idx in display ", current_idx)
        return redirect(url_for("display"))


@app.route(f"{subpath}annotating_type", methods=["GET", "POST"])
def display_type():
    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(need_deduplication_datas) - 1)
    datas_curr_user = need_deduplication_datas[s_idx : e_idx + 1]
    username = session.get("username")
    if not username:
        flash("请先登录。")
        return redirect(url_for("welcome"))
    deduplication_file = f"{res_dir}/deduplication_{username}.jsonl"
    current_idx = int(session.get("current_idx", 0))
    print("curr_data_idx in display_type ", current_idx)

    slice_start_idx = 0
    slice_end_idx = len(datas_curr_user) - 1
    if current_idx <= slice_end_idx:

        groud_id = datas_curr_user[current_idx]['group_id']
        print("groud in display_type ", f"{groud_id}")

        answer_data_dict = {}
        if os.path.exists(deduplication_file):
            with open(deduplication_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        answer_data_dict.update(d)
                    except json.JSONDecodeError:
                        continue

        answered_vid_list = list(answer_data_dict.keys())
        annotation_flag =False
        current_answers = []
        if groud_id in answered_vid_list:
            annotation_flag = True
            current_answers = answer_data_dict[groud_id]

        print("current_answers (list) ", current_answers)

        html_file = "display_type.html"
        subscore_def = subscore_def_en_list
        deduplication_anno = deduplication
        language = session.get("language", "en")
        print("language in display_type ", language)

        curr_deduplication_data = datas_curr_user[current_idx]
        group_id = curr_deduplication_data["group_id"]

        return render_template(
            html_file,
            deduplication_anno=deduplication_anno,
            multiple_annp=multiple,
            start_index=slice_start_idx,
            end_index=slice_end_idx,
            current_idx=current_idx,
            group_id=group_id,
            question_list=curr_deduplication_data["items"],
            answered_vid_list=answered_vid_list,
            annotation_flag=annotation_flag,
            selected_deduplications=current_answers,
            _is_val=0,
        )
    else:
        current_idx = 0
        session["current_idx"] = current_idx
        user_data[username]["current_idx"] = session["current_idx"]
        with open(user_info_path, "w", encoding="utf-8") as file:
            json.dump(user_info_path, file, indent=4, ensure_ascii=False)

        print("curr_idx in display_type ", current_idx)
        return redirect(url_for("display_type"))


@app.route("/navigate_main", methods=["POST"])
def navigate_main():
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    current_idx = int(request.form.get("current_idx", 0))
    direction = request.form.get("direction", "")

    if direction == "next":
        next_idx = current_idx + 1
    elif direction == "last":
        next_idx = current_idx - 1
    else:
        next_idx = current_idx

    # 更新 session 中的 current_idx
    session["current_idx"] = next_idx
    
    return redirect(url_for("display"))


def submit_success(
    username,
    current_idx,
    video_question_idx,
    user_data,
    user_info_path,
    video_question_number,
):
    if video_question_idx + 1 >= video_question_number:
        session["current_idx"] = current_idx + 1
        session["video_question_idx"] = 0
        session.modified = True
    else:
        session["video_question_idx"] = video_question_idx + 1

    print("idx after submission ", session.get("current_idx", 0))
    print("video_question_idx after submission ", session.get("video_question_idx", 0))

    # 更新用户数据
    if username not in user_data:
        user_data[username] = {}

    user_data[username]["current_idx"] = session["current_idx"]
    user_data[username]["video_question_idx"] = session["video_question_idx"]

    with open(user_info_path, "w", encoding="utf-8") as file:
        json.dump(user_data, file, indent=4, ensure_ascii=False)
    print("*" * 100)
    flash("提交成功！")
    print("*" * 100)


def update_annotation_file(ans_file, uuid, marked_question, annotations, modifications=None):
    annotation_dict = {}

    # 读取现有的注释文件
    if os.path.exists(ans_file):
        with open(ans_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    annotation = json.loads(line)
                    current_uuid = annotation.get("uuid")
                    if current_uuid:
                        if current_uuid == uuid:
                            # 更新指定的 uuid
                            if marked_question:
                                annotation_dict[current_uuid] = {
                                    "marked_question": True,
                                    "delete_options": 'all',
                                    "modifications": None  # 如果题目被标记删除，清空修改
                                }
                            else:
                                annotation_dict[current_uuid] = {
                                    "marked_question": False,
                                    "delete_options": annotations,
                                    "modifications": modifications  # 直接使用前端传来的修改内容
                                }
                        else:
                            # 保持其他 uuid 的原有状态
                            annotation_dict[current_uuid] = annotation
                except json.JSONDecodeError:
                    continue

    # 如果文件不存在或 uuid 不在文件中，则添加新的注释
    if uuid not in annotation_dict:
        annotation_dict[uuid] = {
            "uuid": uuid,
            "marked_question": marked_question,
            "delete_options": 'all' if marked_question else annotations,
            "modifications": None if marked_question else modifications
        }

    # 写回 ans_file
    with open(ans_file, "w", encoding="utf-8") as f:
        for uid, data in annotation_dict.items():
            json.dump({"uuid": uid, **data}, f, ensure_ascii=False)
            f.write("\n")


# 处理标注数据的提交
@app.route('/submit', methods=['POST'])
def submit():
    try:
        # 获取基础表单数据
        current_idx = int(request.form.get("current_idx", 0))
        uuid = request.form.get("uuid", "")
        source_page = request.form.get("source_page", "")
        action = request.form.get("action", "")
        
        # 如果是导航操作，执行相应的导航逻辑
        if action == "navigate":
            next_idx = int(request.form.get("next_idx", 1)) - 1  # Convert to 0-based index
            return redirect(url_for('display', idx=next_idx))
        
        # 处理提交的修改数据
        if action == "submit":
            # 获取原始问题数据
            try:
                question_dict = get_question_by_uuid(uuid)
                if not question_dict:
                    flash("Error: Question not found")
                    return redirect(url_for('display', idx=current_idx))
            except Exception as e:
                flash(f"Error loading question data: {str(e)}")
                return redirect(url_for('display', idx=current_idx))
            
            # 收集所有修改内容
            modifications = {}
            
            # 获取每个问题的修改内容
            for i in range(1, len(question_dict.get('data', [])) + 1):
                question_mods = {}
                
                # 标题修改
                title = request.form.get(f"title_{i}")
                if title and title != question_dict['data'][i-1]['title']:
                    question_mods['title'] = title
                
                # 选项修改
                choices = {}
                choice_a = request.form.get(f"choice_a_{i}")
                choice_b = request.form.get(f"choice_b_{i}")
                choice_c = request.form.get(f"choice_c_{i}")
                choice_d = request.form.get(f"choice_d_{i}")
                
                if choice_a and choice_a != question_dict['data'][i-1]['choices']['A']:
                    choices['A'] = choice_a
                if choice_b and choice_b != question_dict['data'][i-1]['choices']['B']:
                    choices['B'] = choice_b
                if choice_c and choice_c != question_dict['data'][i-1]['choices']['C']:
                    choices['C'] = choice_c
                if choice_d and choice_d != question_dict['data'][i-1]['choices']['D']:
                    choices['D'] = choice_d
                
                if choices:
                    question_mods['choices'] = choices
                
                # 元数据修改
                metadata_fields = [
                    'correct_answer', 'hierarchy', 'time_reference', 
                    'video_type', 'question_type', 'wrong_choice_design', 'data_id'
                ]
                
                for field in metadata_fields:
                    field_value = request.form.get(f"{field}_{i}")
                    if field_value and field_value != question_dict['data'][i-1][field]:
                        question_mods[field] = field_value
                
                # 如果有修改，添加到总修改列表
                if question_mods:
                    modifications[i-1] = question_mods
            
            # 如果有修改，更新文件
            if modifications:
                try:
                    # 创建一个修改后的副本
                    updated_question_dict = copy.deepcopy(question_dict)
                    
                    # 应用所有修改
                    for idx, mods in modifications.items():
                        for field, value in mods.items():
                            if field == 'choices':
                                for choice_key, choice_value in value.items():
                                    updated_question_dict['data'][idx]['choices'][choice_key] = choice_value
                            else:
                                updated_question_dict['data'][idx][field] = value
                    
                    # 将更新后的内容写入文件
                    save_modified_question(uuid, updated_question_dict)
                    
                    # 记录修改日志
                    log_modifications(uuid, modifications, current_user.id if current_user.is_authenticated else "anonymous")
                    
                    flash("Changes saved successfully!")
                except Exception as e:
                    flash(f"Error saving changes: {str(e)}")
            else:
                flash("No changes detected.")
            
            # 重定向回显示页面
            return redirect(url_for('display', idx=current_idx))
    
    except Exception as e:
        flash(f"Error processing form: {str(e)}")
        return redirect(url_for('display', idx=0))

# 保存修改后的问题
def save_modified_question(uuid, updated_data):
    """
    将修改后的问题数据保存到文件。
    
    Args:
        uuid (str): 问题的UUID
        updated_data (dict): 更新后的问题数据
    """
    # 确保目录存在
    output_dir = os.path.join(ANNOTATIONS_DIR, 'modified')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存到文件
    output_file = os.path.join(output_dir, f"{uuid}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    # 可选：更新主数据源
    # update_main_data_source(uuid, updated_data)

# 记录修改日志
def log_modifications(uuid, modifications, user_id):
    """
    记录修改日志，包括谁在什么时间修改了什么内容。
    
    Args:
        uuid (str): 问题的UUID
        modifications (dict): 修改内容
        user_id (str): 用户ID
    """
    log_dir = os.path.join(ANNOTATIONS_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        "uuid": uuid,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "modifications": modifications
    }
    
    log_file = os.path.join(log_dir, f"modification_log_{datetime.now().strftime('%Y%m%d')}.jsonl")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        return redirect(url_for("display"))

    else:
        flash("Unknown operation.")
        return redirect(url_for("display"))
    
    return redirect(url_for("display"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT_NUM, debug=False)
