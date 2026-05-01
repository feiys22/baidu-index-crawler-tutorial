# 完整代码逐段解析

> 零基础也能看懂！这段代码是爬虫的核心，建议认真阅读理解每一段的作用。

---

## 一、完整代码全文

```python
from qdata.baidu_index import get_search_index
import csv
import time
import random
import json
import os

# ====================== 核心配置（按你的需求修改） ======================
# 多Cookie轮询，至少填2个，越多越稳，格式：三引号包裹的完整Cookie字符串
COOKIE_LIST = [
    # 请在这里填入你的多个百度账号Cookie，一行一个
    '''ppfuid=第一段; XFI=第二段; ...''',   # ← 替换成你的真实Cookie
    '''ppfuid=另一个; XFI=另一个; ...''',
]

# 100%保留你的原始关键词列表
KEYWORDS = [
    '十五五规划', '全面深化改革', '高质量发展', '经济增长', '城市群',
    '扩大内需', '市场', '民营经济', '内卷',
    '改善民生', '新质生产力', '人工智能', '就业',
    '新兴产业', '智能经济', '脑机接口', '显卡', '低空经济',
    '科技', '资本市场', '新型工业化', '再贷款',
    '农民养老金', '未来能源', '住房', '出生率', '智能体',
    '人力资源', '健康中国', '收入', '生态环境',
    '消费', '正风反腐', '全面依法治国', '美丽中国',
    '种业', '智慧农业', '机器人', '贴息', '智能系统',
    '高额彩礼', '形式主义', '金融科技', '绿色金融',
    '普惠金融', '养老金融', '数字金融', '货币政策', '金融强国',
    '半导体', '金融安全', '智能交通'
]

# 去重后的完整城市列表（城市名, 城市代码）
CITY_LIST = [
    ("上海", 910), ("北京", 911), ("深圳", 94), ("重庆", 904), ("广州", 95),
    ("苏州", 126), ("成都", 97), ("武汉", 28), ("杭州", 138), ("南京", 125),
    ("天津", 923), ("宁波", 289), ("青岛", 77), ("无锡", 127), ("长沙", 43),
    ("郑州", 168), ("佛山", 196), ("合肥", 189), ("济南", 1), ("南通", 163),
    ("西安", 165), ("东莞", 133), ("泉州", 55), ("常州", 162), ("烟台", 78),
    ("唐山", 261), ("温州", 149), ("大连", 29), ("福州", 50), ("徐州", 161),
    ("厦门", 54), ("扬州", 158), ("绍兴", 303), ("盐城", 160), ("泰州", 159),
    ("潍坊", 80), ("石家庄", 141), ("长春", 154), ("南昌", 5), ("嘉兴", 304),
    ("台州", 287), ("洛阳", 378), ("哈尔滨", 152), ("临沂", 79), ("金华", 135),
    ("襄阳", 32), ("宜昌", 35), ("惠州", 199), ("镇江", 169), ("太原", 231),
    ("沧州", 148), ("榆林", 278), ("济宁", 352), ("淄博", 81), ("昆明", 117),
    ("保定", 259), ("邯郸", 292), ("柳州", 89), ("威海", 88), ("包头", 13),
    ("菏泽", 84), ("淮安", 157), ("岳阳", 44), ("茂名", 203), ("九江", 6),
    ("赣州", 10), ("常德", 68), ("遵义", 59), ("绵阳", 98), ("湖州", 305),
    ("湛江", 197), ("上饶", 9), ("宿迁", 172), ("株洲", 46), ("滁州", 182),
    ("东营", 82), ("廊坊", 147), ("衡阳", 45), ("南阳", 262), ("漳州", 56),
    ("邢台", 293), ("中山", 207), ("聊城", 83), ("滨州", 76), ("宜春", 256),
    ("黄冈", 33), ("德州", 86), ("眉山", 291),
    ("宜宾", 96), ("宿州", 179), ("鞍山", 215), ("南充", 104), ("泰安", 353),
    ("曲靖", 339), ("孝感", 41), ("吉林", 270), ("荆门", 34), ("宁德", 87),
    ("邵阳", 405), ("龙岩", 53), ("赤峰", 21), ("乐山", 107), ("怀化", 67),
    ("永州", 269), ("丽江", 342), ("黄山", 174), ("郴州", 49), ("荆州", 31),
    ("大同", 227), ("延安", 401), ("运城", 233), ("晋中", 230), ("咸阳", 277),
    ("鄂州", 39), ("萍乡", 136), ("抚州", 8), ("新余", 246), ("六盘水", 4),
    ("百色", 131), ("贵港", 93), ("防城港", 130), ("钦州", 129), ("河池", 119),
    ("来宾", 506), ("贺州", 92), ("崇左", 665), ("广元", 99), ("达州", 113),
    ("巴中", 101), ("雅安", 114), ("攀枝花", 112), ("自贡", 111), ("天水", 308),
    ("武威", 283),
    ("鄂尔多斯", 14), ("呼和浩特", 20), ("桂林", 91), ("兰州", 166),
    ("银川", 140), ("西宁", 139), ("乌鲁木齐", 467), ("玉溪", 123),
    ("克拉玛依", 317), ("拉萨", 466)
]

# 爬取时间范围
START_DATE = '2026-03-01'
END_DATE = '2026-03-15'

# 进度文件路径（用于断点续爬）
PROGRESS_FILE = 'crawl_progress.json'
# ======================================================================

# ------------------- 以下代码通常不需要修改 -------------------

def load_progress():
    """
    加载已保存的爬取进度。
    
    为什么需要这个？
    如果爬虫中途被中断（比如断电、程序崩溃），进度文件可以让你从
    断点继续，而不是从头开始爬取所有城市。
    
    进度文件格式：
    {"completed_cities": ["上海", "北京", "深圳", ...]}
    """
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed_cities": []}

def save_progress(completed_cities):
    """
    保存当前已完成的城市列表到进度文件。
    
    每次成功爬完一个城市，就把这个城市记录下来。
    这样程序中断后重启，能从断点继续。
    """
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"completed_cities": completed_cities}, f, ensure_ascii=False, indent=2)

def random_sleep(mu, sigma, min_sleep=1):
    """
    正态分布随机延时。
    
    为什么用正态分布而不是固定延时？
    
    固定延时的缺点：
    爬虫每 3 秒请求一次，百度服务器很容易发现"这个请求间隔太规律了"
    发现规律后就能判断这是机器而不是真人，所以容易被封。
    
    正态分布延时的优点：
    人类操作浏览器时，间隔本来就是随机分布的。
    均值 3 秒、标准差 1 秒的正态分布，更接近真实人类行为。
    
    参数：
    - mu: 均值（秒）
    - sigma: 标准差（秒）
    - min_sleep: 最小延时（秒），防止出现极端短的间隔
    """
    sleep_time = random.gauss(mu, sigma)
    sleep_time = max(min_sleep, sleep_time)  # 确保不低于最小值
    time.sleep(sleep_time)

def crawl_single_city(city_name, city_code):
    """
    爬取单个城市的全部关键词数据。
    
    参数：
    - city_name: 城市名称，用于文件名和输出
    - city_code: 百度指数的城市代码，用于API请求
    
    返回：
    - True: 爬取成功
    - False: 爬取失败
    """
    print(f"\n{'=' * 50}")
    print(f"正在爬取: {city_name} (代码: {city_code})")
    print(f"{'=' * 50}")
    
    all_data = []
    
    # ----------- 关键优化：批量关键词请求 -----------
    # 之前错误做法：逐个关键词请求（52个关键词 = 52次请求）
    # 正确做法：每批3个关键词（52个关键词 = 18次请求）
    # 请求量减少 65%，触发限流概率大幅下降！
    batch_size = 3
    keyword_batches = [KEYWORDS[i:i+batch_size] for i in range(0, len(KEYWORDS), batch_size)]
    total_batch = len(keyword_batches)
    print(f"关键词拆分 {total_batch} 个批次，单批次最多{batch_size}个关键词")

    for batch_num, keywords_batch in enumerate(keyword_batches, 1):
        print(f"\n[{batch_num}/{total_batch}] 正在爬取: {keywords_batch}")
        
        # ----------- 重试机制 -----------
        # 为什么要重试？
        # 百度偶尔会返回临时错误（网络波动、服务器抖动等）
        # 重试机制让程序在遇到临时错误时自动重试，而不是直接放弃
        retry_count = 0
        max_retry = 3
        success = False
        
        # 随机抽取一个 Cookie（轮询策略）
        # 为什么随机而不顺序？
        # 如果按顺序用 Cookie，第一个用完才换第二个，
        # 在大规模爬取时同一个 Cookie 容易在短时间内请求过多，触发限流
        current_cookie = random.choice(COOKIE_LIST)
        
        while retry_count < max_retry and not success:
            try:
                # ----------- 实际调用 qdata 的地方 -----------
                # 这是真正向百度服务器发请求的地方
                for index in get_search_index(
                    keywords_list=[keywords_batch],  # 注意：这里是列表的列表！
                    start_date=START_DATE,
                    end_date=END_DATE,
                    cookies=current_cookie,
                    area=city_code
                ):
                    # index 的结构：{'date': 'xxx', 'keyword': 'xxx', 'type': 'xxx', 'index': 12345}
                    for kw in index['keyword']:
                        all_data.append({
                            'date': index['date'],
                            'keyword': kw,
                            'city': city_name,
                            'type': index['type'],
                            'index': index['index']
                        })
                success = True
                print(f"  爬取成功")
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                print(f"  第{retry_count}次失败: {error_msg}")
                
                # ----------- 错误类型区分处理 -----------
                if "REQUEST_LIMITED" in error_msg or "验证码" in error_msg:
                    # 限流/验证码错误：指数退避 + 更换Cookie
                    # 为什么要指数退避？
                    # 如果立刻重试，很可能被继续限流
                    # 等待时间翻倍增长：10秒 → 20秒 → 40秒
                    wait_time = 10 * (2 ** (retry_count - 1))
                    print(f"  触发限流，等待{wait_time}秒后更换Cookie重试...")
                    current_cookie = random.choice(COOKIE_LIST)  # 换一个Cookie试试
                    time.sleep(wait_time)
                else:
                    # 普通错误：线性等待（5秒 → 10秒 → 15秒）
                    time.sleep(5 * retry_count)
        
        # ----------- 批次间延时 -----------
        # 为什么要延时？
        # 即使请求成功了，也不能马上发下一个请求
        # 正常用户不会在 0.1 秒内连续查询，两个请求之间需要间隔
        if batch_num < total_batch:
            print(f"  批次间等待中...")
            random_sleep(mu=3, sigma=1, min_sleep=1)
    
    # ----------- 保存CSV -----------
    # 每个城市的数据保存为一个独立的CSV文件
    # 为什么要独立文件？
    # - 如果全部存一个文件，中途出错数据会丢失
    # - 独立文件可以单独验证每个城市的数据质量
    output_file = f"{city_name}_baidu_index.csv"
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'keyword', 'city', 'type', 'index'])
        writer.writeheader()
        writer.writerows(all_data)
    
    print(f"\n✅ {city_name} 完成! 共 {len(all_data)} 条数据")
    print(f"保存到: {output_file}")
    return True

def main():
    """
    主函数：遍历所有城市，依次爬取
    """
    print("=" * 50)
    print("百度指数批量爬取工具")
    print(f"关键词数量: {len(KEYWORDS)} | 城市总数: {len(CITY_LIST)}")
    print("=" * 50)
    
    # 加载断点进度
    progress = load_progress()
    completed_cities = progress["completed_cities"]
    print(f"已完成城市: {len(completed_cities)} 个")
    
    # 过滤掉已完成的城市
    todo_cities = [city for city in CITY_LIST if city[0] not in completed_cities]
    print(f"待爬取城市: {len(todo_cities)} 个")
    
    if not todo_cities:
        print("\n🎉 全部完成！")
        return
    
    for idx, (city_name, city_code) in enumerate(todo_cities, 1):
        print(f"\n【进度 {idx}/{len(todo_cities)}】")
        
        try:
            crawl_success = crawl_single_city(city_name, city_code)
            if crawl_success:
                completed_cities.append(city_name)
                save_progress(completed_cities)
        except Exception as e:
            print(f"❌ {city_name} 异常跳过: {e}")
            continue
        
        # 城市切换延时
        if idx < len(todo_cities):
            print(f"\n⏳ 城市切换等待中...")
            random_sleep(mu=12, sigma=3, min_sleep=5)
    
    print("\n" + "=" * 50)
    print("🎉 所有任务执行完毕")
    print("=" * 50)

if __name__ == "__main__":
    main()
```

