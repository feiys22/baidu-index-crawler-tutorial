# Cookie 获取完整指南

> 这是整个爬虫过程中最关键的一步。Cookie 就像你的"登录凭证"，没有它，百度不返回任何真实数据。

---

## 一、什么是 Cookie？为什么需要它？

当你用浏览器登录百度账号时，百度服务器会在你的浏览器里写入一小段数据，叫 **Cookie**。

这段数据包含你的身份信息，下次浏览器访问百度时，会自动带上这个 Cookie，百度就知道"哦，这是某个已登录用户在访问"，就会返回真实数据。

**我们的爬虫程序就是借用了这个原理：**
- 从你的浏览器里复制 Cookie
- 把这个 Cookie 交给爬虫程序
- 百度以为是有用户在操作，返回真实数据

---

## 二、Cookie 包含哪些关键字段？

从百度指数页面复制的 Cookie 里，真正起作用的主要是这几个：

| 字段名 | 作用 | 重要程度 |
|--------|------|----------|
| **BDUSS** | 百度账号登录凭证，最核心！ | ⭐⭐⭐⭐⭐ |
| **BDUSS_BFESS** | 同上，备用字段，也需要 | ⭐⭐⭐⭐⭐ |
| **BAIDUID** | 浏览器唯一标识 | ⭐⭐⭐⭐ |
| **H_PS_PSSID** | 百度统一会话ID | ⭐⭐⭐⭐ |
| **PTOKEN** | 百度登录态令牌 | ⭐⭐⭐ |

---

## 三、方法一：Chrome 开发者工具（最通用）

### 步骤 1：打开百度并登录

在 Chrome 浏览器里打开：https://index.baidu.com

确认右上角显示了你的百度账号头像和用户名（已登录状态）。

### 步骤 2：打开开发者工具

按 **F12**（或者右键 → 检查），Chrome 会弹出开发者工具。

### 步骤 3：切换到 Application 面板

点击开发者工具顶部的 **"Application"**（应用）标签。

### 步骤 4：找到 Cookie

在左侧菜单找到并展开 **"Cookies"** → 点击 **"https://index.baidu.com"**

### 步骤 5：复制 Cookie 值

找到以下关键字段，复制它们的 **Value**（值）：

- BDUSS
- BDUSS_BFESS
- BAIDUID（可选但建议有）
- H_PS_PSSID

**复制格式要特别注意！**

复制后的格式应该是这样的（中间用**分号分隔**）：

```
BDUSS=刚才复制的值; BDUSS_BFESS=刚才复制的值; BAIDUID=刚才复制的值; H_PS_PSSID=刚才复制的值
```

### 步骤 6：填入 Python 代码

在 Python 代码里这样写：

```python
COOKIE = '''BDUSS=刚才复制的值; BDUSS_BFESS=刚才复制的值; BAIDUID=刚才复制的值; H_PS_PSSID=刚才复制的值'''
```

**注意是三引号！不是普通引号！** 具体原因见 [三引号详解](03-cookie-format-explained.md)

---

## 四、方法二：Chrome Network 抓包

### 适用场景

方法一是"从存储中读取 Cookie"，但有时候 Application 面板里 Cookie 列表太长或显示不完整。

Network 抓包是"从请求中获取 Cookie"，更直接。

### 步骤

1. 在 Chrome 里打开 https://index.baidu.com（确保已登录）
2. 按 **F12** 打开开发者工具
3. 点击 **"Network"**（网络）标签
4. 在过滤框里输入 `index.baidu.com` 过滤请求
5. 刷新页面（按 Ctrl + F5 强制刷新）
6. 点击任意一个请求（通常 name 列会显示请求的 URL）
7. 在右侧面板找到 **"Request Headers"** → 找到 **"cookie:"** 字段
8. 完整复制 cookie 后面的整段字符串

### 为什么 Ctrl+F5 而不是 F5？

F5 会使用浏览器缓存，可能返回旧数据。Ctrl+F5 强制从服务器重新加载所有资源，确保抓到最新的 Cookie。

---

## 五、方法三：控制台命令（最简单！）

这是最偷懒但最有效的方法，适合不想折腾开发者工具的同学。

