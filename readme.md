# 说明

**分用户标注**：每个用户标注 **100** 个题目。每个用户仅仅可以看到自己需要标注的100个题目和标注结果

用户信息路径

`./text_files/user_info.json`

去重题目输入文件

`./text_files/similar_questions_grouped.jsonl`

多项选择输入文件

`./text_files/toprp-with-confusion-options.jsonl`

输出目录

`./outputs/`

## 代码配置

```bash
## 安装环境
cd gpqa
conda create -n gpqa1 python=3.10
conda activate gpqa1
pip install flask flask_login markdown
```
将app_flask.py文件的第13行修改为自己的目录
`static_root_path = "/Users/dehua/code/gpqa"`

运行代码
`python app_flask.py`

网页访问
`http://127.0.0.1:22005/gpqa`