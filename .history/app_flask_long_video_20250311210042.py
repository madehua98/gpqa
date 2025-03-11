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
    return redirect(url_for("display"))


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
    annotation_flag = False
    
    if not os.path.exists(annotation_file):
        return annotation_flag
        
    with open(annotation_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                annotation = json.loads(line)
                if uuid == annotation["uuid"]:
                    annotation_flag = True
                    break
            except json.JSONDecodeError:
                continue
                
    return annotation_flag


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
        annotation_flag = load_multiple_annotations(multiple_file, uuid)
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
            _is_val=0,
        )

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

import copy

# 设置和文件路径
res_dir = "./outputs"
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

multiple_path = "./text_files/long_video_all_new.jsonl"
with open(multiple_path, 'r', encoding='utf-8') as file:
    multiple_datas = [json.loads(line) for line in file.readlines()]

@app.route("/submit", methods=["POST"])
def submit():
    username = session.get("username")
    if not username:
        # 处理未登录或未设置用户名的情况
        flash("请先登录。")
        return redirect(url_for("welcome"))

    ans_file = f"{res_dir}/ans_{username}.jsonl"
    deduplication_file = f"{res_dir}/deduplication_{username}.jsonl"
    multiple_file = f"{res_dir}/multiple_true_options_{username}.jsonl"

    action = request.form.get("action", "")
    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(need_deduplication_datas) - 1)
    slice_end_idx = e_idx - s_idx
    source_page = request.form.get("source_page")

    current_idx = int(request.form.get("current_idx", 0))
    video_question_idx = int(request.form.get("video_question_idx", 0))
    video_question_number = int(request.form.get("video_question_number", 0))
    vid_name = request.form.get("video", "").split("/")[-1].split(".")[0]

    if action == "navigate":
        # 处理跳转到指定索引，不进行metadata的完备性检查
        try:
            next_idx = int(request.form.get("next_idx", 1)) - 1
            # 确保 next_idx 在视频范围内
            if next_idx < 0 or next_idx > slice_end_idx:
                flash("跳转的索引超出范围。")
                return redirect(url_for("display"))
            session["current_idx"] = next_idx
            session["video_question_idx"] = 0  # 切换视频时重置标注索引
            session.modified = True
            flash(f"已跳转到索引 {next_idx + 1}。")
            if source_page == "display_type":
                return redirect(url_for("display_type"))
            return redirect(url_for("display"))
        except ValueError:
            flash("无效的索引值。")
            if source_page == "display_type":
                return redirect(url_for("display_type"))
            return redirect(url_for("display"))

    elif action == "submit":
        # 处理标注数据的提交
        current_idx = int(request.form.get("current_idx", 0))
        s_idx = session.get("s_idx", 0)
        e_idx = session.get("e_idx", len(multiple_datas) - 1)
        datas_curr_user = multiple_datas[s_idx : e_idx + 1]
        curr_multiple_data = datas_curr_user[current_idx]
        uuid = request.form.get("uuid", "")
        text = request.form.get("question", "")
        print(request.form)
        curr_multiple= request.form.getlist("multiple")
        annotations = curr_multiple
        uuid = request.form.uuid
        for i in range(len(curr_multiple_data)):
            f"title_{i+1}"

        # 获取修改内容
        modifications = None
        modified_content = request.form.get('modified_content')
        if modified_content:
            modifications = json.loads(modified_content)
            print(f"modifications is {modifications}")

        return redirect(url_for("display"))

    else:
        flash("Unknown operation.")
        return redirect(url_for("display"))


def get_question_data(uuid):
    """根据uuid获取问题数据"""
    for item in multiple_datas:
        if item['uuid'] == uuid:
            return item
    return None


def update_annotation_file(ans_file, uuid, marked_question, annotations):
    """更新标注文件"""
    annotation_dict = {}

    # 读取现有的注释文件
    if os.path.exists(ans_file):
        with open(ans_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    annotation = json.loads(line)
                    if annotation["uuid"] == uuid:
                        # 更新指定的 uuid
                        annotation_dict[uuid] = {
                            "marked_question": marked_question,
                            "annotations": annotations
                        }
                    else:
                        annotation_dict[annotation["uuid"]] = annotation
                except json.JSONDecodeError:
                    continue

    # 写回注释文件
    with open(ans_file, "w", encoding="utf-8") as f:
        for uuid, data in annotation_dict.items():
            json.dump({"uuid": uuid, **data}, f, ensure_ascii=False)
            f.write("\n")


def get_question_data(uuid):
    """
    获取指定UUID的问题数据
    此处假设全局变量或导入了question_data_list
    根据实际情况可能需要调整
    """
    try:
        # 从你的数据源中找到对应UUID的问题
        for item in need_deduplication_datas:
            if item.get('uuid') == uuid:
                return item
        return None
    except Exception as e:
        print(f"获取问题数据时出错: {str(e)}")
        return None
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT_NUM, debug=False)
