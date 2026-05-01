# qdata 百度指数库详解

## 一、qdata 是什么？

**qdata** 是一个封装了百度指数 API 请求的 Python 库，它的作用是：

> 不用你自己去逆向百度指数的加密逻辑，直接调用现成接口，传入 Cookie 就能拿到数据。

### 官方定义

qdata（通常叫 `qdata.baidu_index`）是 GitHub 上一个开源项目，专门用于爬取百度指数数据。

**GitHub 地址**：https://github.com/qiantongtech/qData

---

## 二、为什么用 qdata 而不是直接 requests？

### 方案 A：直接用 requests 请求

**缺点**（这是为什么我们用 qdata）：

1. 百度指数接口有 **AES 加密参数**，你需要逆向前端的 JS 加密逻辑
2. 接口返回的数据也是**加密的**，需要用密钥解密
3. 加密算法可能随时更新，维护成本极高
4. 需要处理各种请求头、签名、时间戳参数

```python
# 如果你自己写 requests，会变成这样...（噩梦）
import requests
import hashlib
import json
from Crypto.Cipher import AES
import base64

# 需要逆向 JS 代码，理解加密流程
# 需要处理 10+ 个请求头参数
# 需要处理加密响应体的解密
# ...200 行代码起步
```

### 方案 B：用 qdata 库

```python
# 用 qdata，核心调用只需要 5 行
from qdata.baidu_index import get_search_index

for index in get_search_index(
    keywords_list=[['人工智能']],  # 关键词列表
    start_date='2026-03-01',
    end_date='2026-03-15',
    cookies='你的Cookie',
    area=911  # 城市代码，北京=911
):
    print(index)
```

---

## 三、安装 qdata

```bash
pip install qdata
```

如果提示找不到包，试试：

```bash
pip install qdata-baidu-index
# 或者
pip install git+https://github.com/xxx/qdata.git
```

---

## 四、qdata 的核心函数

### get_search_index（最常用）

批量获取关键词的搜索指数。

```python
from qdata.baidu_index import get_search_index

# 参数说明
for index in get_search_index(
    keywords_list=[['关键词1', '关键词2']],  # 列表的列表，支持批量（最多5个）
    start_date='2026-03-01',                   # 开始日期，格式 YYYY-MM-DD
    end_date='2026-03-15',                    # 结束日期
    cookies='BDUSS=xxx; ...',                 # 百度 Cookie（必须已登录）
    area=0                                     # 城市代码，0=全国
):
    # index 是一个字典，包含 date, keyword, type, index 字段
    print(index)
```

**返回值格式**：

```python
{
    'date': '2026-03-01',    # 日期
    'keyword': '人工智能',   # 关键词
    'type': 'all',           # 搜索类型（all=整体，pc=PC端，mobile=移动端）
    'index': 12847           # 搜索指数值
}
```

### keywords_index（按关键词获取）

一次性获取多个关键词的多个日期数据，返回结构和上面一样。

---

## 五、qdata 的参数详解

### keywords_list：关键词列表

```python
# 单个关键词
keywords_list=[['人工智能']]

# 多个关键词（最多 5 个，超出会被截断）
keywords_list=[['人工智能', '大数据', '云计算']]

# 如果关键词超过 5 个，需要分批次调用
keywords_list=[['关键词1', '关键词2', '关键词3', '关键词4', '关键词5']]
# 下一批
keywords_list=[['关键词6', '关键词7', '关键词8', '关键词9', '关键词10']]
```

### cookies：Cookie

```python
# 必须用三引号包裹（详见 03-cookie-format-explained.md）
cookies = '''BDUSS=xxx; BAIDUID=yyy; H_PS_PSSID=zzz; ...'''

# 建议用 Cookie 列表轮询（详见反爬策略文档）
```

### area：城市代码

```python
area=0        # 0 = 全国
area=911      # 911 = 北京
area=910      # 910 = 上海
area=94       # 94 = 深圳
area=95       # 95 = 广州
```

全国城市代码见 [城市代码对照表](07-city-codes.md)

---

## 六、qdata 的底层原理（了解即可）

qdata 之所以能工作，是因为它**预置了百度的加密逻辑**，包括：

1. **Cipher-Text 请求头**：百度 API 要求请求带上这个头部，是加密后的请求标识
2. **解密算法**：响应数据经过加密，qdata 内置了解密函数
3. **请求签名**：百度接口有 sign 参数，qdata 帮你算好了

这些加密逻辑本来是在百度前端 JS 代码里执行的，qdata 的作者提前把它逆向出来并用 Python 实现了。

---

## 七、qdata 的局限性

| 问题 | 说明 | 应对方法 |
|------|------|----------|
| **Cookie 会过期** | 大约 7~30 天失效 | 定期更新 Cookie |
| **会被限流** | 请求太频繁会触发 `REQUEST_LIMITED` | 加延时，换 Cookie |
| **IP 可能被封** | 同一 IP 请求太多次 | 使用代理 IP |
| **不是官方接口** | 百度随时可能改加密 | 关注 GitHub 更新 |

---

## 八、qdata 报错处理

### 错误1：status 10018

```python
# 错误信息
Exception: status: 10018，异常的访问行为

# 原因：Cookie 无效或过期
# 解决方法：重新从浏览器获取新的 Cookie
```

### 错误2：REQUEST_LIMITED

```python
# 错误信息
Exception: status: 10018，REQUEST_LIMITED

# 原因：请求太频繁，被临时限流
# 解决方法：等待 10~20 秒后重试，换一个 Cookie
```

### 错误3：Empty reply / Connection error

```python
# 原因：网络问题或 IP 被封
# 解决方法：检查网络，或者使用代理
```

---

## 九、qdata 的替代方案

如果 qdata 不可用，还可以考虑：

| 方案 | 难度 | 费用 | 说明 |
|------|------|------|------|
| **BaiduIndexHunter** | 中 | 免费 | 开源平台，功能更全但需要部署 |
| **Selenium 模拟浏览器** | 中 | 免费 | 慢，但稳定 |
| **商业 API 服务** | 低 | 付费 | 稳定性好，适合企业 |

---

## 十、快速验证 qdata 是否安装成功

```python
import qdata.baidu_index
print("✅ qdata 安装成功，版本:", qdata.__version__)
```

或者直接在命令行测试：

```bash
python -c "from qdata.baidu_index import get_search_index; print('OK')"
```

如果输出 `OK` 说明安装成功。

---

[→ 下一步：完整代码逐段解析](05-complete-code-explained.md)
