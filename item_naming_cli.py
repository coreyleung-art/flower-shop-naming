#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
花店物品命名审查工具 CLI v2.0
用法: python3 item_naming_cli.py "商品原始名称" [--platform 1688|taobao|pdd|huawu]
"""

import argparse
import re
import json
from typing import Optional, Dict, List, Tuple

# ========== 配置数据 ==========

# 一级大类映射关键词（增强版）
# 注意：类别按优先级排序，花艺资材类优先于花材类
CATEGORY_KEYWORDS = {
    # ========== 花艺资材类（优先匹配）==========
    # 贺卡（高优先级，避免被花材误匹配）
    '花艺资材-贺卡': [
        '贺卡', '卡片', '祝福卡', '小卡片', '感谢卡', '生日卡', '生日卡片', '标签卡', '吊牌',
        '花艺卡', '花束卡', '问候卡', '节日卡', '明信片', '心愿卡',
    ],
    # 包花纸
    '花艺资材-包花纸': [
        '包装纸', '包花纸', '牛皮纸', '雪梨纸', '瓦楞纸', '欧雅纸', '韩素纸', '玻璃纸',
        '雾面纸', '牛奶棉', '木棉纸', '雪奈纸', 'OPP膜', '韩纸', '和纸', '油画纸',
        '防水纸', '珠光纸', '云龙纸', '莫奈', '肌理纸',
        '蝴蝶纸', '翅膀纸', '锦衣纸', '羽毛纸', '蕾丝纸',
        '压纹纸', '圆点纸', '波卡尔', '波点纸', '格子纸', '条纹纸', '印花纸',
    ],
    # 丝带
    '花艺资材-丝带捆绑类耗材': [
        '丝带', '扎带', '胶带', '鱼尾纱', '罗纹带', '波浪纱', '缎带', '纱带', '蕾丝带',
        '棉绳', '麻绳', '拉菲草', '雪纱', '欧根纱', '格子带',
    ],
    # 花器
    '花艺资材-花器': [
        '花瓶', '花器', '花盆', '醒花桶', '养花桶', '玻璃瓶', '陶瓷瓶', '花插', '剑山',
        '试管瓶', '吊瓶', '壁挂瓶',
        '圆肚瓶', '长颈瓶', '梅瓶', '葫芦瓶', '观音瓶', '玉壶春瓶', '天球瓶', '胆瓶',
        '蒜头瓶', '棒槌瓶', '凤尾瓶', '柳叶瓶', '灯笼瓶', '双耳瓶', '盘口瓶',
        '瓶',
    ],
    # 包材
    '花艺资材-包材': [
        '手提袋', '礼品袋', '防尘袋', '配送袋', '包装袋', '透明袋', '纸袋', '塑料袋',
        '礼袋', '束口袋',
    ],
    # 礼盒
    '花艺资材-礼盒/包装盒': [
        '礼盒', '包装盒', '花盒', '抱抱桶', '手提盒', '鲜花盒', '手捧盒',
        '盆栽礼盒', '绿植礼盒', '开业礼盒', '节日礼盒', '花篮', '篮子', '提篮',
    ],
    # 配件道具/摆件
    '花艺资材-玩偶/配件/道具': [
        '玩偶', '招财猫', '配件', '小熊', '蝴蝶结', '珍珠', '摆件', '陶瓷摆件',
        '装饰品', '挂件', '吊坠', '插片', '花艺配件', '婚庆配件', '开业配件',
        '仿真水果', '仿真蔬菜', '小天使', '爱心', '星星',
        '吉祥物', '生肖', '小马', '布艺马', '金元宝', '福字', '中国结',
    ],
    # 气球
    '花艺资材-气球': [
        '气球', '铝膜气球', '乳胶气球', '波波球', '氦气球', '字母气球', '数字气球',
        '长条气球', '心形气球', '波点气球',
    ],
    # 喷漆
    '花艺资材-喷漆喷色剂': [
        '喷漆', '喷色剂', '染色剂', '彩喷', '自喷漆', '碎冰蓝', '鲜花漆',
    ],
    # 耗材
    '花艺资材-耗材-粘贴剂': [
        '花泥', '胶水', '热熔胶', '泡沫板', '珍珠棉', '固定底座', '包花神器',
        '保鲜管', '营养管', '吸水棉', '花泥刀', '胶棒', '双面胶',
    ],
    '花艺资材-耗材-垃圾袋': ['垃圾袋', '清洁袋'],
    '花艺资材-桌布': ['桌布', '台布', '餐桌布'],
    '花艺资材-低值易耗品': ['一次性', '手套', '围裙', '袖套', '口罩'],
    '花艺资材-材料包': [
        '材料包', 'DIY材料', '手工包', '半成品',
        '扭扭棒', '手工花', '年宵花', 'DIY花束',
    ],
    # 工具
    '五金工具': ['剪刀', '花泥刀', '打刺夹', '工具', '美工刀', '削皮刀', '钳子', '铁丝'],
    # 道具
    '道具': ['展示道具', '装饰道具', '羽毛', '鸵鸟毛', '展示架', '花架', '陈列道具'],
    # 行政
    '行政耗材-文具': ['订书机', '订书针', '笔', '本子', '文件夹', '胶带座'],

    # ========== 花材类（后匹配）==========
    # 鲜切花
    '鲜切花材': [
        '玫瑰', '郁金香', '洋桔梗', '康乃馨', '向日葵', '菊花', '百合', '满天星', '紫罗兰',
        '草花', '绣球', '飞燕草', '牡丹', '洋牡丹', '尤加利', '腊梅', '小手球', '蝴蝶兰', '睡莲',
        '荷花', '芍药', '鸢尾', '洋甘菊', '雏菊', '翠珠', '蓝星花', '铁线莲', '雪柳',
    ],
    # 叶材
    '鲜切叶材': [
        '叶材', '散尾葵', '龟背竹', '春羽', '琴叶榕', '橡皮叶', '尤加利叶', '满天星叶',
    ],
    # 仿真花
    '仿真/塑料花材': [
        '仿真花', '仿真玫瑰', '仿真绣球', '仿真郁金香', '塑料花', '高仿', '假花', '永生花材',
    ],
    # 永生花/干花
    '永生花/干花类型': [
        '永生花', '干花', '千日红', '蓬莱松', '满天星干', '玫瑰干花', '绣球干花',
    ],
    # 园艺
    '园艺-盆栽': [
        '绿植', '多肉', '仙人掌', '发财树', '幸福树', '绿萝', '吊兰',
    ],
}

# 营销词/冗余词过滤
FILTER_WORDS = [
    '网红', '爆款', '热销', '新款', '创意', '高级感', 'ins风', '韩风', '日式', '北欧',
    '包邮', '特价', '批发', '厂家直销', '直销', '热卖', '精品', '高端', '豪华',
    '花店专用', '花艺资材', '鲜花包装', '花束包装', '花店资材', '花艺材料',
    '花束', '花盒', '鲜花', '花艺', '花店', '淘宝', '拼多多', '1688',
    '高级', '时尚', '潮流', '流行', '热卖', '畅销', '人气', '推荐',
    # 场景词
    '咖啡店', '奶茶店', '餐厅', '酒店', '办公室', '居家',
]

# 颜色词映射（增强版）
COLOR_MAPPING = {
    # 基础色
    '红': '红色', '粉红': '粉色', '粉': '粉色',
    '白': '白色', '奶白': '奶白色', '米白': '米白色',
    '黄': '黄色', '柠檬黄': '柠檬黄', '鹅黄': '鹅黄色',
    '金': '金色', '香槟金': '香槟金色',
    '银': '银色',
    '紫': '紫色', '淡紫': '淡紫色', '深紫': '深紫色',
    '橙': '橙色', '橘色': '橙色',
    '绿': '绿色', '浅绿': '浅绿色', '深绿': '深绿色', '墨绿': '墨绿色', '翠绿': '翠绿色',
    '蓝': '蓝色', '天蓝': '天蓝色', '深蓝': '深蓝色', '浅蓝': '浅蓝色',
    '黑': '黑色', '灰': '灰色',
    # 特殊色
    '香槟': '香槟色', '卡布奇诺': '卡布奇诺色', '咖啡': '卡布奇诺色', '奶茶': '奶茶色',
    '透明': '透明色', '原色': '原色', '混色': '混色',
    '碎冰蓝': '碎冰蓝', '薄雾紫': '薄雾紫', '火烈鸟粉': '火烈鸟粉',
    '蔷薇粉': '蔷薇粉', '樱花粉': '樱花粉', '莫兰迪': '莫兰迪色',
    '苏格兰绿': '苏格兰绿', '薄荷绿': '薄荷绿', '牛油果绿': '牛油果绿',
    '珊瑚粉': '珊瑚粉', '脏橘': '脏橘色', '脏粉': '脏粉色', '藕粉': '藕粉色',
    '莫兰迪粉': '莫兰迪粉', '莫兰迪蓝': '莫兰迪蓝', '莫兰迪绿': '莫兰迪绿',
    # 陶瓷釉色（优先匹配）
    '青釉': '青釉', '豆青釉': '豆青釉', '粉青釉': '粉青釉', '梅子青': '梅子青釉',
    '白釉': '白釉', '黑釉': '黑釉', '红釉': '红釉', '蓝釉': '蓝釉',
    '影青': '影青釉', '天青': '天青釉', '汝窑': '汝窑釉', '哥窑': '哥窑釉',
    # 材质色
    '木色': '原木色', '原木': '原木色', '竹': '竹色',
    # 特殊
    '彩色': '彩色', '混色': '混色', '多色': '彩色',
}

# 工艺词/款式词（非颜色，用于识别）
CRAFT_WORDS = ['粉彩', '青花', '斗彩', '珐琅', '釉里红', '颜色釉', '刻花', '印花', '贴花']
STYLE_WORDS = ['财源滚滚', '大吉大利', '心想事成', '万事如意', '恭喜发财', '一路生花', '繁花似锦',
               '步步高升', '生意兴隆', '开业大吉', '财源广进', '招财进宝']

# 材质映射
MATERIAL_MAPPING = {
    '陶瓷': '陶瓷',
    '玻璃': '玻璃',
    '塑料': '塑料',
    '纸质': '纸质',
    '牛皮纸': '牛皮纸',
    '布艺': '布艺',
    '木质': '木质',
    '金属': '金属',
    '铁艺': '铁艺',
    '竹编': '竹编',
    '草编': '草编',
    '藤编': '藤编',
    '亚克力': '亚克力',
    '树脂': '树脂',
    '泡沫': '泡沫',
}

# 单位建议库（按品类）
UNIT_SUGGESTIONS = {
    '鲜切花材': {
        'default': '扎',
        'options': ['扎', '支', '把', '束'],
        'standard_qty': ['20支/扎', '10支/扎', '5支/扎', '1支装'],
    },
    '鲜切叶材': {
        'default': '扎',
        'options': ['扎', '把', '束'],
        'standard_qty': ['10支/扎', '5支/扎'],
    },
    '花艺资材-包花纸': {
        'default': '张',
        'options': ['张', '包', '卷'],
        'standard_qty': ['10张/包', '20张/包', '50张/包'],
    },
    '花艺资材-丝带捆绑类耗材': {
        'default': '卷',
        'options': ['卷', '米', '码', '包'],
        'standard_qty': ['25码/卷', '40码/卷', '50米/卷'],
    },
    '花艺资材-花器': {
        'default': '个',
        'options': ['个', '只', '套'],
        'standard_qty': [],
    },
    '花艺资材-包材': {
        'default': '个',
        'options': ['个', '包', '卷', '套'],
        'standard_qty': ['10个/包', '20个/包', '50个/包'],
    },
    '花艺资材-礼盒/包装盒': {
        'default': '个',
        'options': ['个', '套', '盒'],
        'standard_qty': [],
    },
    '花艺资材-贺卡': {
        'default': '张',
        'options': ['张', '包', '套'],
        'standard_qty': ['10张/包', '20张/包', '50张/包'],
    },
    '花艺资材-玩偶/配件/道具': {
        'default': '个',
        'options': ['个', '套', '组', '对'],
        'standard_qty': [],
    },
    '花艺资材-气球': {
        'default': '包',
        'options': ['包', '袋', '卷', '个'],
        'standard_qty': ['10个/包', '20个/包', '50个/包', '100个/包'],
    },
    '花艺资材-喷漆喷色剂': {
        'default': '瓶',
        'options': ['瓶', '罐', '支'],
        'standard_qty': ['450ml/瓶', '300ml/瓶'],
    },
    '花艺资材-耗材-粘贴剂': {
        'default': '块',
        'options': ['块', '包', '箱', '卷'],
        'standard_qty': ['40块/箱', '20块/包'],
    },
    '五金工具': {
        'default': '把',
        'options': ['把', '个', '套'],
        'standard_qty': [],
    },
    '道具': {
        'default': '个',
        'options': ['个', '套', '组'],
        'standard_qty': [],
    },
}

# 规格建议库（按品类）
SPEC_SUGGESTIONS = {
    '鲜切花材': {
        'grade': ['A级', 'B级', 'C级', 'D级', 'E级'],
        'size': ['20支/扎', '10支/扎', '5支/扎'],
        'note': '等级从高到低：A级>B级>C级>D级>E级',
    },
    '花艺资材-包花纸': {
        'size': ['50*70cm', '58*58cm', '45*45cm', '38*52cm', '60*60cm'],
        'thickness': ['2.2丝', '2.3丝', '3丝'],
        'note': '常用尺寸50*70cm，厚度单位为"丝"',
    },
    '花艺资材-丝带捆绑类耗材': {
        'size': ['2.5cm*25m', '4cm*40码', '5cm*25m', '1cm*25m'],
        'note': '宽度*长度，1码=0.914米',
    },
    '花艺资材-花器': {
        'size': ['大号', '中号', '小号', '迷你'],
        'dimension': ['高*口径*底径cm'],
        'note': '建议标注具体尺寸，如：高20*口径10cm',
    },
    '花艺资材-包材': {
        'size': ['大号', '中号', '小号'],
        'dimension': ['长*宽*高cm', '60*70cm'],
        'note': '防尘袋常用60*70cm',
    },
    '花艺资材-喷漆喷色剂': {
        'volume': ['450ml', '300ml', '150ml'],
        'color_options': ['碎冰蓝', '薄雾紫', '火烈鸟粉', '蔷薇粉', '苏格兰绿'],
        'note': '常用450ml，颜色根据实际选择',
    },
    '花艺资材-玩偶/配件/道具': {
        'size': ['大号', '中号', '小号', '迷你'],
        'dimension': ['高*宽cm', '直径cm'],
        'note': '摆件类建议标注高度',
    },
    '花艺资材-气球': {
        'size': ['10寸', '12寸', '18寸', '24寸', '36寸'],
        'material': ['乳胶', '铝膜', '波波球'],
        'note': '气球尺寸用"寸"表示直径，1寸≈3.33cm',
    },
}

# 标准颜色词
STANDARD_COLORS = list(set(COLOR_MAPPING.values()))


class ItemNamingReviewer:
    """物品命名审查器 v2.0"""

    def __init__(self):
        self.category_keywords = CATEGORY_KEYWORDS
        self.filter_words = FILTER_WORDS
        self.color_mapping = COLOR_MAPPING
        self.material_mapping = MATERIAL_MAPPING
        self.unit_suggestions = UNIT_SUGGESTIONS
        self.spec_suggestions = SPEC_SUGGESTIONS

    def detect_platform(self, name: str) -> str:
        """检测来源平台"""
        if '规格型号' in name or '花艺资材' in name:
            return '1688'
        elif '淘宝' in name.lower():
            return 'taobao'
        elif '拼多多' in name or 'pdd' in name.lower():
            return 'pdd'
        elif '-' in name and '级' in name and '支' in name:
            return 'huawu'
        return 'unknown'

    def extract_spec(self, name: str) -> Dict[str, str]:
        """提取规格信息"""
        spec = {}

        # 提取等级 A/B/C/D/E级
        grade_match = re.search(r'([A-E])级', name)
        if grade_match:
            spec['grade'] = f'{grade_match.group(1)}级'

        # 提取数量 XX支/扎
        qty_match = re.search(r'(\d+)\s*支[/／]扎', name)
        if qty_match:
            spec['quantity'] = f'{qty_match.group(1)}支/扎'

        # 提取尺寸 XX*XXcm 或 XX*XX*XXcm 或 XX*XX*XX（无单位）
        size_match = re.search(r'(\d+)[*x×](\d+)(?:[*x×](\d+))?\s*(?:cm)?', name, re.IGNORECASE)
        if size_match:
            if size_match.group(3):
                spec['size'] = f'{size_match.group(1)}*{size_match.group(2)}*{size_match.group(3)}cm'
            else:
                spec['size'] = f'{size_match.group(1)}*{size_match.group(2)}cm'

        # 提取寸（气球等）
        inch_match = re.search(r'(\d+)\s*寸', name)
        if inch_match:
            spec['inch'] = f'{inch_match.group(1)}寸'

        # 提取规格型号中的内容
        spec_match = re.search(r'规格型号[：:]\s*([^;；]+)', name)
        if spec_match:
            spec['spec_detail'] = spec_match.group(1).strip()

        # 提取大号/中号/小号
        size_name = re.search(r'(超大号|大号|中号|小号|迷你|特小号)', name)
        if size_name:
            spec['size_name'] = size_name.group(1)

        # 提取容量 ml/L
        ml_match = re.search(r'(\d+)\s*(ml|ML|升|升)', name, re.IGNORECASE)
        if ml_match:
            spec['volume'] = f'{ml_match.group(1)}{ml_match.group(2).lower()}'

        # 提取数量 XX个/包 XX张/包 XX张/盒
        pack_match = re.search(r'(\d+)\s*(个|张|片|条|支|对|套)[/／](包|箱|卷|盒)', name)
        if pack_match:
            spec['pack'] = f'{pack_match.group(1)}{pack_match.group(2)}/{pack_match.group(3)}'

        # 提取 XX套/XX张 格式
        set_qty_match = re.search(r'(\d+)\s*套[/／](\d+)\s*张', name)
        if set_qty_match:
            spec['pack'] = f'{set_qty_match.group(1)}套{set_qty_match.group(2)}张'

        # 提取 *N包 格式
        star_pack_match = re.search(r'\*(\d+)\s*(包|袋|卷|箱)', name)
        if star_pack_match:
            spec['pack'] = f'{star_pack_match.group(1)}{star_pack_match.group(2)}'

        # 提取简单数量 XX张 XX个 XX片（不带有/包的）
        if 'pack' not in spec:
            simple_qty_match = re.search(r'(\d+)\s*(张|个|片|支|套)(?![/／])', name)
            if simple_qty_match:
                spec['quantity'] = f'{simple_qty_match.group(1)}{simple_qty_match.group(2)}'

        # 提取长度 XX码 XX米
        length_match = re.search(r'(\d+)\s*(码|米|m)(?![a-z])', name, re.IGNORECASE)
        if length_match:
            spec['length'] = f'{length_match.group(1)}{length_match.group(2)}'

        # 提取宽度 Xcm宽
        width_match = re.search(r'(\d+(?:\.\d+)?)\s*cm宽', name)
        if width_match:
            spec['width'] = f'{width_match.group(1)}cm'

        # 提取高度 高度:XXcm 或 高XXcm 或 高XX 或 矮XX
        height_match = re.search(r'(?:高度[：:]|高|矮)\s*(\d+(?:\.\d+)?)\s*(?:cm)?', name, re.IGNORECASE)
        if height_match:
            prefix = '矮' if '矮' in name[:height_match.end()] else '高'
            spec['height'] = f'{prefix}{height_match.group(1)}cm'

        # 提取直径 直径XXcm 或 直径XX
        diameter_match = re.search(r'直径\s*(\d+(?:\.\d+)?)\s*(?:cm)?', name, re.IGNORECASE)
        if diameter_match:
            spec['diameter'] = f'直径{diameter_match.group(1)}cm'

        return spec

    def extract_craft(self, name: str) -> Optional[str]:
        """提取工艺词（如粉彩、青花等）"""
        for craft in CRAFT_WORDS:
            if craft in name:
                return craft
        return None

    def extract_style(self, name: str) -> Optional[str]:
        """提取款式词（如财源滚滚、大吉大利等）"""
        for style in STYLE_WORDS:
            if style in name:
                return style
        return None

    def extract_color(self, name: str) -> Optional[str]:
        """提取并标准化颜色（排除工艺词、款式词、场景词干扰）"""
        # 先过滤营销词、工艺词、款式词
        temp_name = self.filter_marketing_words(name)
        for craft in CRAFT_WORDS:
            temp_name = temp_name.replace(craft, '')
        for style in STYLE_WORDS:
            temp_name = temp_name.replace(style, '')

        # 按长度降序排列，优先匹配更长的颜色词（如"藕粉"优先于"粉"）
        sorted_colors = sorted(self.color_mapping.items(), key=lambda x: len(x[0]), reverse=True)
        for original, standard in sorted_colors:
            if original in temp_name:
                return standard
        return None

    def extract_material(self, name: str) -> Optional[str]:
        """提取材质"""
        for keyword, material in self.material_mapping.items():
            if keyword in name:
                return material
        return None

    def filter_marketing_words(self, name: str) -> str:
        """过滤营销词"""
        result = name
        for word in self.filter_words:
            result = result.replace(word, '')
        return result

    def match_category(self, name: str) -> Optional[str]:
        """匹配一级大类"""
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in name:
                    return category
        return None

    def extract_product_name(self, name: str, category: str) -> str:
        """提取产品名称"""
        # 过滤营销词
        filtered = self.filter_marketing_words(name)

        # 移除规格型号部分
        filtered = re.sub(r'规格型号[：:].*$', '', filtered)
        filtered = re.sub(r'颜色[分类]*[：:].*$', '', filtered)
        filtered = re.sub(r'规格[：:].*$', '', filtered)

        # 根据类别提取核心词
        if category == '花艺资材-包花纸':
            if '玻璃纸' in filtered:
                return '玻璃纸'
            elif '牛皮纸' in filtered:
                return '牛皮纸'
            elif '雪梨纸' in filtered:
                return '雪梨纸'
            elif '木棉纸' in filtered or '牛奶棉' in filtered:
                return '木棉纸'
            elif '欧雅纸' in filtered:
                return '欧雅纸'
            elif '雪奈纸' in filtered:
                return '雪奈纸'
            elif '雾面纸' in filtered:
                return '雾面纸'
            elif '韩素纸' in filtered or '韩纸' in filtered:
                return '韩素纸'
            else:
                return '包装纸'

        elif category == '花艺资材-喷漆喷色剂':
            return '鲜花喷漆'

        elif category == '花艺资材-包材':
            if '防尘袋' in filtered:
                return '防尘袋'
            elif '手提袋' in filtered:
                return '手提袋'
            elif '礼品袋' in filtered:
                return '礼品袋'
            return '包装袋'

        elif category == '花艺资材-礼盒/包装盒':
            if '盆栽礼盒' in filtered or '绿植礼盒' in filtered:
                return '盆栽礼盒'
            elif '抱抱桶' in filtered:
                return '抱抱桶'
            elif '花篮' in filtered or '篮子' in filtered:
                return '花篮'
            elif '提篮' in filtered:
                return '提篮'
            elif '花盒' in filtered:
                return '花盒'
            elif '礼盒' in filtered:
                return '礼盒'
            return '包装盒'

        elif category == '花艺资材-贺卡':
            if '生日卡' in filtered or '生日' in filtered:
                return '生日卡'
            elif '新年卡' in filtered or '新年' in filtered or '贺岁' in filtered:
                return '新年卡'
            elif '感谢卡' in filtered or '感谢' in filtered:
                return '感谢卡'
            elif '祝福卡' in filtered or '祝福' in filtered:
                return '祝福卡'
            elif '节日卡' in filtered or '节日' in filtered:
                return '节日卡'
            elif '花束卡' in filtered:
                return '花束卡'
            elif '花艺卡' in filtered:
                return '花艺卡'
            elif '明信片' in filtered:
                return '明信片'
            return '贺卡'

        elif category == '花艺资材-丝带捆绑类耗材':
            if '鱼尾纱' in filtered:
                return '鱼尾纱'
            elif '罗纹带' in filtered:
                return '罗纹带'
            elif '丝带' in filtered:
                return '丝带'
            elif '扎带' in filtered:
                return '扎带'
            elif '胶带' in filtered:
                return '胶带'
            elif '蕾丝带' in filtered:
                return '蕾丝带'
            return '丝带'

        elif category == '花艺资材-花器':
            # 花瓶器型识别
            if '圆肚瓶' in filtered:
                return '圆肚瓶'
            elif '长颈瓶' in filtered:
                return '长颈瓶'
            elif '梅瓶' in filtered:
                return '梅瓶'
            elif '葫芦瓶' in filtered:
                return '葫芦瓶'
            elif '观音瓶' in filtered:
                return '观音瓶'
            elif '玉壶春瓶' in filtered:
                return '玉壶春瓶'
            elif '天球瓶' in filtered:
                return '天球瓶'
            elif '胆瓶' in filtered:
                return '胆瓶'
            elif '花瓶' in filtered:
                return '花瓶'
            elif '醒花桶' in filtered or '养花桶' in filtered:
                return '醒花桶'
            elif '抱抱桶' in filtered:
                return '抱抱桶'
            elif '花盆' in filtered:
                return '花盆'
            return '花器'

        elif category == '花艺资材-玩偶/配件/道具':
            if '摆件' in filtered:
                if '陶瓷' in filtered:
                    return '陶瓷摆件'
                return '摆件'
            elif '吉祥物' in filtered:
                if '布艺' in filtered:
                    return '布艺吉祥物'
                return '吉祥物'
            elif '布艺马' in filtered or '小马' in filtered:
                return '布艺马'
            elif '金元宝' in filtered:
                return '金元宝'
            elif '招财猫' in filtered:
                return '招财猫'
            elif '玩偶' in filtered or '小熊' in filtered:
                return '玩偶'
            elif '蝴蝶结' in filtered:
                return '蝴蝶结'
            elif '珍珠' in filtered:
                return '珍珠'
            elif '知花' in filtered:
                return '知花'
            elif '挂件' in filtered:
                return '挂件'
            return '配件'

        elif category == '花艺资材-气球':
            if '铝膜' in filtered:
                if '字母' in filtered:
                    return '字母铝膜气球'
                elif '数字' in filtered:
                    return '数字铝膜气球'
                return '铝膜气球'
            elif '乳胶' in filtered:
                return '乳胶气球'
            elif '波波球' in filtered:
                return '波波球'
            elif '长条' in filtered:
                return '长条气球'
            elif '心形' in filtered:
                return '心形气球'
            return '气球'

        elif category == '花艺资材-材料包':
            if '扭扭棒' in filtered or '手工花' in filtered:
                return '扭扭棒手工花'
            elif '年宵花' in filtered:
                return '年宵花材料包'
            elif 'DIY' in filtered:
                return 'DIY材料包'
            return '材料包'

        elif category == '鲜切花材':
            if '多头玫瑰' in filtered:
                return '多头玫瑰'
            elif '单头玫瑰' in filtered or '玫瑰' in filtered:
                return '单头玫瑰'
            elif '郁金香' in filtered:
                return '郁金香'
            elif '洋桔梗' in filtered:
                return '洋桔梗'
            elif '康乃馨' in filtered:
                return '康乃馨'
            elif '向日葵' in filtered:
                return '向日葵'
            elif '洋牡丹' in filtered:
                return '洋牡丹'
            elif '绣球' in filtered:
                return '绣球'
            elif '百合' in filtered:
                return '百合'
            elif '满天星' in filtered:
                return '满天星'
            elif '牡丹' in filtered:
                return '牡丹'
            elif '芍药' in filtered:
                return '芍药'
            elif '紫罗兰' in filtered:
                return '紫罗兰'
            elif '飞燕草' in filtered:
                return '飞燕草'
            elif '腊梅' in filtered:
                return '腊梅'
            elif '蝴蝶兰' in filtered:
                return '蝴蝶兰'
            elif '荷花' in filtered or '睡莲' in filtered:
                return '荷花'
            elif '鸢尾' in filtered:
                return '鸢尾'
            elif '洋甘菊' in filtered:
                return '洋甘菊'
            elif '雏菊' in filtered:
                return '雏菊'
            elif '翠珠' in filtered:
                return '翠珠'
            elif '蓝星花' in filtered:
                return '蓝星花'
            elif '铁线莲' in filtered:
                return '铁线莲'
            elif '雪柳' in filtered:
                return '雪柳'
            return '花材'

        elif category == '五金工具':
            if '剪刀' in filtered:
                return '花艺剪刀'
            elif '花泥刀' in filtered:
                return '花泥刀'
            elif '打刺夹' in filtered:
                return '打刺夹'
            return '工具'

        return '产品'

    def extract_pattern(self, name: str) -> Optional[str]:
        """提取图案/款式"""
        patterns = [
            '蝴蝶翅膀', '蝴蝶', '翅膀', '羽毛', '蕾丝',
            '油菜花', '莫奈花园', '油画', '印花', '星空', '格纹',
            '纯色', '条纹', '波点', '碎花', '锦衣',
        ]
        for p in patterns:
            if p in name:
                return f'{p}图案' if p not in ['纯色', '条纹', '格纹', '波点'] else p
        return None

    def get_unit_suggestion(self, category: str) -> Dict:
        """获取单位建议"""
        return self.unit_suggestions.get(category, {
            'default': '个',
            'options': ['个', '套', '包'],
            'standard_qty': [],
        })

    def get_spec_suggestion(self, category: str) -> Dict:
        """获取规格建议"""
        return self.spec_suggestions.get(category, {
            'note': '请根据实际情况填写规格',
        })

    def generate_standard_name(self, original_name: str, platform: str = None) -> Dict:
        """生成标准命名"""
        result = {
            'original_name': original_name,
            'platform': platform or self.detect_platform(original_name),
            'suggested_name': None,
            'category': None,
            'product_name': None,
            'material': None,
            'color': None,
            'spec': {},
            'unit_suggestion': {},
            'spec_suggestion': {},
            'modifications': [],
        }

        # 1. 匹配一级大类
        category = self.match_category(original_name)
        if not category:
            result['modifications'].append('⚠️ 无法自动匹配一级大类，需要手动指定')
            category = '未分类'
        result['category'] = category

        # 2. 提取材质
        material = self.extract_material(original_name)
        if material:
            result['material'] = material

        # 3. 提取颜色
        color = self.extract_color(original_name)
        if color:
            result['color'] = color
            result['modifications'].append(f'颜色标准化: → {color}')

        # 4. 提取规格
        spec = self.extract_spec(original_name)
        result['spec'] = spec

        # 5. 提取产品名称
        product_name = self.extract_product_name(original_name, category)
        result['product_name'] = product_name

        # 6. 提取图案
        pattern = self.extract_pattern(original_name)

        # 7. 获取单位和规格建议
        if category != '未分类':
            result['unit_suggestion'] = self.get_unit_suggestion(category)
            result['spec_suggestion'] = self.get_spec_suggestion(category)

        # 8. 组装标准命名
        parts = [category]

        # 避免重复（如"花艺资材-气球-气球"）
        if product_name not in category:
            parts.append(product_name)

        if pattern:
            parts.append(pattern)

        if material and material not in product_name:
            parts.append(material)

        if color:
            parts.append(color)

        # 添加规格
        if 'size_name' in spec:
            parts.append(spec['size_name'])
        elif 'size' in spec:
            parts.append(spec['size'])

        if 'inch' in spec:
            parts.append(spec['inch'])

        if 'grade' in spec and 'quantity' in spec:
            parts.append(f"{spec['grade']}-{spec['quantity']}")
        elif 'grade' in spec:
            parts.append(spec['grade'])
        elif 'quantity' in spec:
            parts.append(spec['quantity'])

        if 'volume' in spec:
            parts.append(spec['volume'])

        if 'height' in spec:
            parts.append(spec['height'])

        if 'pack' in spec:
            parts.append(spec['pack'])

        result['suggested_name'] = '-'.join(parts)

        # 9. 添加修改说明
        filtered = self.filter_marketing_words(original_name)
        if filtered != original_name:
            result['modifications'].append('已过滤营销词/冗余词')

        return result

    def review(self, original_name: str, platform: str = None) -> str:
        """审查并返回格式化结果"""
        result = self.generate_standard_name(original_name, platform)

        output = []
        output.append("=" * 70)
        output.append("花店物品命名审查结果 v2.0")
        output.append("=" * 70)
        output.append(f"原始名称: {result['original_name']}")
        output.append(f"来源平台: {result['platform']}")
        output.append("-" * 70)
        output.append(f"一级大类: {result['category']}")
        output.append(f"产品名称: {result['product_name']}")
        output.append(f"材质: {result['material'] or '(未识别)'}")
        output.append(f"标准颜色: {result['color'] or '(未识别)'}")
        output.append(f"规格信息: {result['spec'] or '(未识别)'}")
        output.append("-" * 70)
        output.append(f"✅ 建议命名: {result['suggested_name']}")
        output.append("-" * 70)

        # 单位建议
        if result['unit_suggestion']:
            unit = result['unit_suggestion']
            output.append("📦 单位建议:")
            output.append(f"   默认单位: {unit['default']}")
            output.append(f"   可选单位: {', '.join(unit['options'])}")
            if unit['standard_qty']:
                output.append(f"   常见规格: {', '.join(unit['standard_qty'])}")

        # 规格建议
        if result['spec_suggestion']:
            spec_sug = result['spec_suggestion']
            output.append("📏 规格建议:")
            for key, value in spec_sug.items():
                if key != 'note' and value:
                    if isinstance(value, list):
                        output.append(f"   {key}: {', '.join(value)}")
                    else:
                        output.append(f"   {key}: {value}")
            if 'note' in spec_sug:
                output.append(f"   💡 {spec_sug['note']}")

        output.append("-" * 70)
        output.append("📝 修改说明:")
        for mod in result['modifications']:
            output.append(f"   • {mod}")
        if not result['modifications']:
            output.append("   • 无需修改")
        output.append("=" * 70)

        return "\n".join(output)

    def to_json(self, original_name: str, platform: str = None) -> str:
        """返回JSON格式结果"""
        result = self.generate_standard_name(original_name, platform)
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='花店物品命名审查工具 v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 item_naming_cli.py "鲜花喷漆花艺彩色碎冰蓝花束喷色剂 规格型号: 碎冰蓝;450ml"
  python3 item_naming_cli.py "单头玫瑰-戴安娜-红色-C级-20支/扎" --platform huawu
  python3 item_naming_cli.py "北欧陶瓷摆件青釉知花" --json
        """
    )
    parser.add_argument('name', help='商品原始名称')
    parser.add_argument('--platform', '-p', choices=['1688', 'taobao', 'pdd', 'huawu'],
                        help='指定来源平台')
    parser.add_argument('--json', '-j', action='store_true',
                        help='输出JSON格式')

    args = parser.parse_args()

    reviewer = ItemNamingReviewer()

    if args.json:
        print(reviewer.to_json(args.name, args.platform))
    else:
        print(reviewer.review(args.name, args.platform))


if __name__ == '__main__':
    main()
