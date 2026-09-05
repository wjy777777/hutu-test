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

# 设置中文字体
try:
    mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC']
    mpl.rcParams['axes.unicode_minus'] = False
except:
    pass

# 加载API Key
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 页面配置
st.set_page_config(page_title="翻斗花园人格测试", page_icon="🏠", layout="wide")

# 25道题目 - 幽默风趣版
QUESTIONS = [
    {
        "q": "周末早上醒来，你第一件事是？",
        "options": [
            {"label": "A", "text": "🤳 摸手机刷视频，躺到饿得不行才起——手机才是真爱", "char_id": "tutu"},
            {"label": "B", "text": "🏃 立刻起床！今天有好多事要干！——卷王本王", "char_id": "kuaikuai"},
            {"label": "C", "text": "💤 继续睡，梦里啥都有——周公是我最好的朋友", "char_id": "xiaoguai"},
            {"label": "D", "text": "🍳 起床做饭，把全家人都叫起来吃——你就是那个'别人家的孩子'", "char_id": "mami"}
        ]
    },
    {
        "q": "你朋友突然放你鸽子，你会？",
        "options": [
            {"label": "A", "text": "😊 没事没事，我自己玩也开心——佛系青年本佛", "char_id": "tutu"},
            {"label": "B", "text": "😤 气死了！下次再也不约ta了！——小本本记仇第一名", "char_id": "shuazi"},
            {"label": "C", "text": "💰 正好，省钱了，回家躺着——省钱小能手", "char_id": "xiaoguai"},
            {"label": "D", "text": "📞 打电话问清楚，是不是出事了——操心老妈子体质", "char_id": "xiaomei"}
        ]
    },
    {
        "q": "在餐厅吃饭发现菜里有根头发，你会？",
        "options": [
            {"label": "A", "text": "🙈 默默挑出来继续吃——多一事不如少一事", "char_id": "niuyeye"},
            {"label": "B", "text": "📢 立刻叫经理！严肃投诉！——正义使者上线", "char_id": "shuazi"},
            {"label": "C", "text": "📸 先拍照发朋友圈——流量不能浪费", "char_id": "tutu"},
            {"label": "D", "text": "🔍 分析这头发是厨师还是服务员的——你怕不是福尔摩斯转世", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你最喜欢什么样的朋友？",
        "options": [
            {"label": "A", "text": "🍻 能一起吃吃喝喝、嘻嘻哈哈的——饭搭子最重要", "char_id": "tutu"},
            {"label": "B", "text": "🤝 靠谱、能讲真心话的——你就是个实在人", "char_id": "jiankang"},
            {"label": "C", "text": "🧠 聪明、能教我东西的——学霸收割机", "char_id": "zhuangzhuang"},
            {"label": "D", "text": "⚔️ 讲义气、有事真上的——古惑仔看多了吧", "char_id": "shuazi"}
        ]
    },
    {
        "q": "你的人生信条更像？",
        "options": [
            {"label": "A", "text": "😄 开心最重要，其他都是浮云——人间清醒", "char_id": "tutu"},
            {"label": "B", "text": "💪 做人要靠谱，说话要算数——行走的信任背书", "char_id": "jiankang"},
            {"label": "C", "text": "🏆 要么不做，要做就做到最好——卷界天花板", "char_id": "zhuangzhuang"},
            {"label": "D", "text": "🍷 人生苦短，及时行乐——今朝有酒今朝醉", "char_id": "baba"}
        ]
    },
    {
        "q": "你收拾房间的方式是？",
        "options": [
            {"label": "A", "text": "🗑️ 全部堆到一起，眼不见为净——懒人收纳法", "char_id": "tutu"},
            {"label": "B", "text": "📦 分门别类，整整齐齐——强迫症晚期患者", "char_id": "zhuangzhuang"},
            {"label": "C", "text": "🎭 看心情，心情好了就收拾——薛定谔的整洁", "char_id": "xiaomei"},
            {"label": "D", "text": "🏚️ 不收拾，乱才是家的感觉——乱室佳人/佳男", "char_id": "baba"}
        ]
    },
    {
        "q": "你突然中了一百万，第一件事是？",
        "options": [
            {"label": "A", "text": "🍔 先吃顿好的！吃最贵的！——吃货的终极梦想", "char_id": "tutu"},
            {"label": "B", "text": "📊 存起来，好好规划怎么花——理财大师就是你", "char_id": "zhuangzhuang"},
            {"label": "C", "text": "🎁 分给家人朋友，一起开心——散财童子转世", "char_id": "xiaomei"},
            {"label": "D", "text": "🛍️ 买一堆平时舍不得买的东西——购物车里清空", "char_id": "baba"}
        ]
    },
    {
        "q": "你最害怕什么事情？",
        "options": [
            {"label": "A", "text": "🍕 饿肚子！没有吃的太可怕了——胃比心大", "char_id": "tutu"},
            {"label": "B", "text": "💔 失去重要的人——重情重义本义", "char_id": "xiaomei"},
            {"label": "C", "text": "👀 被人看不起、被忽视——面子比天大", "char_id": "shuazi"},
            {"label": "D", "text": "📅 计划被打乱、失控的感觉——控制欲爆表", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你觉得自己像什么食物？",
        "options": [
            {"label": "A", "text": "🍲 火锅——热气腾腾，什么都往里加——社交牛逼症", "char_id": "tutu"},
            {"label": "B", "text": "🍦 冰淇淋——看着冷，其实很甜——外冷内热小天使", "char_id": "xiaomei"},
            {"label": "C", "text": "🌶️ 辣椒——看着普通，但很有劲儿——人狠话不多", "char_id": "shuazi"},
            {"label": "D", "text": "🍚 白米饭——百搭、靠谱、不能少——定海神针", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你遇到挫折的时候，第一反应是？",
        "options": [
            {"label": "A", "text": "😭 先哭一场，哭完再说——泪腺发达星人", "char_id": "xiaomei"},
            {"label": "B", "text": "🤬 骂一句脏话，然后想办法——暴躁但有用", "char_id": "shuazi"},
            {"label": "C", "text": "📱 找朋友吐槽，求安慰——专业求抱抱", "char_id": "tutu"},
            {"label": "D", "text": "🧐 冷静分析问题出在哪里——理性人本人", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你最喜欢的一句话是？",
        "options": [
            {"label": "A", "text": "🍜 今天吃啥？——人生终极哲学问题", "char_id": "tutu"},
            {"label": "B", "text": "💪 我相信你能行！——行走的鸡汤", "char_id": "jiankang"},
            {"label": "C", "text": "🦁 人要有骨气，不能怂——硬汉/女汉子代言人", "char_id": "shuazi"},
            {"label": "D", "text": "🤔 嗯，让我想想——深思熟虑代言人", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你出门前会花多长时间？",
        "options": [
            {"label": "A", "text": "⏱️ 5分钟，穿上衣服就走——速度与激情", "char_id": "kuaikuai"},
            {"label": "B", "text": "🕒 30分钟，得好好搭配一下——精致猪猪", "char_id": "xiaomei"},
            {"label": "C", "text": "🕐 1小时起，选衣服选到崩溃——选择困难症晚期", "char_id": "tutu"},
            {"label": "D", "text": "🎯 看情况，不赶时间就慢慢来——随心所欲派", "char_id": "baba"}
        ]
    },
    {
        "q": "你最讨厌什么事情？",
        "options": [
            {"label": "A", "text": "🗣️ 别人催我——越催越慢，再催熄火", "char_id": "tutu"},
            {"label": "B", "text": "🤥 别人骗我——信任是底线", "char_id": "shuazi"},
            {"label": "C", "text": "📢 别人唠叨我——唐僧本僧退退退", "char_id": "xiaoguai"},
            {"label": "D", "text": "⏳ 别人浪费我的时间——时间就是生命", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你觉得自己最大的魅力是什么？",
        "options": [
            {"label": "A", "text": "☀️ 我很快乐，跟我待着的人也会快乐——人间小太阳", "char_id": "tutu"},
            {"label": "B", "text": "🛡️ 我很坚强，遇到什么事都能扛住——铁打的汉子/女子", "char_id": "shuazi"},
            {"label": "C", "text": "🌸 我很温柔，会照顾别人的感受——治愈系天使", "char_id": "xiaomei"},
            {"label": "D", "text": "🧠 我很聪明，能帮别人解决问题——行走的百科全书", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你遇到困难时，会向谁求助？",
        "options": [
            {"label": "A", "text": "🙋 谁在就找谁，不挑——随缘求助法", "char_id": "tutu"},
            {"label": "B", "text": "🤝 找最靠谱的那个朋友——精准求助", "char_id": "jiankang"},
            {"label": "C", "text": "💪 自己扛，不想麻烦别人——独立自主小能手", "char_id": "shuazi"},
            {"label": "D", "text": "🧠 先自己想，想不通再找人——理性求助", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你最喜欢什么季节？",
        "options": [
            {"label": "A", "text": "☀️ 夏天——冰淇淋空调西瓜，人间天堂", "char_id": "tutu"},
            {"label": "B", "text": "🍂 秋天——不冷不热，刚好够美", "char_id": "xiaomei"},
            {"label": "C", "text": "❄️ 冬天——窝在被子里追剧，完美", "char_id": "xiaoguai"},
            {"label": "D", "text": "🌱 春天——万物复苏，我又活了", "char_id": "jiankang"}
        ]
    },
    {
        "q": "你在朋友圈里扮演什么角色？",
        "options": [
            {"label": "A", "text": "🎭 开心果——气氛组组长", "char_id": "tutu"},
            {"label": "B", "text": "👑 大姐大——有事我罩你", "char_id": "shuazi"},
            {"label": "C", "text": "👂 倾听者——情绪垃圾桶专业户", "char_id": "xiaomei"},
            {"label": "D", "text": "🧠 军师——诸葛转世", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你吃饭的时候最喜欢？",
        "options": [
            {"label": "A", "text": "🗣️ 边吃边说话，嘴巴根本停不下来——社交吃饭法", "char_id": "tutu"},
            {"label": "B", "text": "🍽️ 专心吃饭，享受美食——美食家本家", "char_id": "niuyeye"},
            {"label": "C", "text": "📱 边吃边看手机——手机才是下饭菜", "char_id": "baba"},
            {"label": "D", "text": "📸 先拍照发朋友圈再吃——相机先吃", "char_id": "xiaomei"}
        ]
    },
    {
        "q": "你看到流浪猫会？",
        "options": [
            {"label": "A", "text": "😍 冲上去撸！太可爱了！——猫奴本奴", "char_id": "tutu"},
            {"label": "B", "text": "🐱 蹲下看看，等它主动过来——尊重猫权", "char_id": "xiaomei"},
            {"label": "C", "text": "🍖 去买根火腿肠喂它——行动派爱心人士", "char_id": "niuyeye"},
            {"label": "D", "text": "👀 看两眼就走了——猫猫绝缘体", "char_id": "xiaoguai"}
        ]
    },
    {
        "q": "你最喜欢的颜色是？",
        "options": [
            {"label": "A", "text": "💛 黄色——看着就开心，元气满满", "char_id": "tutu"},
            {"label": "B", "text": "❤️ 红色——热烈有力量，霸气侧漏", "char_id": "shuazi"},
            {"label": "C", "text": "💗 粉色——温柔可爱，少女心爆棚", "char_id": "xiaomei"},
            {"label": "D", "text": "💙 蓝色——冷静理性，智慧担当", "char_id": "zhuangzhuang"}
        ]
    },
    {
        "q": "你遇到杠精会怎么办？",
        "options": [
            {"label": "A", "text": "⚔️ 和ta对线，谁怕谁！——键盘侠克星", "char_id": "shuazi"},
            {"label": "B", "text": "🙄 懒得理，浪费口舌——格局打开了", "char_id": "xiaoguai"},
            {"label": "C", "text": "🧠 用逻辑把ta说服——理性碾压", "char_id": "zhuangzhuang"},
            {"label": "D", "text": "😏 笑嘻嘻地附和，看ta表演——阴阳怪气大师", "char_id": "baba"}
        ]
    },
    {
        "q": "你觉得自己最大的缺点是什么？",
        "options": [
            {"label": "A", "text": "🍔 太贪吃了，根本管不住嘴——美食的奴隶", "char_id": "tutu"},
            {"label": "B", "text": "🔥 脾气太急说话太直——钢铁直男/女", "char_id": "shuazi"},
            {"label": "C", "text": "🤯 想太多容易纠结——精神内耗王者", "char_id": "zhuangzhuang"},
            {"label": "D", "text": "💗 太爱操心管不住自己——老妈子附体", "char_id": "mami"}
        ]
    },
    {
        "q": "你最想去哪里旅行？",
        "options": [
            {"label": "A", "text": "🍜 成都——从街头吃到街尾，吃到破产", "char_id": "tutu"},
            {"label": "B", "text": "🏔️ 西藏——净化心灵，洗涤灵魂", "char_id": "xiaomei"},
            {"label": "C", "text": "🗾 日本——干净精致有秩序，强迫症天堂", "char_id": "zhuangzhuang"},
            {"label": "D", "text": "🎒 随便哪里，有朋友一起就行——友谊第一", "char_id": "baba"}
        ]
    },
    {
        "q": "你对未来的态度是？",
        "options": [
            {"label": "A", "text": "😎 未来嘛，走一步看一步——随缘佛系", "char_id": "tutu"},
            {"label": "B", "text": "📋 我已经做好了五年规划——人生规划师", "char_id": "zhuangzhuang"},
            {"label": "C", "text": "🌈 相信未来会越来越好——人间希望", "char_id": "jiankang"},
            {"label": "D", "text": "😰 有点焦虑，但不想去想——鸵鸟心态", "char_id": "xiaoguai"}
        ]
    },
    {
        "q": "用一句话形容自己，你会说？",
        "options": [
            {"label": "A", "text": "🍗 我是快乐的吃货，烦恼吃完就忘——没心没肺第一名", "char_id": "tutu"},
            {"label": "B", "text": "⚔️ 我是勇敢的战士，不轻易认输——打不死的小强", "char_id": "shuazi"},
            {"label": "C", "text": "☀️ 我是温柔的小太阳，温暖身边的人——治愈系本愈", "char_id": "xiaomei"},
            {"label": "D", "text": "🧠 我是冷静的智者，用脑子解决问题——理性脑本脑", "char_id": "zhuangzhuang"}
        ]
    }
]

# CSS美化
st.markdown("""
<style>
    .stApp {
        background: #faf8f5;
    }
    
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
        color: #888;
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
    
    .question-text {
        font-size: 1.4rem;
        font-weight: 600;
        margin: 20px 0 15px 0;
        color: #2d3748;
        text-align: center;
        padding: 15px 20px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stButton > button {
        width: 100%;
        background: white;
        color: #2d3748;
        font-size: 1rem;
        font-weight: 500;
        padding: 14px 10px;
        border: 2px solid #e8e0d8;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        white-space: normal;
        word-wrap: break-word;
        height: auto;
        min-height: 55px;
        text-align: left;
    }
    
    .stButton > button:hover {
        border-color: #f7971e;
        background: #fef9e7;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(247, 151, 30, 0.15);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    .result-hero {
        text-align: center;
        padding: 30px 20px 20px 20px;
        background: linear-gradient(135deg, #fef9e7 0%, #fdebd0 50%, #fef9e7 100%);
        border-radius: 24px;
        margin-bottom: 25px;
        border: 2px solid #f7d9a0;
        position: relative;
        overflow: hidden;
    }
    
    .result-hero::before {
        content: "✨";
        position: absolute;
        top: 10px;
        left: 20px;
        font-size: 2rem;
        opacity: 0.3;
    }
    
    .result-hero::after {
        content: "✨";
        position: absolute;
        bottom: 10px;
        right: 20px;
        font-size: 2rem;
        opacity: 0.3;
    }
    
    .result-emoji {
        font-size: 4.5rem;
        display: block;
        margin-bottom: 5px;
    }
    
    .result-name {
        font-size: 2.6rem;
        font-weight: 800;
        color: #2d3748;
        margin: 5px 0;
    }
    
    .result-label {
        font-size: 1.2rem;
        color: #f7971e;
        font-weight: 600;
        background: rgba(247, 151, 30, 0.12);
        padding: 4px 18px;
        border-radius: 20px;
        display: inline-block;
        margin: 5px 0 10px 0;
    }
    
    .result-mood {
        font-size: 1.1rem;
        color: #e67e22;
        margin: 8px 0 12px 0;
        font-weight: 500;
    }
    
    .match-bar {
        background: #e8e0d8;
        border-radius: 12px;
        height: 28px;
        margin: 12px 0 15px 0;
        overflow: hidden;
        position: relative;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .match-fill {
        height: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #f7971e, #ffd200);
        transition: width 1s ease;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 12px;
        color: white;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .tags-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin: 12px 0 15px 0;
    }
    
    .tag {
        display: inline-block;
        background: #f7971e;
        color: white;
        padding: 5px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(247, 151, 30, 0.25);
    }
    
    .result-desc {
        font-size: 1.05rem;
        color: #4a5568;
        margin: 15px 0;
        background: rgba(255,255,255,0.7);
        padding: 18px 22px;
        border-radius: 14px;
        line-height: 1.9;
        border: 1px solid rgba(247, 151, 30, 0.15);
        text-align: left;
    }
    
    .result-quote {
        font-size: 1.15rem;
        color: #e67e22;
        font-style: italic;
        background: white;
        padding: 12px 20px;
        border-radius: 12px;
        display: inline-block;
        border-left: 4px solid #f7971e;
        margin: 5px 0 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .result-career {
        font-size: 1rem;
        color: #4a5568;
        background: #eef2f7;
        padding: 10px 18px;
        border-radius: 10px;
        display: inline-block;
        margin: 5px 0;
    }
    
    .funny-extra {
        margin-top: 15px;
        padding: 14px 18px;
        background: white;
        border-radius: 12px;
        font-size: 0.95rem;
        color: #666;
        border: 1px dashed #f7971e;
        text-align: center;
    }
    
    .rank-card {
        background: white;
        padding: 10px 16px;
        border-radius: 10px;
        margin: 5px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        border: 1px solid #f0ebe5;
        transition: all 0.2s ease;
    }
    
    .rank-card:hover {
        border-color: #f7971e;
        background: #fef9e7;
    }
    
    .rank-number {
        font-weight: 700;
        color: #f7971e;
        min-width: 28px;
        font-size: 1rem;
    }
    
    .rank-emoji {
        font-size: 1.4rem;
    }
    
    .rank-name {
        font-weight: 600;
        color: #2d3748;
        flex: 1;
    }
    
    .rank-pct {
        font-weight: 600;
        color: #f7971e;
        background: #fef3e0;
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
    }
    
    .rank-badge {
        font-size: 0.8rem;
        color: #e67e22;
        font-weight: 500;
    }
    
    .footer {
        text-align: center;
        color: #ccc;
        font-size: 0.8rem;
        margin-top: 50px;
        padding: 20px 0;
        border-top: 1px solid #eee;
    }
    
    .qr-container {
        background: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin-top: 10px;
        border: 1px solid #f0ebe5;
    }
    
    .bottom-buttons {
        margin-top: 20px;
    }
    
    .section-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #f7d9a0, transparent);
        margin: 30px 0;
    }
    
    .share-box {
        background: #f8f6f3;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #e8e0d8;
        font-size: 0.9rem;
        color: #555;
        word-break: break-all;
        font-family: monospace;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">🏠 翻斗花园人格测试</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">测一测你是《大耳朵图图》里的谁？</div>', unsafe_allow_html=True)

# 侧边栏
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
    st.caption("😄 幽默测试，开心就好")

# 初始化
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
    st.session_state.scores = {c["id"]: 0 for c in CHARACTERS}
    st.session_state.answers = []
    st.session_state.finished = False

# 重置
if st.sidebar.button("🔄 重新测试"):
    st.session_state.current_q = 0
    st.session_state.scores = {c["id"]: 0 for c in CHARACTERS}
    st.session_state.answers = []
    st.session_state.finished = False
    st.rerun()

# 主逻辑
if not st.session_state.finished:
    q_index = st.session_state.current_q
    total = len(QUESTIONS)

    if q_index < total:
        q_data = QUESTIONS[q_index]
        st.markdown(f'<div class="progress-text">第 {q_index + 1} / {total} 题</div>', unsafe_allow_html=True)
        st.progress((q_index) / total)

        st.markdown(f'<div class="question-text">{q_data["q"]}</div>', unsafe_allow_html=True)

        options = q_data["options"]
        
        cols = st.columns(2)
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if st.button(
                    f'{opt["label"]}. {opt["text"]}',
                    key=f"q{q_index}_{opt['label']}",
                    use_container_width=True
                ):
                    st.session_state.scores[opt['char_id']] += 1
                    st.session_state.answers.append(opt['label'])
                    st.session_state.current_q += 1
                    st.rerun()

        st.markdown('<div class="bottom-buttons">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if q_index > 0:
                if st.button("⬅️ 上一题", use_container_width=True):
                    if st.session_state.answers:
                        last_answer = st.session_state.answers.pop()
                        prev_q = QUESTIONS[q_index - 1]
                        for opt in prev_q["options"]:
                            if opt["label"] == last_answer:
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

# 结果展示
else:
    scores = st.session_state.scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_id = sorted_scores[0][0]
    top_char = next(c for c in CHARACTERS if c["id"] == top_id)

    total_score = sum(scores.values())
    pct = int(scores[top_id] / total_score * 100) if total_score > 0 else 0

    if pct >= 60:
        mood = "🎉 亲生的！你就是翻斗花园本园！"
    elif pct >= 45:
        mood = "😄 太像了！你怕不是从动画片里走出来的！"
    elif pct >= 30:
        mood = "🤔 有点意思！你跟ta有八分相似！"
    else:
        mood = "😏 你确定你不是在演ta？再测一次试试！"

    st.balloons()
    
    st.markdown(f"""
    <div class="result-hero">
        <span class="result-emoji">{top_char["emoji"]}</span>
        <div class="result-name">你就是：{top_char["name"]}！</div>
        <div class="result-label">{top_char["label"]}</div>
        <div class="result-mood">{mood}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin: 5px 0 10px 0;">
        <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #666;">
            <span>匹配度</span>
            <span style="font-weight: 700; color: #f7971e;">{pct}%</span>
        </div>
        <div class="match-bar">
            <div class="match-fill" style="width: {pct}%;">
                {pct}%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in top_char["tags"]])
    st.markdown(f'<div class="tags-container">{tags_html}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="result-desc">{top_char["description"]}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<div class="result-quote">💬 {top_char["quote"]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="result-career">🎯 适合职业：{top_char["career"]}</div>', unsafe_allow_html=True)

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

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown("### 📊 你的角色匹配排名")
    
    rank_emojis = ["🥇", "🥈", "🥉"]
    for i, (char_id, score) in enumerate(sorted_scores[:5]):
        char = next(c for c in CHARACTERS if c["id"] == char_id)
        pct_i = int(score / total_score * 100) if total_score > 0 else 0
        
        if i == 0:
            badge = "⭐ 你就是ta！"
        elif i == 1:
            badge = "很接近！"
        elif i == 2:
            badge = "也不错！"
        else:
            badge = ""
        
        rank_icon = rank_emojis[i] if i < 3 else f"{i+1}."
        
        st.markdown(f"""
        <div class="rank-card">
            <span class="rank-number">{rank_icon}</span>
            <span class="rank-emoji">{char["emoji"]}</span>
            <span class="rank-name">{char["name"]}</span>
            <span class="rank-pct">{pct_i}%</span>
            <span class="rank-badge">{badge}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown("### 📤 分享给朋友")
    share_text = f"🏠 我测了翻斗花园人格测试，我是{top_char['name']}！{top_char['emoji']} 快来测测你是《大耳朵图图》里的谁？ 👉 {app_url}"
    st.markdown(f'<div class="share-box">{share_text}</div>', unsafe_allow_html=True)
    st.caption("💡 复制上面的文字，分享到朋友圈或群聊")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("📋 复制结果", use_container_width=True):
            st.write("📋 已复制到剪贴板！")
            st.balloons()
    with col2:
        if st.button("🔄 再测一次", use_container_width=True):
            st.session_state.current_q = 0
            st.session_state.scores = {c["id"]: 0 for c in CHARACTERS}
            st.session_state.answers = []
            st.session_state.finished = False
            st.rerun()

# 页脚
st.markdown("""
<div class="footer">
Made with ❤️ · 翻斗花园人格测试 · 2026
</div>
""", unsafe_allow_html=True)