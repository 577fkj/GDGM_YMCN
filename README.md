# 适用于 GDGM 的一些脚本

- jxzg: 自动填写 `学生个人发展规划书`
- [优慕课脚本](https://greasyfork.org/zh-CN/scripts/496851-%E5%B9%BF%E4%B8%9C%E5%B7%A5%E8%B4%B8%E4%BC%98%E6%85%95%E8%AF%BE%E8%84%9A%E6%9C%AC)
- [登录保存账号密码](https://greasyfork.org/zh-CN/scripts/483848-%E5%B9%BF%E4%B8%9C%E5%B7%A5%E8%B4%B8%E7%99%BB%E5%BD%95%E4%BF%9D%E5%AD%98%E8%B4%A6%E5%8F%B7%E5%AF%86%E7%A0%81)

## 学生个人发展规划书

填写配置文件 `config.json`

```yaml
# 统一登录
gdgm:
  user: "学号"
  password: "密码"
```

需要先自行填写 `目标标准/规划管理` 然后运行脚本。

```bash
pip install -r requirements.txt
python jxzg.py
```

# 幽默⏰
