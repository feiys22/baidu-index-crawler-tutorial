# 为什么 Python 里 Cookie 要用三引号包裹？

> 这是 Python 新手最常踩的坑！99% 的人在第一次写爬虫时都会在这里卡住。

---

## 一、问题演示

很多同学第一次写代码时，会这样写：

```python
# ❌ 错误写法（引号不匹配会导致各种奇怪报错）
COOKIE = "BDUSS=abc123; BAIDUID=def456"

# ❌ 另一种常见错误
COOKIE = 'BDUSS=abc123; BAIDUID=def456; H_PS_PSSID=ghi"789"jkl'
```

然后运行时报错：

```
SyntaxError: invalid syntax
```

或者 Cookie 里明明有分号（`;`）和引号（`"`），但程序就是解析不对。

---

## 二、为什么普通引号会出问题？

百度 Cookie 的值里**包含很多特殊字符**，比如：

| 特殊字符 | 示例 | 在 Cookie 里干什么 |
|----------|------|-------------------|
| 分号 `;` | `BDUSS=abc; BAIDUID=def` | **分隔不同的 Cookie 字段** |
| 等号 `=` | `BDUSS=abc123` | 分隔 Cookie 名和值 |
| 引号 `"` | `"value": "xxx"` | 有时值里包含引号 |
| 百分号 `%` | `H_PS_PSSID=abc%2Fdef` | URL 编码字符 |
| 加号 `+` | `ptoken=abc+def` | 有时会出现在值里 |

**当你用普通引号（`"` 或 `'`）包裹包含这些特殊字符的字符串时，Python 解析器可能会把它们当成字符串的结束符或特殊指令，导致解析错误。**

---

## 三、三引号是什么？

Python 的三引号（triple quotes）是另一种字符串字面量，用**三个单引号 `'''`** 或**三个双引号 `"""`** 包裹字符串。

```python
# 三单引号
cookie = '''BDUSS=abc123; BAIDUID=def456'''

# 三双引号
cookie = """BDUSS=abc123; BAIDUID=def456"""
```

### 三引号的特点：

1. **可以包含普通引号**：字符串里可以直接写 `"` 或 `'` 而不用转义
2. **可以换行**：多行字符串可以直接写
3. **所见即所得**：Cookie 里是什么，存进字符串就是什么

---

## 四、三引号 vs 普通引号实战对比

### 场景：Cookie 字符串里有单引号

```python
# 普通引号：报错！
name = 'It' + 's a beautiful day'   # ❌

# 三引号：完美
name = '''It's a beautiful day'''   # ✅
```

### 场景：Cookie 里有分号（实际最常见的情况）

```python
# 普通引号：能运行，但语义上不推荐
cookie = "BDUSS=abc; BAIDUID=def"

# 三引号：更规范，含义清晰
cookie = '''BDUSS=abc; BAIDUID=def'''
```

### 场景：Cookie 里有双引号

```python
# 普通引号：报错！
cookie = "BDUSS=abc"def"ghi"

# 三单引号：完美
cookie = '''BDUSS=abc"def"ghi'''
```

---

## 五、百度 Cookie 的实际情况

百度 Cookie 的值**通常比较长，而且经常包含 URL 编码字符**（百分号 `%`），以及各种特殊符号。

实际从浏览器复制的 Cookie 类似这样（这里只是示例，不是真实值）：

```
BDUSS=dGWXA0UEZ3OW5kVUpMdWFZfmot...; BAIDUID=6569AF53050B113C64E5B2D2161F4EF0:FG=1; H_PS_PSSID=63143_67603_67862_68166_68296...
```

注意里面有很多**百分号（`%`）**——这些是 URL 编码字符。如果用普通引号，在某些情况下 Python 可能会误解析 `%` 后的字符。

**所以，用三引号是最安全的选择。**

---

## 六、代码里的正确写法

```python
# ✅ 正确：用三单引号包裹，Cookie 里有什么字符都不怕
COOKIE_LIST = [
    '''BDUSS=第一段值; BAIDUID=第二段值; H_PS_PSSID=第三段值; ...''',
    '''BDUSS=另一个账号的值; BAIDUID=另一个值; H_PS_PSSID=另一个值; ...''',
]

# ✅ 或者用三双引号，效果完全一样
COOKIE_LIST = [
    """BDUSS=第一段值; BAIDUID=第二段值; H_PS_PSSID=第三段值; ...""",
]
```

---

## 七、延伸：Python 字符串引号规则

Python 里字符串可以用三种引号：

```python
# 1. 单引号
s1 = 'hello'

# 2. 双引号
s2 = "hello"

# 3. 三引号（单双都行）
s3 = '''hello'''
s4 = """hello"""
```

单引号和双引号功能完全相同，只是风格偏好问题。

**但三引号是唯一能安全包含其他两种引号的写法。**

---

## 八、如果你坚持不想用三引号怎么办？

如果你确定 Cookie 里没有单引号，也可以用普通引号，但要注意：

```python
# ✅ 安全的普通引号写法（确保 Cookie 里没有单引号）
COOKIE = "BDUSS=abc123; BAIDUID=def456"

# ✅ 转义引号（Python 不会把 \' 当作字符串结束符）
COOKIE = "BDUSS=abc\"123\"; BAIDUID=def456"

# ❌ 危险：分号本身没问题，但 Cookie 里经常有混合引号，容易出错
```

**结论：为了省心，直接用三引号。**

---

## 九、快速检查清单

写完代码后，对照检查一下：

- [ ] Cookie 用的是 `'''` 三引号还是 `'` 单引号？
- [ ] 三引号开头和结尾都是三个 `'''`？
- [ ] Cookie 里包含的特殊字符（`;` `"` `%` `+`）都原样保留了吗？
- [ ] Cookie 前后没有多余的空格？
- [ ] 如果有多个 Cookie，每个都是独立的 `'''...'''` 条目？

---

[→ 下一步：qdata 百度指数库详解](04-qdata-library.md)
