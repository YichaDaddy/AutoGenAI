#!/usr/bin/env python3
"""
跨平台热点监测 - 可执行脚本
确保在 Claude Code 和 Trae 中运行结果一致
"""

import json
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# 领域关键词映射
NICHE_KEYWORDS = {
    "AI 人工智能": ["AI", "ChatGPT", "GPT", "DeepSeek", "大模型", "机器学习", "神经网络", "OpenAI", "Claude", "AIGC", "文生图", "文生视频"],
    "美妆护肤": ["美妆", "护肤", "化妆", "彩妆", "口红", "面膜", "美容", "穿搭", "时尚"],
    "科技数码": ["手机", "电脑", "数码", "AI", "芯片", "智能", "科技", "互联网", "编程"],
    "职场成长": ["职场", "工作", "求职", "面试", "晋升", "效率", "自我提升", "技能"],
    "财经投资": ["股票", "基金", "理财", "投资", "金融", "经济", "币圈", "加密货币"],
    "美食探店": ["美食", "餐厅", "探店", "食谱", "烹饪", "小吃", "网红店", "打卡"],
    "健身运动": ["健身", "运动", "瑜伽", "跑步", "减肥", "增肌", "训练", "马拉松"],
    "育儿知识": ["育儿", "宝宝", "怀孕", "亲子", "儿童", "早教", "喂养"],
    "游戏攻略": ["游戏", "电竞", "攻略", "赛季", "英雄", "皮肤", "手游", "端游"],
    "情感心理": ["情感", "心理", "恋爱", "婚姻", "情绪", "心理健康"],
    "汽车": ["汽车", "车", "新能源", "电动车", "自动驾驶", "特斯拉", "比亚迪"],
    "房产": ["房产", "房价", "买房", "租房", "房地产", "楼盘"],
    "娱乐": ["娱乐", "明星", "综艺", "电影", "电视剧", "八卦", "绯闻"],
    "体育": ["体育", "足球", "篮球", "NBA", "CBA", "奥运会", "冠军"],
    "军事": ["军事", "国防", "武器", "军演", "军队", "战机", "军舰"],
    "国际": ["国际", "外交", "美国", "欧洲", "全球", "联合国"]
}

# 领域关键词映射（英文）
NICHE_KEYWORDS_EN = {
    "AI 人工智能": ["AI", "ChatGPT", "GPT", "DeepSeek", "LLM", "machine learning", "AIGC", "OpenAI"],
    "美妆护肤": ["makeup", "skincare", "beauty", "fashion", "cosmetics"],
    "科技数码": ["tech", "AI", "smartphone", "computer", "programming", "software", "AI"],
    "职场成长": ["career", "job", "workplace", "interview", "resume", "productivity"],
    "财经投资": ["stock", "market", "invest", "finance", "crypto", "economy"],
    "美食探店": ["food", "restaurant", "recipe", "cooking", "dining"],
    "健身运动": ["fitness", "workout", "gym", "exercise", "training"],
    "育儿知识": ["parenting", "baby", "child", "pregnancy", "education"],
    "游戏攻略": ["game", "gaming", "esports", "video game", "gamer"],
    "情感心理": ["relationship", "dating", "marriage", "mental health", "psychology"],
    "汽车": ["car", "EV", "electric vehicle", "Tesla", "BYD", "auto", "automotive"],
    "房产": ["real estate", "housing", "property", "apartment"],
    "娱乐": ["entertainment", "celebrity", "movie", "tv show", "drama"],
    "体育": ["sports", "football", "basketball", "NBA", "Olympics"],
    "军事": ["military", "defense", "weapons", "army"],
    "国际": ["international", "global", "diplomacy", "US", "Europe"]
}

# 国内平台 API 端点
DOMESTIC_ENDPOINTS = {
    "微博": "https://60s.viki.moe/v2/weibo",
    "知乎": "https://60s.viki.moe/v2/zhihu",
    "百度": "https://60s.viki.moe/v2/baidu/hot",
    "抖音": "https://60s.viki.moe/v2/douyin",
    "B站": "https://60s.viki.moe/v2/bili",
    "今日头条": "https://60s.viki.moe/v2/toutiao"
}

# 免费微信公众号监控节点 (WeWeRSS 私有部署方案)
# 强烈建议在本地或服务器使用 Docker 部署 cooderl/wewerss
# 默认指向本地 WeWeRSS 服务，可以通过环境变量或参数覆盖
WEWERSS_BASE_URL = "http://127.0.0.1:4000/feeds/all.atom"

