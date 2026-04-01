# 花店物品命名审查工具

将电商平台商品名称转换为标准命名格式的CLI工具。

## 功能特性

- 🏷️ **自动分类**: 支持23个一级大类自动匹配
- 🎨 **颜色标准化**: 藕粉、莫兰迪、碎冰蓝等50+颜色词映射
- 📏 **规格提取**: 自动识别尺寸、等级、数量、重量等规格信息
- 🛒 **多平台支持**: 1688/淘宝/拼多多/花伍APP
- 💡 **智能建议**: 提供单位建议和规格建议
- 📦 **零依赖**: 纯Python标准库，无需安装额外包

## 安装

### 方式1: 一键安装脚本 (推荐)

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/coreyleung-art/flower-shop-naming/main/install.sh | bash
```

**Windows:**
```powershell
# 下载并运行
curl -o install.bat https://raw.githubusercontent.com/coreyleung-art/flower-shop-naming/main/install.bat
install.bat
```

### 方式2: pip安装

```bash
pip install git+https://github.com/coreyleung-art/flower-shop-naming.git
```

### 方式3: 手动安装

```bash
# 克隆仓库
git clone https://github.com/coreyleung-art/flower-shop-naming.git
cd flower-shop-naming

# 直接使用
python3 item_naming_cli.py "商品名称"
```

## 使用方法

### 基本用法

```bash
# pip安装后
flower-naming "商品名称"

# 手动安装
python3 item_naming_cli.py "商品名称"
```

### 示例

```bash
# 鲜切花材
flower-naming "白色洋牡丹，默认C级"
# 输出: 鲜切花材-洋牡丹-白色-C级

# 包装纸
flower-naming "立体圆点压纹纸防水鲜花波卡尔圆点纸【藕粉】53*53cm/10张"
# 输出: 花艺资材-包花纸-包装纸-藕粉色-53*53cm-10张

# 花篮
flower-naming "白色矮35篮子"
# 输出: 花艺资材-礼盒/包装盒-花篮-白色-矮35cm

# 工具
flower-naming "5齿扒理花神器"
# 输出: 五金工具-理花神器-5齿
```

### 指定平台

```bash
flower-naming "商品名称" --platform 1688
flower-naming "商品名称" --platform taobao
flower-naming "商品名称" --platform pdd
flower-naming "商品名称" --platform huawu
```

### JSON输出

```bash
flower-naming "商品名称" --json
```

## 一级大类

| 大类 | 关键词示例 |
|-----|----------|
| 鲜切花材 | 玫瑰、郁金香、洋桔梗、康乃馨、向日葵、洋牡丹 |
| 鲜切叶材 | 叶材、散尾葵、龟背竹、尤加利叶 |
| 仿真/塑料花材 | 仿真花、塑料花、高仿 |
| 永生花/干花类型 | 永生花、干花、蓬莱松 |
| 园艺-盆栽 | 盆栽、绿植、多肉 |
| 花艺资材-包花纸 | 包装纸、压纹纸、圆点纸、牛皮纸、硬卡纸 |
| 花艺资材-丝带捆绑类耗材 | 丝带、扎带、胶带、鱼尾纱 |
| 花艺资材-花器 | 花瓶、花盆、醒花桶、圆肚瓶 |
| 花艺资材-包材 | 手提袋、礼品袋、防尘袋 |
| 花艺资材-礼盒/包装盒 | 礼盒、花盒、花篮、篮子 |
| 花艺资材-贺卡 | 贺卡、卡片、生日卡 |
| 花艺资材-玩偶/配件/道具 | 玩偶、招财猫、摆件、蝴蝶结 |
| 花艺资材-气球 | 气球、波波球、铝膜气球 |
| 花艺资材-喷漆喷色剂 | 喷漆、喷色剂、染色剂 |
| 花艺资材-耗材-粘贴剂 | 花泥、胶水、热熔胶 |
| 五金工具 | 剪刀、花泥刀、打刺夹、理花神器 |
| 道具 | 展示道具、羽毛、鸵鸟毛 |

## 命名格式

```
[一级大类]-[产品名称]-[颜色]-[规格]
```

### 示例

- `鲜切花材-洋牡丹-白色-C级`
- `花艺资材-包花纸-包装纸-藕粉色-53*53cm-10张`
- `花艺资材-花器-圆肚瓶-青釉-中号`
- `五金工具-理花神器-5齿`

## 单位建议

| 品类 | 默认单位 | 可选单位 | 常见规格 |
|-----|---------|---------|---------|
| 鲜切花材 | 扎 | 支、把、束 | 20支/扎、10支/扎 |
| 花艺资材-包花纸 | 张 | 包、卷 | 10张/包、20张/包 |
| 花艺资材-丝带 | 卷 | 米、码 | 25码/卷、40码/卷 |
| 花艺资材-花器 | 个 | 只、套 | - |
| 花艺资材-贺卡 | 张 | 包、套 | 10张/包 |

## 规格建议

| 品类 | 规格项 | 常见值 |
|-----|-------|-------|
| 鲜切花材 | 等级 | A级、B级、C级、D级、E级 |
| 花艺资材-包花纸 | 尺寸 | 50*70cm、58*58cm、45*45cm |
| 花艺资材-丝带 | 尺寸 | 2.5cm*25m、4cm*40码 |
| 花艺资材-花器 | 尺寸 | 大号、中号、小号 |

## API使用

```python
from item_naming_cli import ItemNamingReviewer

reviewer = ItemNamingReviewer()
result = reviewer.review("白色洋牡丹，默认C级")

print(result['standard_name'])  # 鲜切花材-洋牡丹-白色-C级
print(result['category'])       # 鲜切花材
print(result['color'])          # 白色
print(result['spec'])           # {'grade': 'C级'}
```

## 在Claude Code中使用

将以下内容保存到 `~/.claude/skills/命名审查.md`:

```markdown
---
name: 命名审查
description: 审查花店物品命名，将电商平台商品名称转换为标准命名格式
userInvocable: true
---

# 花店物品命名审查

## CLI工具位置
/path/to/flower-shop-naming/item_naming_cli.py

## 待审查商品
$ARGUMENTS
```

## 更新日志

### v2.0.0
- 简化类别名称：鲜切花-花材 → 鲜切花材，鲜切花-叶材 → 鲜切叶材
- 新增关键词：洋牡丹、压纹纸、圆点纸、花篮、篮子、理花神器、硬卡纸
- 新增颜色：藕粉色、牛皮色
- 优化颜色匹配：优先匹配更长的颜色词
- 新增规格提取：高/矮XX、直径XX、X齿、重量XX克
- 支持cm*cm格式的尺寸提取
- 添加pip安装支持
- 添加一键安装脚本

## License

MIT License
