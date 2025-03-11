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


user_info_path = f"./{text_files_dir}/user_info_translation.json"

need_deduplication_path = f"./{text_files_dir}/similar_questions_grouped.jsonl"
with open(need_deduplication_path, 'r', encoding='utf-8') as file:
    need_deduplication_datas = []
    for line in file.readlines():
        line = json.loads(line)
        need_deduplication_datas.append(line)


multiple_path = f"./{text_files_dir}/all_data_v2_translation.jsonl"
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
    
    multiple_file = f"{res_dir}/translation_{username}.jsonl"
    html_file = "display_translation.html"
    
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


@app.route("/submit", methods=["POST"])
def submit():
    username = session.get("username")
    if not username:
        # 处理未登录或未设置用户名的情况
        flash("请先登录。")
        return redirect(url_for("welcome"))

    ans_file = f"{res_dir}/ans_{username}.jsonl"
    deduplication_file = f"{res_dir}/deduplication_{username}.jsonl"
    multiple_file = f"{res_dir}/translation_{username}.jsonl"

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
        if source_page == "display_type":
            # 处理 question type 的提交
            current_idx = int(request.form.get("current_idx", 0))
            video_question_idx = int(request.form.get("video_question_idx", 0))
            curr_deduplication = request.form.getlist("deduplication")
            print(curr_deduplication)
            group_id = request.form.get("group_id", "")

            # 加载现有的 question_type 数据
            answer_data_dict = {}
            if os.path.exists(deduplication_file):
                with open(deduplication_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            d = json.loads(line)
                            answer_data_dict.update(d)
                        except json.JSONDecodeError:
                            continue

            # 更新当前视频的 question_type
            answer_data_dict[group_id] = curr_deduplication

            # 保存回 deduplication_file
            with open(deduplication_file, "w", encoding="utf-8") as f:
                for group_id, curr_deduplication in answer_data_dict.items():
                    json_line = json.dumps({group_id: curr_deduplication}, ensure_ascii=False)
                    f.write(json_line + "\n")

            # 更新 current_idx 和 video_question_idx
            session["current_idx"] = current_idx + 1
            session["video_question_idx"] = 0
            session.modified = True

            flash("Question Type 已成功更新。")
            return redirect(url_for("display_type"))

        # 处理标注数据的提交
        current_idx = int(request.form.get("current_idx", 0))
        uuid = request.form.get("uuid", "")
        text = request.form.get("question", "")
        print(request.form)
        marked_question = 'mark_question' in request.form
        print(marked_question)
        curr_multiple= request.form.getlist("multiple")
        print(f"curr_multiple is {curr_multiple}")
        annotations = curr_multiple

        # 获取修改内容
        modifications = None
        modified_content = request.form.get('question_english')
        print(modified_content)
        if modified_content:
            print(f"modifications is {modified_content}")

        # 更新标注和修改
        update_annotation_file(multiple_file, uuid, marked_question, annotations, modified_content)

        # 更新 video_question_idx 如果需要
        submit_success(
            username,
            current_idx,
            video_question_idx,
            user_data,
            user_info_path,
            video_question_number,
        )
        return redirect(url_for("display"))

    else:
        flash("Unknown operation.")
        return redirect(url_for("display"))
    
    return redirect(url_for("display"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT_NUM, debug=False)
