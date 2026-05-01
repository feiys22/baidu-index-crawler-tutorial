"""
百度指数批量爬虫 - 完整可运行版本

使用方法：
1. 安装依赖：pip install qdata
2. 获取百度 Cookie（见 docs/02-cookie-guide.md）
3. 填入下方 COOKIE_LIST（用三引号包裹！）
4. 修改 KEYWORDS 和 CITY_LIST（如需要）
5. 运行：python crawl_baidu_index.py

注意事项：
- Cookie 会过期（约7-30天），过期后需重新获取
- 大规模爬取建议用多账号 Cookie 轮询
- 遇到 REQUEST_LIMITED 是正常现象，程序会自动重试
"""

from qdata.baidu_index import get_search_index
import csv
import time
import random
import json
import os

# ====================== 核心配置区 ======================
# 【重要】请在这里填入你的百度 Cookie，至少 2 个，越多越稳定
# Cookie 格式：用三个单引号 ''' 包裹完整 Cookie 字符串
# 获取方法见：docs/02-cookie-guide.md
COOKIE_LIST = [
    # ============================================
    # 示例格式（请替换成你自己的真实 Cookie）：
    # '''BDUSS=xxx; BAIDUID=xxx; H_PS_PSSID=xxx; ...'''
    # ============================================
    '''请在这里填入第一个百度账号的完整Cookie''',
    '''请在这里填入第二个百度账号的完整Cookie''',
]

# 要爬取的关键词列表（可自行修改）
KEYWORDS = [
   
    '新质生产力', '人工智能', '就业'
    
]

# 全国城市列表（城市名, 百度指数城市代码）
# 完整144城市列表见：docs/07-city-codes.md
CITY_LIST = [
    ("上海", 910), ("北京", 911), ("深圳", 94), ("重庆", 904), ("广州", 95)
    
]

# 爬取时间范围（格式：YYYY-MM-DD）
START_DATE = '2026-03-01'
END_DATE = '2026-03-15'

# 进度文件（用于断点续爬，程序会自动创建）
PROGRESS_FILE = 'crawl_progress.json'
# =========================================================

# ---------- 以下代码通常不需要修改 ----------

def load_progress():
    """加载已完成的爬取进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed_cities": []}

def save_progress(completed_cities):
    """保存当前进度"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"completed_cities": completed_cities}, f, ensure_ascii=False, indent=2)

def random_sleep(mu, sigma, min_sleep=1):
    """
    正态分布随机延时
    
    为什么用正态分布？
    - 固定延时容易被百度识别为爬虫
    - 正态分布更接近真实用户的行为模式
    """
    sleep_time = random.gauss(mu, sigma)
    sleep_time = max(min_sleep, sleep_time)
    time.sleep(sleep_time)

def crawl_single_city(city_name, city_code):
    """爬取单个城市的所有关键词数据"""
    print(f"\n{'=' * 50}")
    print(f"正在爬取: {city_name} (代码: {city_code})")
    print(f"{'=' * 50}")
    
    all_data = []
    
    # 批量关键词请求（每批3个，最多支持5个）
    batch_size = 3
    keyword_batches = [KEYWORDS[i:i+batch_size] for i in range(0, len(KEYWORDS), batch_size)]
    total_batch = len(keyword_batches)
    print(f"关键词拆分 {total_batch} 个批次")

    for batch_num, keywords_batch in enumerate(keyword_batches, 1):
        print(f"\n[{batch_num}/{total_batch}] 关键词: {keywords_batch}")
        
        retry_count = 0
        max_retry = 3
        success = False
        current_cookie = random.choice(COOKIE_LIST)
        
        while retry_count < max_retry and not success:
            try:
                for index in get_search_index(
                    keywords_list=[keywords_batch],
                    start_date=START_DATE,
                    end_date=END_DATE,
                    cookies=current_cookie,
                    area=city_code
                ):
                    for kw in index['keyword']:
                        all_data.append({
                            'date': index['date'],
                            'keyword': kw,
                            'city': city_name,
                            'type': index['type'],
                            'index': index['index']
                        })
                success = True
                print(f"  ✅ 成功")
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                print(f"  ❌ 第{retry_count}次失败: {error_msg}")
                
                if "REQUEST_LIMITED" in error_msg or "验证码" in error_msg:
                    wait_time = 10 * (2 ** (retry_count - 1))
                    print(f"  限流等待 {wait_time} 秒...")
                    current_cookie = random.choice(COOKIE_LIST)
                    time.sleep(wait_time)
                else:
                    time.sleep(5 * retry_count)
        
        if batch_num < total_batch:
            random_sleep(mu=3, sigma=1, min_sleep=1)
    
    # 保存CSV
    output_file = f"{city_name}_baidu_index.csv"
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'keyword', 'city', 'type', 'index'])
        writer.writeheader()
        writer.writerows(all_data)
    
    print(f"\n✅ {city_name} 完成! 共 {len(all_data)} 条数据 → {output_file}")
    return True

def main():
    print("=" * 50)
    print("百度指数批量爬取工具")
    print(f"关键词: {len(KEYWORDS)} 个 | 城市: {len(CITY_LIST)} 个")
    print("=" * 50)
    
    progress = load_progress()
    completed_cities = progress["completed_cities"]
    print(f"已完成: {len(completed_cities)} 个城市")
    
    todo_cities = [city for city in CITY_LIST if city[0] not in completed_cities]
    print(f"待爬取: {len(todo_cities)} 个城市")
    
    if not todo_cities:
        print("\n🎉 全部完成!")
        return
    
    for idx, (city_name, city_code) in enumerate(todo_cities, 1):
        print(f"\n【{idx}/{len(todo_cities)}】")
        try:
            crawl_success = crawl_single_city(city_name, city_code)
            if crawl_success:
                completed_cities.append(city_name)
                save_progress(completed_cities)
        except Exception as e:
            print(f"❌ {city_name} 异常: {e}")
            continue
        
        if idx < len(todo_cities):
            random_sleep(mu=12, sigma=3, min_sleep=5)
    
    print("\n" + "=" * 50)
    print("🎉 全部任务执行完毕!")
    print("=" * 50)

if __name__ == "__main__":
    main()