---

## 二、代码核心逻辑图

```
main()
  │
  ├── load_progress()          ← 读取已完成的进度
  │
  ├── 遍历 todo_cities         ← 跳过已完成的城市
  │
  └── crawl_single_city(city_name, city_code)
        │
        ├── 拆分关键词为批次（每批3个）
        │
        ├── 遍历每个批次
        │     │
        │     ├── 随机选一个 Cookie
        │     │
        │     ├── 调用 qdata.get_search_index()
        │     │     │
        │     │     ├── 成功 → 写入 all_data
        │     │     │
        │     │     └── 失败 → 重试（最多3次）
        │     │           │
        │     │           ├── REQUEST_LIMITED → 等10/20/40秒 + 换Cookie
        │     │           └── 其他错误 → 等5/10/15秒
        │     │
        │     └── 批次间延时（正态分布，均值3秒）
        │
        └── 保存城市CSV文件 + 更新进度
```

---

## 三、为什么代码这样设计？

### 1. 为什么要分批次爬取？

百度指数接口每次最多接受 **5 个关键词**，但实际使用中发现每批 **3 个**最稳定。

### 2. 为什么要轮换 Cookie？

百度对每个账号的请求频率有上限。单账号连续请求容易触发限流。多账号轮换可以分散请求量。

### 3. 为什么要正态分布延时？

人类的操作间隔不是固定 3 秒，而是服从正态分布（多数在 2-5 秒之间，偶尔长偶尔短）。正态分布延时更接近真实用户行为。

### 4. 为什么要断点续爬？

爬取 144 个城市 × 52 个关键词，如果中途出错从头开始非常浪费时间。断点续爬让你随时可以中断、继续。

### 5. 为什么要每个城市单独保存 CSV？

如果所有数据存一个文件，中途崩溃会丢失所有数据。独立文件可以保证每个城市的数据独立完整。

---

[→ 下一步：反爬原理与应对策略](06-anti-crawl-strategy.md)