def get_wechat_articles(account_names: List[str]) -> Dict:
    """
    通过 WeWeRSS 节点获取最新文章。
    如果 account_names 包含 'all'，则不进行账号过滤，直接返回 WeWeRSS 订阅列表中的所有最新文章。
    """
    results = {}
    is_sync_all = 'all' in [name.lower() for name in account_names]
    
    # 初始化返回结构
    if not is_sync_all:
        for name in account_names:
             results[name] = {'platform': f'微信公众号 ({name})', 'data': [], 'error': None}
    else:
        results['全局监控'] = {'platform': 'WeWeRSS (全库同步)', 'data': [], 'error': None}

    try:
        headers = {'User-Agent': 'Trae-Agent/1.0'}
        response = requests.get(WEWERSS_BASE_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            is_atom = 'feed' in root.tag.lower()
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry') if is_atom else root.findall('.//item')
            
            for entry in entries:
                if is_atom:
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text if entry.find('{http://www.w3.org/2005/Atom}title') is not None else ''
                    author = entry.find('.//{http://www.w3.org/2005/Atom}name').text if entry.find('.//{http://www.w3.org/2005/Atom}name') is not None else '未知公众号'
                    link = entry.find('{http://www.w3.org/2005/Atom}link').attrib.get('href', '') if entry.find('{http://www.w3.org/2005/Atom}link') is not None else ''
                else:
                    title = entry.find('title').text if entry.find('title') is not None else ''
                    author = entry.find('author').text if entry.find('author') is not None else '未知公众号'
                    link = entry.find('link').text if entry.find('link') is not None else ''
                
                # 全局同步模式：不挑食，只要是 WeWeRSS 抓到的，都记录下来
                if is_sync_all:
                    if len(results['全局监控']['data']) < 15: # 全局模式最多取 15 篇最新文章
                        results['全局监控']['data'].append({
                            'title': f"[{author}] {title}",
                            'link': link,
                            'source': 'WeWeRSS'
                        })
                else:
                    # 精确匹配模式：只记录特定的几个号
                    matched_account = None
                    for name in account_names:
                        if name.lower() in author.lower() or name.lower() in title.lower():
                            matched_account = name
                            break
                    
                    if matched_account and len(results[matched_account]['data']) < 3:
                        results[matched_account]['data'].append({
                            'title': title,
                            'link': link,
                            'source': 'WeWeRSS'
                        })
        else:
             error_msg = f'WeWeRSS 节点访问失败 (HTTP {response.status_code})。请确保您已通过 Docker 启动 WeWeRSS。'
             if is_sync_all:
                 results['全局监控']['error'] = error_msg
             else:
                 for name in account_names:
                     results[name]['error'] = error_msg

    except Exception as e:
         error_msg = f'无法连接 WeWeRSS 节点: {str(e)}。提示：这是一项需要您私有部署的高级功能。'
         if is_sync_all:
             results['全局监控']['error'] = error_msg
         else:
             for name in account_names:
                 results[name]['error'] = error_msg

    return results


def calculate_relevance_score(title: str, niche: str) -> int:
    """计算热点与用户领域的相关度得分（0-10）"""
    if not niche or niche not in NICHE_KEYWORDS:
        return 5  # 默认中等相关

    keywords = set(NICHE_KEYWORDS.get(niche, []))
    if niche in NICHE_KEYWORDS_EN:
        keywords.update(NICHE_KEYWORDS_EN[niche])

    if not keywords:
        return 5

    score = 0
    title_lower = title.lower()
    for keyword in keywords:
        if keyword.lower() in title_lower:
            score += 3
            if score >= 9:
                break

    return min(10, score)


def get_domestic_trends(platforms: List[str] = None, limit: int = 10) -> Dict:
    """获取国内热点"""
    results = {}
    if platforms is None:
        platforms = list(DOMESTIC_ENDPOINTS.keys())

    for name in platforms:
        url = DOMESTIC_ENDPOINTS.get(name)
        if not url:
            continue
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = []
                raw_data = data.get('data', [])

                # 解析不同平台的返回格式
                for idx, item in enumerate(raw_data[:limit], 1):
                    if isinstance(item, dict):
                        title = item.get('title', item.get('word', item.get('name', str(item))))
                        hot = item.get('hot', item.get('heat', item.get('num', '')))
                        items.append({
                            'rank': idx,
                            'title': str(title),
                            'hot': str(hot),
                            'relevance': 0  # 待计算
                        })
                    else:
                        items.append({
                            'rank': idx,
                            'title': str(item),
                            'hot': '',
                            'relevance': 0
                        })

                results[name] = {
                    'platform': name,
                    'data': items,
                    'update_time': data.get('update_time', ''),
                    'error': None
                }
            else:
                results[name] = {'platform': name, 'data': [], 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            results[name] = {'platform': name, 'data': [], 'error': str(e)}

    return results


def get_overseas_trends_simulation(platforms: List[str] = None) -> Dict:
    """
    获取海外热点（模拟数据，因为需要 WebSearch）
    返回结构化提示，让 Claude 调用 WebSearch
    """
    if platforms is None:
        platforms = ['Reddit', 'TikTok', 'YouTube', 'Instagram']

    need_search = []
    for p in platforms:
        if p in ['Reddit', 'TikTok', 'YouTube', 'Instagram']:
            need_search.append(p)

    return {
        'type': 'overseas_search_needed',
        'platforms': need_search,
        'queries': {
            'Reddit': ['Reddit trending today', 'Reddit popular posts site:reddit.com'],
            'TikTok': ['TikTok trending today', 'TikTok viral videos trending'],
            'YouTube': ['YouTube trending today', 'YouTube trending videos'],
            'Instagram': ['Instagram trending hashtags today']
        },
        'message': '请使用 WebSearch 获取以下平台的热点信息'
    }


def annotate_trends_with_niche(trends: Dict, niche: str) -> Dict:
    """为热点标注相关度"""
    annotated = {}
    for platform, data in trends.items():
        if 'error' in data:
            annotated[platform] = data
            continue

        annotated_items = []
        for item in data.get('data', []):
            title = item.get('title', '')
            relevance = calculate_relevance_score(title, niche)
            item['relevance'] = relevance
            annotated_items.append(item)

        data['data'] = annotated_items
        annotated[platform] = data

    return annotated


def format_trends_for_display(trends: Dict, niche: str) -> str:
    """格式化热点数据用于展示"""
    output = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output.append(f"获取时间: {timestamp}")
    output.append(f"用户领域: {niche}")
    output.append("")

    for platform, data in trends.items():
        if 'error' in data:
            output.append(f"### {platform}")
            output.append(f"获取失败: {data['error']}")
            output.append("")
            continue

        items = data.get('data', [])
        output.append(f"## {platform}")
        output.append("")
        output.append("| 排名 | 话题 | 热度 | 相关度 |")
        output.append("|------|------|------|--------|")

        for item in items:
            rank = item.get('rank', '')
            title = item.get('title', '')
            hot = item.get('hot', '')
            relevance = item.get('relevance', 0)
            fire = "🔥" if relevance >= 6 else ""
            output.append(f"| {rank} | {title} | {hot} | {relevance}/10 {fire} |")

        output.append("")

    return "\n".join(output)


def main():
    """主函数：解析参数并执行"""
    args = sys.argv[1:]

    # 默认参数
    niche = None
    scope = "all"  # domestic, overseas, all
    platforms = None
    wechat_accounts = [] # 新增微信账号参数

    # 解析参数
    i = 0
    while i < len(args):
        if args[i] == '--niche' and i + 1 < len(args):
            niche = args[i + 1]
            i += 2
        elif args[i] == '--scope' and i + 1 < len(args):
            scope = args[i + 1]
            i += 2
        elif args[i] == '--platforms' and i + 1 < len(args):
            platforms = args[i + 1].split(',')
            i += 2
        elif args[i] == '--wechat' and i + 1 < len(args):
            wechat_accounts = args[i + 1].split(',')
            i += 2
        else:
            i += 1

    # 如果没有提供领域，打印使用说明
    if not niche:
        print("请提供 --niche 参数")
        print("用法: python main.py --niche 'AI 人工智能' --scope all --wechat '卡兹克,饼干哥哥'")
        return

    # 获取热点数据
    results = {}

    # 国内热点
    if scope in ['domestic', 'all']:
        if platforms:
            domestic_platforms = [p for p in platforms if p in DOMESTIC_ENDPOINTS]
        else:
            domestic_platforms = None
        domestic_trends = get_domestic_trends(domestic_platforms)
        results.update(domestic_trends)
        
    # 微信公众号监控
    if wechat_accounts:
        wechat_trends = get_wechat_articles(wechat_accounts)
        results.update(wechat_trends)

    # 海外热点（返回搜索提示）
    if scope in ['overseas', 'all']:
        overseas_result = get_overseas_trends_simulation()
        results['__overseas__'] = overseas_result

    # 标注相关度
    annotated = annotate_trends_with_niche(results, niche)

    # 输出结果（JSON 格式供程序解析）
    json_output = json.dumps(annotated, ensure_ascii=False, indent=2)
    print(json_output)
    
    # 将最新数据保存到文件，供渲染看板使用
    try:
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "latest_raw_data.json"), "w", encoding="utf-8") as f:
            f.write(json_output)
    except Exception as e:
        pass


if __name__ == "__main__":
    main()
