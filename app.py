import streamlit as st
import time
import os
import json
import random
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.express as px
from collections import Counter
import qrcode
from io import BytesIO
from characters import CHARACTERS

# ---------- 设置中文字体 ----------
try:
    mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC']
    mpl.rcParams['axes.unicode_minus'] = False
except:
    pass

# ---------- 加载API Key ----------
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# ---------- 页面配置 ----------
st.set_page_config(page_title="翻斗花园人格测试", page_icon="🏠", layout="wide")

# ---------- 25道全新题目 ----------
QUESTIONS = [
    {
        "q": "周末早上醒来，你第一件事是？",
        "options": {
            "A": {"text": "摸手机刷视频，躺到饿得不行才起", "char_id": "tutu"},
            "B": {"text": "立刻起床，今天有好多事要干！", "char_id": "kuaikuai"},
            "C": {"text": "继续睡，梦里啥都有", "char_id": "xiaoguai"},
            "D": {"text": "起床做饭，把全家人都叫起来吃", "char_id": "mami"}
        }
    },
    {
        "q": "你朋友突然放你鸽子，你会？",
        "options": {
            "A": {"text": "没事没事，我自己玩也开心", "char_id": "tutu"},
            "B": {"text": "气死了！下次再也不约ta了！", "char_id": "shuazi"},
            "C": {"text": "正好，省钱了，回家躺着", "char_id": "xiaoguai"},
            "D": {"text": "打电话问清楚原因，是不是出事了", "char_id": "xiaomei"}
        }
    },
    {
        "q": "你在餐厅吃饭，发现菜里有根头发，你会？",
        "options": {
            "A": {"text": "默默挑出来继续吃，不想惹麻烦", "char_id": "niuyeye"},
            "B": {"text": "立刻叫服务员，严肃投诉", "char_id": "shuazi"},
            "C": {"text": "拍照发朋友圈，先吐槽再说", "char_id": "tutu"},
            "D": {"text": "分析一下，这头发是厨师还是服务员的", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你最喜欢什么样的朋友？",
        "options": {
            "A": {"text": "能一起吃吃喝喝、嘻嘻哈哈的", "char_id": "tutu"},
            "B": {"text": "靠谱、能讲真心话的", "char_id": "jiankang"},
            "C": {"text": "聪明、能教我东西的", "char_id": "zhuangzhuang"},
            "D": {"text": "讲义气、有事真上的", "char_id": "shuazi"}
        }
    },
    {
        "q": "你的人生信条更像？",
        "options": {
            "A": {"text": "开心最重要，其他都是浮云", "char_id": "tutu"},
            "B": {"text": "做人要靠谱，说话要算数", "char_id": "jiankang"},
            "C": {"text": "要么不做，要做就做到最好", "char_id": "zhuangzhuang"},
            "D": {"text": "人生苦短，及时行乐", "char_id": "baba"}
        }
    },
    {
        "q": "你收拾房间的方式是？",
        "options": {
            "A": {"text": "全部堆到一起，眼不见为净", "char_id": "tutu"},
            "B": {"text": "分门别类，整整齐齐", "char_id": "zhuangzhuang"},
            "C": {"text": "看心情，心情好了就收拾", "char_id": "xiaomei"},
            "D": {"text": "不收拾，乱才是家的感觉", "char_id": "baba"}
        }
    },
    {
        "q": "你突然中了一百万，第一件事是？",
        "options": {
            "A": {"text": "先吃顿好的！吃最贵的！", "char_id": "tutu"},
            "B": {"text": "存起来，好好规划怎么花", "char_id": "zhuangzhuang"},
            "C": {"text": "分给家人朋友，大家一起开心", "char_id": "xiaomei"},
            "D": {"text": "买一堆平时舍不得买的东西", "char_id": "baba"}
        }
    },
    {
        "q": "你最害怕什么事情？",
        "options": {
            "A": {"text": "饿肚子！没有吃的太可怕了", "char_id": "tutu"},
            "B": {"text": "失去重要的人", "char_id": "xiaomei"},
            "C": {"text": "被人看不起、被人忽视", "char_id": "shuazi"},
            "D": {"text": "计划被打乱、失控的感觉", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你觉得自己像什么食物？",
        "options": {
            "A": {"text": "火锅——热气腾腾，什么都往里加", "char_id": "tutu"},
            "B": {"text": "冰淇淋——看着冷，其实很甜", "char_id": "xiaomei"},
            "C": {"text": "辣椒——看着普通，但很有劲儿", "char_id": "shuazi"},
            "D": {"text": "白米饭——百搭、靠谱、不能少", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你遇到挫折的时候，第一反应是？",
        "options": {
            "A": {"text": "先哭一场，哭完再说", "char_id": "xiaomei"},
            "B": {"text": "骂一句脏话，然后想办法", "char_id": "shuazi"},
            "C": {"text": "找朋友吐槽，求安慰", "char_id": "tutu"},
            "D": {"text": "冷静分析问题出在哪里", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你最喜欢的一句话是？",
        "options": {
            "A": {"text": "今天吃啥？", "char_id": "tutu"},
            "B": {"text": "我相信你能行！", "char_id": "jiankang"},
            "C": {"text": "人要有骨气，不能怂", "char_id": "shuazi"},
            "D": {"text": "嗯，让我想想", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你出门前会花多长时间？",
        "options": {
            "A": {"text": "5分钟，穿上衣服就走", "char_id": "kuaikuai"},
            "B": {"text": "30分钟，得好好搭配一下", "char_id": "xiaomei"},
            "C": {"text": "1小时起，选衣服选到崩溃", "char_id": "tutu"},
            "D": {"text": "看情况，不赶时间就慢慢来", "char_id": "baba"}
        }
    },
    {
        "q": "你最讨厌什么事情？",
        "options": {
            "A": {"text": "别人催我", "char_id": "tutu"},
            "B": {"text": "别人骗我", "char_id": "shuazi"},
            "C": {"text": "别人唠叨我", "char_id": "xiaoguai"},
            "D": {"text": "别人浪费我的时间", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你觉得自己最大的魅力是什么？",
        "options": {
            "A": {"text": "我很快乐，跟我待着的人也会快乐", "char_id": "tutu"},
            "B": {"text": "我很坚强，遇到什么事都能扛住", "char_id": "shuazi"},
            "C": {"text": "我很温柔，会照顾别人的感受", "char_id": "xiaomei"},
            "D": {"text": "我很聪明，能帮别人解决问题", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你遇到困难时，会向谁求助？",
        "options": {
            "A": {"text": "谁在就找谁，不挑", "char_id": "tutu"},
            "B": {"text": "找最靠谱的那个朋友", "char_id": "jiankang"},
            "C": {"text": "自己扛，不想麻烦别人", "char_id": "shuazi"},
            "D": {"text": "先自己想，想不通再找人", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你最喜欢什么季节？",
        "options": {
            "A": {"text": "夏天——可以吃冰淇淋、吹空调", "char_id": "tutu"},
            "B": {"text": "秋天——不冷不热，刚刚好", "char_id": "xiaomei"},
            "C": {"text": "冬天——可以窝在被子里不出来", "char_id": "xiaoguai"},
            "D": {"text": "春天——万物复苏，充满希望", "char_id": "jiankang"}
        }
    },
    {
        "q": "你在朋友圈里扮演什么角色？",
        "options": {
            "A": {"text": "开心果——负责搞笑和活跃气氛", "char_id": "tutu"},
            "B": {"text": "大姐大——有事找我我罩你", "char_id": "shuazi"},
            "C": {"text": "倾听者——耐心听大家倾诉", "char_id": "xiaomei"},
            "D": {"text": "军师——帮大家出主意", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你吃饭的时候最喜欢？",
        "options": {
            "A": {"text": "边吃边说话，嘴巴停不下来", "char_id": "tutu"},
            "B": {"text": "专心吃饭，享受美食", "char_id": "niuyeye"},
            "C": {"text": "边吃边看手机", "char_id": "baba"},
            "D": {"text": "先拍照发朋友圈再吃", "char_id": "xiaomei"}
        }
    },
    {
        "q": "你看到流浪猫会？",
        "options": {
            "A": {"text": "冲上去摸摸摸，太可爱了", "char_id": "tutu"},
            "B": {"text": "蹲下看看，等它主动过来", "char_id": "xiaomei"},
            "C": {"text": "去便利店买根火腿肠喂它", "char_id": "niuyeye"},
            "D": {"text": "看两眼就走了，不感兴趣", "char_id": "xiaoguai"}
        }
    },
    {
        "q": "你最喜欢的颜色是？",
        "options": {
            "A": {"text": "黄色——看着就开心", "char_id": "tutu"},
            "B": {"text": "红色——热烈、有力量", "char_id": "shuazi"},
            "C": {"text": "粉色——温柔、可爱", "char_id": "xiaomei"},
            "D": {"text": "蓝色——冷静、理性", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你遇到杠精会怎么办？",
        "options": {
            "A": {"text": "和ta对线，谁怕谁", "char_id": "shuazi"},
            "B": {"text": "懒得理，浪费口舌", "char_id": "xiaoguai"},
            "C": {"text": "用逻辑把ta说服", "char_id": "zhuangzhuang"},
            "D": {"text": "笑嘻嘻地附和，看ta表演", "char_id": "baba"}
        }
    },
    {
        "q": "你觉得自己最大的缺点是什么？",
        "options": {
            "A": {"text": "太贪吃、管不住嘴", "char_id": "tutu"},
            "B": {"text": "脾气太急、说话太直", "char_id": "shuazi"},
            "C": {"text": "想太多、容易纠结", "char_id": "zhuangzhuang"},
            "D": {"text": "太爱操心、管不住自己", "char_id": "mami"}
        }
    },
    {
        "q": "你最想去哪里旅行？",
        "options": {
            "A": {"text": "成都——吃遍所有小吃", "char_id": "tutu"},
            "B": {"text": "西藏——感受神圣和宁静", "char_id": "xiaomei"},
            "C": {"text": "日本——干净、精致、有秩序", "char_id": "zhuangzhuang"},
            "D": {"text": "随便哪里，有朋友一起就行", "char_id": "baba"}
        }
    },
    {
        "q": "你对未来的态度是？",
        "options": {
            "A": {"text": "未来嘛，走一步看一步", "char_id": "tutu"},
            "B": {"text": "我已经做好了五年规划", "char_id": "zhuangzhuang"},
            "C": {"text": "相信未来会越来越好", "char_id": "jiankang"},
            "D": {"text": "有点焦虑，但不想去想", "char_id": "xiaoguai"}
        }
    },
    {
        "q": "用一句话形容自己，你会说？",
        "options": {
            "A": {"text": "我是快乐的吃货，烦恼吃完就忘", "char_id": "tutu"},
            "B": {"text": "我是勇敢的战士，不轻易认输", "char_id": "shuazi"},
            "C": {"text": "我是温柔的小太阳，温暖身边的人", "char_id": "xiaomei"},
            "D": {"text": "我是冷静的智者，用脑子解决问题", "char_id": "zhuangzhuang"}
        }
    }
]

# ---------- CSS美化 ----------
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 20px 0 5px 0;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
    .progress-text {
        text-align: center;
        font-size: 1rem;
        color: #888;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .question-number {
        text-align: center;
        font-size: 0.85rem;
        color: #aaa;
        margin-bottom: 15px;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 12px 0;
        border: none;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(247, 151, 30, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(247, 151, 30, 0.5);
        color: white;
    }
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.8rem;
        margin-top: 40px;
        padding: 20px 0;
        border-top: 1px solid #eee;
    }
    .result-box {
        background: linear-gradient(135deg, #fef9e7 0%, #fdebd0 100%);
        padding: 30px;
        border-radius: 20px;
        border-left: 6px solid #f7971e;
        margin-top: 20px;
        line-height: 1.9;
    }
    .result-box .name {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2d3748;
    }
    .result-box .label {
        font-size: 1.2rem;
        color: #f7971e;
        font-weight: 600;
    }
    .result-box .desc {
        font-size: 1rem;
        color: #4a5568;
        margin: 15px 0;
        background: rgba(255,255,255,0.5);
        padding: 15px 18px;
        border-radius: 12px;
        line-height: 1.8;
    }
    .result-box .quote {
        font-size: 1.1rem;
        color: #e67e22;
        font-style: italic;
        background: #fff;
        padding: 10px 16px;
        border-radius: 10px;
        display: inline-block;
    }
    .tag {
        display: inline-block;
        background: #f7971e;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 3px 5px 3px 0;
    }
    .qr-container {
        background: #f8f9ff;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin-top: 10px;
    }
    .bottom-buttons {
        margin-top: 25px;
    }
    .option-btn {
        display: block;
        width: 100%;
        padding: 14px 18px;
        margin: 6px 0;
        border-radius: 12px;
        border: 2px solid #e8ecf4;
        background: white;
        text-align: left;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .option-btn:hover {
        border-color: #f7971e;
        background: #fef9e7;
        transform: translateX(4px);
    }
    .option-label {
        display: inline-block;
        background: #f7971e;
        color: white;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        text-align: center;
        line-height: 28px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 12px;
    }
    .funny-extra {
        margin-top: 15px;
        padding: 12px 16px;
        background: #fff;
        border-radius: 10px;
        font-size: 0.95rem;
        color: #888;
        border: 1px dashed #f7971e;
    }
    .mood-text {
        font-size: 1rem;
        color: #e67e22;
        margin: 5px 0 10px 0;
    }
    .rank-item {
        padding: 6px 12px;
        border-radius: 8px;
        margin: 3px 0;
        background: rgba(255,255,255,0.6);
    }
</style>
""", unsafe_allow_html=True)

# ---------- 标题 ----------
st.markdown('<div class="main-title">🏠 翻斗花园人格测试</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">测一测你是《大耳朵图图》里的谁？</div>', unsafe_allow_html=True)

# ---------- 侧边栏 ----------
with st.sidebar:
    st.header("📱 扫码访问")
    app_url = "https://hutu-test-ih9koxugfjcycv3xxeahsg.streamlit.app"

    try:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(app_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#f7971e", back_color="white")
        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)
        st.markdown('<div class="qr-container">', unsafe_allow_html=True)
        st.image(buf, caption="扫码测试", use_container_width=True)
        st.download_button(
            label="⬇️ 下载二维码",
            data=buf.getvalue(),
            file_name="翻斗花园测试二维码.png",
            mime="image/png",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.caption("部署后自动生成二维码")

    st.markdown("---")
    st.caption("🎬 15个角色，25道题")
    st.caption("💡 选最像你的答案，不是最理想的")

# ---------- 初始化 ----------
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
    st.session_state.scores = {c["id"]: 0 for c in CHARACTERS}
    st.session_state.answers = []
    st.session_state.finished = False

# ---------- 重置 ----------
if st.sidebar.button("🔄 重新测试"):
    st.session_state.current_q = 0
    st.session_state.scores = {c["id"]: 0 for c in CHARACTERS}
    st.session_state.answers = []
    st.session_state.finished = False
    st.rerun()

# ---------- 主逻辑 ----------
if not st.session_state.finished:
    q_index = st.session_state.current_q
    total = len(QUESTIONS)

    if q_index < total:
        q_data = QUESTIONS[q_index]
        # 显示进度 - 修复序号显示（从1开始）
        st.markdown(f'<div class="progress-text">第 {q_index + 1} / {total} 题</div>', unsafe_allow_html=True)
        st.progress((q_index) / total)

        # 显示题目 - 用普通文本不加#
        st.markdown(f'<div style="font-size:1.3rem;font-weight:600;margin:15px 0 10px 0;color:#2d3748;">{q_data["q"]}</div>', unsafe_allow_html=True)

        options = q_data["options"]
        letters = list(options.keys())

        # 选项用两列布局
        cols = st.columns(2)
        for i, letter in enumerate(letters):
            opt = options[letter]
            with cols[i % 2]:
                # 美化选项按钮 - 带字母标签
                if st.button(
                    f"<span style='display:inline-block;background:#f7971e;color:white;border-radius:50%;width:28px;height:28px;text-align:center;line-height:28px;font-weight:700;font-size:0.85rem;margin-right:12px;'>{letter}</span> {opt['text']}",
                    key=f"q{q_index}_{letter}",
                    use_container_width=True
                ):
                    st.session_state.scores[opt['char_id']] += 1
                    st.session_state.answers.append(letter)
                    st.session_state.current_q += 1
                    st.rerun()

        # ----- 底部按钮：上一题 + 重新开始 -----
        st.markdown('<div class="bottom-buttons">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if q_index > 0:
                if st.button("⬅️ 上一题", use_container_width=True):
                    if st.session_state.answers:
                        last_answer = st.session_state.answers.pop()
                        prev_q = QUESTIONS[q_index - 1]
                        for letter, opt in prev_q["options"].items():
                            if letter == last_answer:
                                st.session_state.scores[opt['char_id']] -= 1
                                break
                        st.session_state.current_q -= 1
                        st.rerun()
        with col3:
            if st.button("🔄 重新开始", use_container_width=True):
                st.session_state.current_q = 0
                st.session_state.scores = {c["id"]: 0 for c in CHARACTERS}
                st.session_state.answers = []
                st.session_state.finished = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.session_state.finished = True
        st.rerun()

# ---------- 结果展示 ----------
else:
    scores = st.session_state.scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_id = sorted_scores[0][0]
    top_char = next(c for c in CHARACTERS if c["id"] == top_id)

    total_score = sum(scores.values())
    pct = int(scores[top_id] / total_score * 100) if total_score > 0 else 0

    # 根据匹配度给不同的幽默评价
    if pct >= 60:
        mood = "🎉 亲生的！你就是翻斗花园本园！"
    elif pct >= 45:
        mood = "😄 太像了！你怕不是从动画片里走出来的！"
    elif pct >= 30:
        mood = "🤔 有点意思！你跟ta有八分相似！"
    else:
        mood = "😏 你确定你不是在演ta？再测一次试试！"

    st.balloons()
    st.markdown("---")
    st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="name">{top_char["emoji"]} 你就是：{top_char["name"]}！</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{top_char["label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mood-text">{mood}</div>', unsafe_allow_html=True)

    st.markdown(f"**匹配度：{pct}%**")
    st.progress(pct / 100)

    st.markdown("**性格标签：**" + " ".join([f'<span class="tag">{tag}</span>' for tag in top_char["tags"]]), unsafe_allow_html=True)
    st.markdown(f'<div class="desc">{top_char["description"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="quote">💬 {top_char["quote"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**🎯 适合你的职业：**{top_char['career']}")

    # 趣味附加信息
    funny_extra = {
        "tutu": "🍔 温馨提示：做这个测试消耗了50卡路里，建议奖励自己一顿好的！",
        "shuazi": "💪 温馨提示：你的气场太强了，建议偶尔也温柔一点～",
        "xiaomei": "🌸 温馨提示：你这么可爱，小心被图图缠上！",
        "zhuangzhuang": "🧠 温馨提示：偶尔也让脑子休息一下，学学图图傻乐～",
        "mami": "🔥 温馨提示：火气大的时候默念'亲生的亲生的'",
        "baba": "🎤 温馨提示：下次KTV请务必叫上我！",
        "xiaoguai": "🐱 温馨提示：高冷可以，但别冷到朋友哦～",
        "jiankang": "🌟 温馨提示：你这么正能量，建议去当幼儿园老师！",
        "niuyeye": "🏠 温馨提示：面冷心热的人最值得交朋友！",
        "kuaikuai": "💨 温馨提示：慢一点，生活不是比赛～",
        "yeye": "🌾 温馨提示：倔强可以，别倔到把牛都拉跑了！",
        "xiaodouding": "👶 温馨提示：想要什么就直接说，别哭！",
        "dahu": "🐯 温馨提示：捣蛋可以，记得帮妈妈收拾！",
        "tiaotiao": "🦘 温馨提示：歇会儿吧，我看得都累了！",
        "wangzi": "🤴 温馨提示：表演欲这么强，建议去学表演！"
    }

    st.markdown(f'<div class="funny-extra">😄 {funny_extra.get(top_id, "你真是太有趣了！")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 你的角色匹配排名")
    for i, (char_id, score) in enumerate(sorted_scores[:5]):
        char = next(c for c in CHARACTERS if c["id"] == char_id)
        pct_i = int(score / total_score * 100) if total_score > 0 else 0
        if i == 0:
            st.markdown(f'<div class="rank-item">🥇 {char["emoji"]} <b>{char["name"]}</b> — {pct_i}% ⭐ 你就是ta！</div>', unsafe_allow_html=True)
        elif i == 1:
            st.markdown(f'<div class="rank-item">🥈 {char["emoji"]} <b>{char["name"]}</b> — {pct_i}%</div>', unsafe_allow_html=True)
        elif i == 2:
            st.markdown(f'<div class="rank-item">🥉 {char["emoji"]} <b>{char["name"]}</b> — {pct_i}%</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="rank-item">   {i+1}. {char["emoji"]} {char["name"]} — {pct_i}%</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("📤 **分享给朋友，看看ta是翻斗花园的谁？**")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        share_text = f"🏠 我测了翻斗花园人格测试，我是{top_char['name']}！{top_char['emoji']} 快来测测你是《大耳朵图图》里的谁？ 👉 {app_url}"
        st.code(share_text, language="text")
    with col2:
        if st.button("🔄 再测一次", use_container_width=True):
            st.session_state.current_q = 0
            st.session_state.scores = {c["id"]: 0 for c in CHARACTERS}
            st.session_state.answers = []
            st.session_state.finished = False
            st.rerun()

# ---------- 页脚 ----------
st.markdown("""
<div class="footer">
Made with ❤️ · 翻斗花园人格测试 · 2026
</div>
""", unsafe_allow_html=True)