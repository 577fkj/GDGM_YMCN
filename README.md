# 适用于 GDGM 的一些脚本

- jxzg: 自动填写 `学生个人发展规划书`

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