### 步骤

1. 在 Chrome 里打开 https://index.baidu.com（确保已登录）
2. 按 **F12** 打开开发者工具
3. 点击 **"Console"**（控制台）标签
4. 在下方的输入框里输入以下代码，按回车：

```javascript
document.cookie
```

5. 控制台会直接输出一段字符串，类似：

```
BDUSS=xxx; BAIDUID=yyy; H_PS_PSSID=zzz; ...
```

6. 完整复制这段字符串即可。

### 常见问题

**Q：输入 document.cookie 后什么都没返回？**

A：这说明你当前浏览的不是百度域名，或者还没登录。确保在 index.baidu.com 页面上执行这个命令。

**Q：返回的 Cookie 很少，只有几项？**

A：百度有些 Cookie 是 HttpOnly 的，JavaScript 无法读取。这不影响，只要关键字段 BDUSS 等能用就行。

---

## 六、方法四：从已登录的浏览器导出扩展

如果你不想每次手动复制，可以使用浏览器扩展来一键导出 Cookie。

### 推荐扩展：EditThisCookie

1. 在 Chrome 里安装 **EditThisCookie** 扩展
2. 打开 https://index.baidu.com
3. 点击地址栏右边的 EditThisCookie 图标
4. 它会显示所有 Cookie 列表
5. 点击右上角的"导出"按钮，导出格式选 **JSON** 或 **Netscape**（代码里用的是 Netscape 格式）
6. 把导出的内容复制到代码里

### 为什么 EditThisCookie 能读到 HttpOnly 的 Cookie？

因为它使用了浏览器的原生 API，不受 JavaScript 的 HttpOnly 限制。

---

## 七、方法五：命令行curl验证（进阶）

如果你对命令行比较熟悉，可以用这招快速验证 Cookie 是否有效。

### Windows PowerShell

```powershell
curl -Uri "https://index.baidu.com/api/SearchApi/index?word=%5B%7B%22name%22%3A%22%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%22%2C%22wordType%22%3A1%7D%5D&area=0&days=30" `
  -Headers @{
    "User-Agent"="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    "Cookie"="这里粘贴你复制的完整Cookie字符串"
  }
```

如果返回的数据里包含 `"status":0` 而不是 `"status":10018`，说明 Cookie 有效。

### Mac / Linux curl

```bash
curl "https://index.baidu.com/api/SearchApi/index?word=%5B%7B%22name%22%3A%22%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%22%2C%22wordType%22%3A1%7D%5D&area=0&days=30"   -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"   -H "Cookie: 这里粘贴你复制的完整Cookie字符串"
```

---

## 八、Cookie 的有效期与失效

**重要：百度 Cookie 会过期！**

- 一般有效期是 **7~30 天**（取决于账号活跃度和百度策略）
- 如果 Cookie 过期了，百度会返回 `"status":10018` 错误
- 解决方法是重新获取新的 Cookie

### 延长 Cookie 有效期的技巧

1. **保持百度账号活跃**：偶尔在浏览器里登录一下百度
2. **使用老账号**：注册时间长的账号 Cookie 有效期通常更长
3. **有百度指数会员的账号**：限流阈值更高，更适合爬虫

---

## 九、常见错误

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `status: 10018，异常的访问行为` | Cookie 无效或已过期 | 重新获取 Cookie |
| `status: 10018，REQUEST_LIMITED` | 请求太频繁被限流 | 加长延时或换 Cookie |
| `Empty reply` | 网络问题或 IP 被封 | 检查网络或换 IP |
| Cookie 里没有 BDUSS | 没有正确登录 | 确认登录后再复制 |

---

## 十、一行命令验证 Cookie 是否有效

在 Python 里快速验证：

```python
from qdata.baidu_index import get_search_index

try:
    for _ in get_search_index(
        keywords_list=[['测试']],
        start_date='2026-03-01',
        end_date='2026-03-02',
        cookies='你的Cookie字符串',
        area=0
    ):
        print("✅ Cookie 有效！")
        break
except Exception as e:
    print(f"❌ Cookie 无效: {e}")
```

---

[→ 下一步：三引号格式详解](03-cookie-format-explained.md)
