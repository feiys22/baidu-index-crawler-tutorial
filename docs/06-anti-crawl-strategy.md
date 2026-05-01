# 反爬原理与应对策略

> 这一篇是整个教程的精华部分！理解了百度是怎么发现爬虫的，你才能真正有效地反反爬。

---

## 一、百度是怎么发现爬虫的？

### 1. 请求频率检测（最常见）

百度服务器会记录每个 IP（或每个账号）的请求频率。

**正常用户的行为模式**：
- 搜索一个关键词，看结果
- 思考几分钟
- 再搜索下一个
- 间隔时间不规律，但通常较长

**爬虫的行为模式**：
- 每秒请求 10 次
- 请求间隔完全相同（比如正好 1 秒）
- 连续不断，24 小时不休息

**结论：请求频率和间隔规律是百度识别爬虫的最主要手段。**

### 2. 请求头特征检测

浏览器发出的每个请求都带有一堆"请求头"，告诉服务器"我是谁"。

**正常浏览器的请求头包含**：
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Referer: https://index.baidu.com/v2/index.html
```

**Python requests 默认的请求头**：
```
User-Agent: python-requests/2.28.0
```

Python requests 的 User-Agent 一眼就能被识别为非浏览器。

### 3. TLS / SSL 指纹检测

当你用浏览器访问百度时，浏览器和百度服务器之间的 TLS（加密）握手会携带浏览器的"指纹"信息。

不同浏览器（Chrome、Firefox、Safari）的 TLS 指纹是不同的。

Python requests 库的 TLS 指纹是固定的，百度可以轻易识别"这是 Python 发起的请求"。

### 4. IP 行为检测

即使你伪装得很好，如果同一个 IP 长期、大量请求，百度也会标记这个 IP。

特别是在同一 IP 请求了"太多不同关键词"的情况下——正常用户不会一天查 1000 个关键词。

### 5. 账号维度检测

百度也会按账号维度统计。如果同一个账号（BDUSS）请求量异常大，即使换了 IP 也逃不过。

---

## 二、核心应对策略

### 策略一：降低请求频率（最关键！）

**核心原则：请求间隔要随机，不要规律。**

❌ 错误做法：
```python
for city in cities:
    crawl(city)
    time.sleep(3)  # 固定 3 秒——容易被识别
```

✅ 正确做法：
```python
import random
import time

def random_sleep(mu=3, sigma=1, min_sleep=1):
    """正态分布延时：均值 3 秒，标准差 1 秒"""
    sleep_time = random.gauss(mu, sigma)
    sleep_time = max(min_sleep, sleep_time)
    time.sleep(sleep_time)

for city in cities:
    crawl(city)
    random_sleep(mu=3, sigma=1)  # 多数 2-4 秒，偶尔更长
```

### 策略二：多 Cookie 轮询

**核心原则：不要用一个 Cookie 打天下。**

单账号的请求量太大会触发限流。准备多个百度账号的 Cookie，轮换使用。

```python
COOKIE_LIST = [
    '''BDUSS=账号1的完整Cookie; ...''',
    '''BDUSS=账号2的完整Cookie; ...''',
    '''BDUSS=账号3的完整Cookie; ...''',
]

# 每次请求随机选一个
current_cookie = random.choice(COOKIE_LIST)
```

### 策略三：指数退避重试

遇到限流错误时，不要立刻重试。

❌ 错误做法：
```python
while True:
    try:
        crawl()
        break
    except REQUEST_LIMITED:
        time.sleep(1)  # 等 1 秒就重试——还是会被限流
```

✅ 正确做法：
```python
for retry in range(3):
    try:
        crawl()
        break
    except REQUEST_LIMITED:
        wait = 10 * (2 ** retry)  # 10 → 20 → 40 秒
        time.sleep(wait)
```

### 策略四：使用真实浏览器 UA

每次请求带上真实的浏览器 User-Agent。

```python
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
]

headers = {
    'User-Agent': random.choice(USER_AGENTS),
    'Referer': 'https://index.baidu.com/v2/index.html',
}
```

### 策略五：TLS 指纹伪装（进阶）

Python requests 的 TLS 指纹是固定的，很容易被识别。

可以用 `curl_cffi` 库来模拟真实浏览器的 TLS 指纹：

```python
# pip install curl_cffi
from curl_cffi import requests

# 模拟 Chrome 浏览器的 TLS 指纹
response = requests.get(
    url,
    cookies=cookies,
    impersonate='chrome110'  # 模拟 Chrome 110
)
```

### 策略六：代理 IP 池（进阶）

同一 IP 请求太多会被封。可以用代理 IP 池，让每个请求来自不同的 IP。

```python
# 代理格式
proxies = [
    'http://user:pass@ip:port',
    'http://user:pass@ip:port',
]

# 每次请求随机选一个代理
proxy = random.choice(proxies)
response = requests.get(url, proxies={'http': proxy, 'https': proxy})
```

注意：不要用免费代理——那些 IP 早就被百度拉黑了。

---

## 三、反爬等级对照表

| 等级 | 措施 | 复杂度 | 适用场景 |
|------|------|--------|----------|
| **青铜** | 固定延时 3-5 秒 | ⭐ | 偶尔爬几个关键词 |
| **白银** | 正态分布延时 + 多 Cookie 轮询 | ⭐⭐ | 爬取 10-50 个城市 |
| **黄金** | + 指数退避重试 + 真实 UA | ⭐⭐⭐ | 爬取 50-200 个城市 |
| **钻石** | + TLS 指纹伪装 + 代理 IP | ⭐⭐⭐⭐ | 大规模长期爬取 |
| **王者** | + 验证码自动识别 + 分布式架构 | ⭐⭐⭐⭐⭐ | 企业级采集 |

---

## 四、不同场景下的配置建议

### 场景 1：学生做课程作业，爬取 10 个城市

```
延时策略：每批次间隔 3-5 秒
Cookie：1 个就够
预计耗时：10-20 分钟
风险：极低
```

### 场景 2：毕业论文数据，爬取 144 个城市

```
延时策略：正态分布（均值3秒，标准差1秒）+ 城市间隔（均值12秒）
Cookie：至少 3 个
预计耗时：14-16 小时（建议通宵跑）
风险：中等（可能触发限流，需要重试）
```

### 场景 3：研究报告，批量长期监控

```
延时策略：严格控制频率 + 时间窗口（凌晨风控松）
Cookie：5+ 个
代理：国内短效代理
预计耗时：可长期稳定运行
风险：需要维护成本
```

---

## 五、常见被封原因及应对

| 被封表现 | 原因 | 应对方法 |
|----------|------|----------|
| `status: 10018` 一直报 | Cookie 过期或 IP 被封 | 换 Cookie / 换 IP |
| `REQUEST_LIMITED` 频繁 | 请求太密集 | 加长延时，换 Cookie |
| 第一次请求成功，第二次立刻失败 | 单 IP 请求过载 | 换代理 IP |
| 白天请求失败，凌晨成功 | 工作时段风控严 | 改到凌晨 0-6 点跑 |
| 账号突然登出 | 异常访问触发百度安全机制 | 停用该账号 24 小时 |

---

## 六、一句话总结反爬核心

> **让你的爬虫表现得像个正常人——请求间隔随机、多账号轮换、被拒后等一等再试。**

---

[→ 下一步：全国城市代码对照表](07-city-codes.md)
