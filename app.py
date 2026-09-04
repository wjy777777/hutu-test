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

# ---------- 25道题目 ----------
QUESTIONS = [
    {
        "q": "看到零食柜里最后一包薯片，你会？",
        "options": {
            "A": {"text": "立刻拆开吃掉，快乐最重要", "char_id": "tutu"},
            "B": {"text": "告诉自己'今天不能吃'，但还是忍不住", "char_id": "mami"},
            "C": {"text": "无所谓，吃不吃都行", "char_id": "xiaoguai"},
            "D": {"text": "研究一下配料表再决定", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "朋友约你去吃自助餐，你会？",
        "options": {
            "A": {"text": "兴奋地计划'先吃三轮'", "char_id": "tutu"},
            "B": {"text": "纠结半天'会不会胖'", "char_id": "xiaomei"},
            "C": {"text": "直接说'不去，人多太吵'", "char_id": "shuazi"},
            "D": {"text": "去，但默默计算性价比", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "妈妈在厨房做饭，你会？",
        "options": {
            "A": {"text": "跑进厨房偷吃", "char_id": "tutu"},
            "B": {"text": "帮忙洗菜切菜", "char_id": "xiaomei"},
            "C": {"text": "在客厅等着喊'好饿啊'", "char_id": "baba"},
            "D": {"text": "观察妈妈做饭的步骤", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "在朋友聚会上，你通常会？",
        "options": {
            "A": {"text": "积极带动气氛，话最多的那个", "char_id": "tutu"},
            "B": {"text": "安静坐着，偶尔插话", "char_id": "xiaomei"},
            "C": {"text": "坐在角落观察别人", "char_id": "xiaoguai"},
            "D": {"text": "负责组织游戏和活动", "char_id": "jiankang"}
        }
    },
    {
        "q": "朋友遇到困难时，你会？",
        "options": {
            "A": {"text": "冲上去帮忙，哪怕方法不太对", "char_id": "shuazi"},
            "B": {"text": "冷静分析问题，给出建议", "char_id": "zhuangzhuang"},
            "C": {"text": "陪在身边，说温暖的话", "char_id": "xiaomei"},
            "D": {"text": "讲个笑话让ta开心", "char_id": "baba"}
        }
    },
    {
        "q": "你的理想周末是？",
        "options": {
            "A": {"text": "和朋友一起疯玩", "char_id": "shuazi"},
            "B": {"text": "一个人安静待着", "char_id": "xiaoguai"},
            "C": {"text": "和家人一起看电视", "char_id": "baba"},
            "D": {"text": "出门探索新地方", "char_id": "kuaikuai"}
        }
    },
    {
        "q": "被人误会在意的事，你会？",
        "options": {
            "A": {"text": "直接怼回去，当场解释清楚", "char_id": "shuazi"},
            "B": {"text": "气鼓鼓地生闷气", "char_id": "mami"},
            "C": {"text": "算了，懒得解释", "char_id": "xiaoguai"},
            "D": {"text": "找机会温和地澄清", "char_id": "xiaomei"}
        }
    },
    {
        "q": "别人说你'不按常理出牌'，你更可能？",
        "options": {
            "A": {"text": "觉得挺好，说明我很特别", "char_id": "tutu"},
            "B": {"text": "生气，我要按自己方式来", "char_id": "mami"},
            "C": {"text": "反思一下，想想为什么", "char_id": "jiankang"},
            "D": {"text": "无所谓，继续做自己的事", "char_id": "xiaoguai"}
        }
    },
    {
        "q": "你最受不了别人什么？",
        "options": {
            "A": {"text": "装模作样", "char_id": "shuazi"},
            "B": {"text": "太吵闹", "char_id": "zhuangzhuang"},
            "C": {"text": "太凶、说话像刮风", "char_id": "tutu"},
            "D": {"text": "总爱指挥别人", "char_id": "mami"}
        }
    },
    {
        "q": "被家人唠叨时，你会？",
        "options": {
            "A": {"text": "左耳进右耳出", "char_id": "tutu"},
            "B": {"text": "认真听完然后照做", "char_id": "zhuangzhuang"},
            "C": {"text": "怼回去", "char_id": "shuazi"},
            "D": {"text": "心里烦但不表现出来", "char_id": "xiaomei"}
        }
    },
    {
        "q": "心情不好的时候，你会？",
        "options": {
            "A": {"text": "吃零食，吃开心就好", "char_id": "tutu"},
            "B": {"text": "一个人待着不说话", "char_id": "xiaoguai"},
            "C": {"text": "找朋友倾诉", "char_id": "xiaomei"},
            "D": {"text": "用游戏和运动发泄", "char_id": "jiankang"}
        }
    },
    {
        "q": "遇到困难时，你第一反应是？",
        "options": {
            "A": {"text": "求助身边人", "char_id": "tutu"},
            "B": {"text": "自己想办法解决", "char_id": "shuazi"},
            "C": {"text": "冷静分析后行动", "char_id": "zhuangzhuang"},
            "D": {"text": "先发一顿脾气再说", "char_id": "mami"}
        }
    },
    {
        "q": "有人需要帮助，你第一反应是？",
        "options": {
            "A": {"text": "毫不犹豫上前帮忙", "char_id": "jiankang"},
            "B": {"text": "先观察一下情况", "char_id": "zhuangzhuang"},
            "C": {"text": "叫上朋友一起帮忙", "char_id": "tutu"},
            "D": {"text": "觉得麻烦但不好意思拒绝", "char_id": "xiaomei"}
        }
    },
    {
        "q": "你最看重朋友的什么？",
        "options": {
            "A": {"text": "讲义气，随叫随到", "char_id": "shuazi"},
            "B": {"text": "真诚不虚假", "char_id": "jiankang"},
            "C": {"text": "能一起开心玩", "char_id": "tutu"},
            "D": {"text": "聪明，能聊得来", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你的做事风格更像？",
        "options": {
            "A": {"text": "想到就做，不犹豫", "char_id": "kuaikuai"},
            "B": {"text": "先计划再行动", "char_id": "zhuangzhuang"},
            "C": {"text": "随心所欲，看心情", "char_id": "tutu"},
            "D": {"text": "按规矩来，不出错", "char_id": "niuyeye"}
        }
    },
    {
        "q": "有人在你面前炫耀，你会？",
        "options": {
            "A": {"text": "直接拆穿ta", "char_id": "shuazi"},
            "B": {"text": "翻个白眼走开", "char_id": "xiaoguai"},
            "C": {"text": "默默远离这种人", "char_id": "zhuangzhuang"},
            "D": {"text": "配合演一下，心里偷笑", "char_id": "baba"}
        }
    },
    {
        "q": "你觉得自己最大的优点是？",
        "options": {
            "A": {"text": "善良单纯", "char_id": "tutu"},
            "B": {"text": "勇敢直爽", "char_id": "shuazi"},
            "C": {"text": "聪明冷静", "char_id": "zhuangzhuang"},
            "D": {"text": "温柔体贴", "char_id": "xiaomei"}
        }
    },
    {
        "q": "你觉得自己最大的缺点是？",
        "options": {
            "A": {"text": "太贪吃了", "char_id": "tutu"},
            "B": {"text": "脾气来得太快", "char_id": "mami"},
            "C": {"text": "想太多了", "char_id": "zhuangzhuang"},
            "D": {"text": "太容易相信别人", "char_id": "xiaomei"}
        }
    },
    {
        "q": "你的生活态度更像？",
        "options": {
            "A": {"text": "及时行乐，开心就好", "char_id": "tutu"},
            "B": {"text": "积极进取，不断突破", "char_id": "kuaikuai"},
            "C": {"text": "随遇而安，顺其自然", "char_id": "niuyeye"},
            "D": {"text": "谨慎规划，稳中求进", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "遇到不喜欢的食物，你会？",
        "options": {
            "A": {"text": "直接说不吃", "char_id": "shuazi"},
            "B": {"text": "皱着眉头吃一点", "char_id": "xiaomei"},
            "C": {"text": "趁人不注意偷偷倒掉", "char_id": "tutu"},
            "D": {"text": "分析为什么不喜欢", "char_id": "zhuangzhuang"}
        }
    },
    {
        "q": "你对待陌生人更像？",
        "options": {
            "A": {"text": "热情大方，主动搭话", "char_id": "jiankang"},
            "B": {"text": "保持距离，观察再说", "char_id": "xiaoguai"},
            "C": {"text": "友好微笑，但不多说", "char_id": "xiaomei"},
            "D": {"text": "看心情，有时候主动有时候冷漠", "char_id": "shuazi"}
        }
    },
    {
        "q": "你最喜欢的天气是？",
        "options": {
            "A": {"text": "大晴天，可以出去玩", "char_id": "tutu"},
            "B": {"text": "阴雨天，窝在家睡觉", "char_id": "xiaoguai"},
            "C": {"text": "下雪天，特别浪漫", "char_id": "xiaomei"},
            "D": {"text": "无所谓，什么天气都能找到乐子", "char_id": "baba"}
        }
    },
    {
        "q": "朋友向你借钱，你会？",
        "options": {
            "A": {"text": "能借就借，朋友有困难必须帮", "char_id": "jiankang"},
            "B": {"text": "问清楚用途再决定", "char_id": "zhuangzhuang"},
            "C": {"text": "直接拒绝，不想扯上钱", "char_id": "shuazi"},
            "D": {"text": "借了，但心里一直惦记着", "char_id": "mami"}
        }
    },
    {
        "q": "你觉得自己像什么动物？",
        "options": {
            "A": {"text": "狗——忠诚快乐", "char_id": "tutu"},
            "B": {"text": "猫——独立神秘", "char_id": "xiaoguai"},
            "C": {"text": "老虎——勇敢威猛", "char_id": "shuazi"},
            "D": {"text": "兔子——温柔可爱", "char_id": "xiaomei"}
        }
    },
    {
        "q": "朋友说你'太幼稚了'，你会？",
        "options": {
            "A": {"text": "觉得这是夸奖，快乐最重要", "char_id": "tutu"},
            "B": {"text": "有点不开心，但想想算了", "char_id": "xiaomei"},
            "C": {"text": "反驳：'这叫童心未泯'", "char_id": "baba"},
            "D": {"text": "反思一下自己哪里不够成熟", "char_id": "zhuangzhuang"}
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
        font-size: 0.9rem;
        color: #888;
        margin-bottom: 10px;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 10px 0;
        border: none;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(247, 151, 30, 0.4);
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
        font-size: 2rem;
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
    .option-btn {
        width: 100%;
        text-align: left;
        padding: 12px 16px;
        border-radius: 10px;
        border: 2px solid #e8ecf4;
        background: white;
        transition: all 0.2s;
        cursor: pointer;
        margin: 4px 0;
    }
    .option-btn:hover {
        border-color: #f7971e;
        background: #fef9e7;
    }
    .selected-option {
        border-color: #f7971e;
        background: #fef9e7;
    }
    .qr-container {
        background: #f8f9ff;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 标题 ----------
st.markdown('<div class="main-title">🏠 翻斗花园人格测试</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">测一测你是《大耳朵图图》里的谁？</div>', unsafe_allow_html=True)

# ---------- 侧边栏 ----------
with st.sidebar:
    st.header("📱 扫码访问")
    app_url = "https://你的地址.streamlit.app"
    
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
        st.markdown(f'<div class="progress-text">第 {q_index+1} / {total} 题</div>', unsafe_allow_html=True)
        st.progress((q_index) / total)

        st.markdown(f"### {q_data['q']}")

        options = q_data["options"]
        letters = list(options.keys())

        cols = st.columns(2)
        for i, letter in enumerate(letters):
            opt = options[letter]
            with cols[i % 2]:
                if st.button(f"{letter}. {opt['text']}", key=f"q{q_index}_{letter}", use_container_width=True):
                    st.session_state.scores[opt['char_id']] += 1
                    st.session_state.answers.append(letter)
                    st.session_state.current_q += 1
                    st.rerun()
    else:
        st.session_state.finished = True
        st.rerun()

# ---------- 结果展示 ----------
else:
    scores = st.session_state.scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_id = sorted_scores[0][0]
    top_char = next(c for c in CHARACTERS if c["id"] == top_id)

    # 显示结果
    st.balloons()
    st.markdown("---")
    st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="name">{top_char["emoji"]} 你是：{top_char["name"]}！</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{top_char["label"]}</div>', unsafe_allow_html=True)

    # 匹配度
    total_score = sum(scores.values())
    if total_score > 0:
        pct = int(scores[top_id] / total_score * 100)
        st.markdown(f"**匹配度：{pct}%**")
        st.progress(pct / 100)

    # 性格标签
    st.markdown("**性格标签：**" + " ".join([f'<span class="tag">{tag}</span>' for tag in top_char["tags"]]), unsafe_allow_html=True)

    # 性格描述
    st.markdown(f'<div class="desc">{top_char["description"]}</div>', unsafe_allow_html=True)

    # 经典语录
    st.markdown(f'<div class="quote">💬 {top_char["quote"]}</div>', unsafe_allow_html=True)

    # 适合职业
    st.markdown(f"**🎯 适合你的职业：**{top_char['career']}")

    # 所有角色排名
    st.markdown("---")
    st.markdown("### 📊 你的角色匹配排名")
    for i, (char_id, score) in enumerate(sorted_scores[:5]):
        char = next(c for c in CHARACTERS if c["id"] == char_id)
        pct = int(score / total_score * 100) if total_score > 0 else 0
        st.markdown(f"{i+1}. {char['emoji']} {char['name']} — {pct}%")

    st.markdown('</div>', unsafe_allow_html=True)

    # 分享按钮
    st.markdown("---")
    st.markdown("📤 **分享给朋友，看看ta是翻斗花园的谁？**")
    col1, col2, col3 = st.columns(3)
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