# 常见错误与解决方案

> 遇到问题先来这里查，通常能找到答案。

---

## 一、代码报错类

### 报错 1：`SyntaxError: invalid syntax`

**错误信息**：
```
SyntaxError: invalid syntax
```

**最常见原因**：三引号没写完整。

检查：
- [ ] 是三个单引号 `'''` 还是三个双引号 `"""`？开头结尾要一致
- [ ] 有没有少写了结尾的 `'''`？
- [ ] Cookie 里如果包含三引号符号，也会报错

**示例**：
```python
# ❌ 错误：结尾少了一个引号
COOKIE = '''abc123

# ✅ 正确：开头三个，结尾三个
COOKIE = '''abc123'''
```

---

### 报错 2：`ModuleNotFoundError: No module named 'qdata'`

**错误信息**：
```
ModuleNotFoundError: No module named 'qdata'
```

**原因**：qdata 没有安装。

**解决**：
```bash
pip install qdata
```

如果安装失败，试试：
```bash
pip install qdata-baidu-index
```

---

### 报错 3：`IndentationError: unexpected indent`

**原因**：代码缩进不一致。

Python 对缩进非常敏感，混用 Tab 和空格会报错。

**解决**：
- 在 VSCode 里，按 Ctrl+Shift+P → 输入 "Convert Indentation to Spaces"
- 确保所有代码都用**4个空格**缩进

---

## 二、百度 API 报错类

### 报错 4：`status: 10018，异常的访问行为`

**原因**：Cookie 无效、已过期，或者当前 IP 被封。

**排查步骤**：
1. 先在浏览器里打开 https://index.baidu.com，确认能正常登录看到数据
2. 如果浏览器里都看不到数据 → Cookie 对应的账号可能已过期登录
3. 如果浏览器里正常 → 重新从浏览器复制 Cookie

**解决**：
```bash
# 快速验证 Cookie 是否有效（PowerShell）
curl "https://index.baidu.com/api/SearchApi/index?word=%5B%7B%22name%22%3A%22%E6%B5%8B%E8%AF%95%22%2C%22wordType%22%3A1%7D%5D&area=0&days=7" `
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" `
  -H "Cookie: 你的Cookie"
```

如果返回 `"status":0` → Cookie 有效
如果返回 `"status":10018` → Cookie 无效

---

### 报错 5：`status: 10018，REQUEST_LIMITED`

**原因**：请求太频繁，触发了百度的频率限制。

**解决**：
1. 等待 10-20 秒后重试
2. 换一个 Cookie
3. 增加代码里的延时时间

**代码里增加延时**：
```python
# 临时解决方案：在出错后增加延时
time.sleep(30)  # 等 30 秒再继续
```

---

### 报错 6：`Empty reply from server`

**原因**：
1. 网络连接问题
2. 目标服务器拒绝了连接
3. 防火墙或代理问题

**解决**：
```python
# 在代码里加超时设置
import requests
requests.get(url, timeout=30)  # 30 秒超时
```

---

### 报错 7：返回数据为空 `[]`

**现象**：API 调用没有报错，但返回空列表，没有任何数据。

**原因**：
1. 关键词在百度指数里没有数据
2. 关键词在指定时间段内没有数据
3. 城市代码错误

**排查**：
```python
# 先单独测试一个关键词
for index in get_search_index(
    keywords_list=[['人工智能']],  # 先用简单英文或数字测试
    start_date='2026-03-01',
    end_date='2026-03-02',
    cookies='你的Cookie',
    area=0  # 先用全国（0）测试
):
    print(index)
```

---

## 三、运行结果异常类

### 问题 8：数据量比预期少

**现象**：爬完了，但数据行数很少，某个城市/关键词数据缺失。

**原因**：
1. 该城市/关键词在百度指数里本来就没有数据
2. 触发了限流，部分请求失败但被静默跳过
3. 时间段设置不对

**检查方法**：
```python
# 打印每个请求的响应
for index in get_search_index(...):
    print(f"关键词: {index['keyword']}, 日期: {index['date']}, 数据: {index['index']}")
```

---

### 问题 9：程序运行很慢

**原因**：延时设置太长。

**解决**：根据你的场景调整延时参数。

| 场景 | 建议延时 |
|------|----------|
| 测试/调试 | 1-2 秒 |
| 小规模（<10 城市） | 3-5 秒 |
| 中等规模（10-50 城市） | 5-10 秒 |
| 大规模（50+ 城市） | 10-15 秒 |

---

### 问题 10：程序中途崩溃，数据丢失

**原因**：没有断点续爬机制，程序崩溃后需要从头开始。

**解决**：确保代码里有 `save_progress()` 和 `load_progress()` 功能，每次成功爬完一个城市就保存进度。代码里已经包含了这个功能，不要删除它。

---

## 四、环境问题类

### 问题 11：Windows 上运行 Python 报错（编码问题）

**错误信息**：
```
UnicodeEncodeError: 'gbk' codec can't encode character
```

**原因**：Windows 终端默认编码是 GBK，而我们的数据是 UTF-8 编码的中文。

**解决**：在代码开头加这一行：
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

或者在 Windows 终端运行前设置编码：
```cmd
chcp 65001
python crawl_baidu_index.py
```

---

### 问题 12：VSCode 里运行 Python 没反应

**排查步骤**：
1. 确认打开的是正确的 `.py` 文件
2. 确认 Python 解释器是系统默认的那个（右下角）
3. 在终端里直接运行：`python 文件名.py`

---

## 五、Q&A 速查

| 问题 | 答案 |
|------|------|
| Cookie 从哪获取？ | 见 [Cookie 获取指南](02-cookie-guide.md) |
| 为什么用三引号？ | 见 [三引号详解](03-cookie-format-explained.md) |
| Cookie 多久过期？ | 通常 7-30 天，过期了要重新获取 |
| 能爬多少数据？ | 取决于 Cookie 和 IP，通常每天上千次请求没问题 |
| 能爬历史数据吗？ | 可以，只要设置 start_date 和 end_date |
| 被封了怎么办？ | 换 Cookie、换 IP、降低频率 |
| 能爬多久的数据？ | 一般支持查询几年内的数据 |
| 城市代码从哪来？ | 见 [城市代码表](07-city-codes.md) |
| 能爬移动端数据吗？ | 可以，qdata 支持 `type` 参数指定 |
| 数据保存在哪？ | 每个城市一个 CSV 文件，在脚本运行目录下 |

---

## 六、错误信息速查表

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `SyntaxError` | 三引号没写对 | 检查 `'''` 开头结尾 |
| `ModuleNotFoundError` | qdata 没装 | `pip install qdata` |
| `IndentationError` | 缩进错误 | 用 4 空格缩进 |
| `status: 10018` | Cookie无效/IP被封 | 换 Cookie |
| `REQUEST_LIMITED` | 请求太频繁 | 加延时，换 Cookie |
| `Empty reply` | 网络问题 | 检查网络 |
| `UnicodeEncodeError` | Windows 编码 | `chcp 65001` |

---

如果以上都没有解决你的问题，可以在 GitHub Issues 里提问，或者检查原始报错信息的完整内容（包括英文部分）来定位问题。
