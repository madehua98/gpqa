# 说明

**分用户标注**：每个用户标注 **50** 个视频。

用户登陆可以使用"user1"~"user6"，每个用户100视频，每个视频有多个题目

输出目录

`./outputs/`

## 代码配置

```bash
## 安装环境
cd gpqa
conda create -n gpqa python=3.10
conda activate gpqa
pip install flask flask_login markdown
```

运行代码
`python app_flask_long_video.py`

网页访问
`http://127.0.0.1:22005/gpqa`