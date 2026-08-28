# -*- coding: utf-8 -*-
"""
Vortex（mihomo）代理配置一键修复脚本
=====================================
用途：订阅更新清规则 / mode 回退 direct / TUN 关闭时，一键恢复良好配置。

背景：机场订阅更新会反复重写 config.yaml —— 清掉 5 条 OpenAI 分流规则、
把 mode 还原成 direct、external-controller 改回 39797、MATCH 兜底指向坏节点。
本脚本在 2026-08-10 第 7 次复发后沉淀（见知识库FAQ 04 文档复发记录）。

功能：
  1. 备份当前 config.yaml 到知识库 FAQ 原始文件备份/
  2. 修复：mode->rule、external-controller->39798、恢复 5 条 OpenAI 规则->美国-IEPL 02、
     MATCH->香港-IEPL 01（可按需修改）
  3. 热加载（PUT /configs?force=true）
  4. 恢复 TUN（PATCH /configs tun.enable=true）
  5. 验证运行态 mode / tun

用法：
  python fix_vortex_config.py

依赖：Python 3.x（标准库），Vortex 控制 API 运行在 127.0.0.1:39798。

修改节点：若美国-IEPL 02 波动，可把 OPENAI_NODE 换成实测可用节点
（如 🇺🇸|美国-IEPL 01、🇺🇸|美国-直连）；MATCH_NODE 同理。
"""
import sys, io, os, time, shutil, urllib.request, json

sys.stdout.reconfigure(encoding='utf-8')

CONFIG_PATH = r'C:\Users\asus\.config\com.vortex.helper\config.yaml'
BACKUP_DIR = r'F:\积昌的知识库 - 副本\总结好的大纲以及笔记\知识库FAQ\原始文件备份'
BASE = 'http://127.0.0.1:39798'

# 5 条 OpenAI 分流规则指向的节点（实测放行 ChatGPT 的节点）
# 2026-08-18 16:0x 实测更新：美国线路全线超时（家宽01/IEPL 02/中转 02/进阶IEPL 02 TLS 握手卡死）；
# 台湾-IEPL 03 与 日本-IEPL 01/02 两轮 401 全通，其中 台湾-IEPL 03 最快（0.4-0.5s）。
# 故 OPENAI_NODE 与 MATCH_NODE 均设为 台湾-IEPL 03。若台湾线路波动，可换成 日本-IEPL 01/02 实测。
OPENAI_NODE = '🇹🇼|台湾-IEPL 03'
# MATCH 兜底节点（外网快节点，实测对 Google/YouTube 等可用）
MATCH_NODE = '🇹🇼|台湾-IEPL 03'

OPENAI_RULES = '''  - DOMAIN-SUFFIX,openai.com,{node}
  - DOMAIN-SUFFIX,chatgpt.com,{node}
  - DOMAIN-SUFFIX,chatgpt-api.com,{node}
  - DOMAIN-SUFFIX,oaistatic.com,{node}
  - DOMAIN-SUFFIX,oaiusercontent.com,{node}
'''.format(node=OPENAI_NODE)


def main():
    if not os.path.exists(CONFIG_PATH):
        print(f'❌ 找不到配置文件: {CONFIG_PATH}')
        return

    # 1. 备份
    ts = time.strftime('%Y%m%d-%H%M')
    os.makedirs(BACKUP_DIR, exist_ok=True)
    bak = os.path.join(BACKUP_DIR, f'vortex-config-{ts}-before-fix.yaml')
    shutil.copy(CONFIG_PATH, bak)
    print(f'✅ 备份: {bak}')

    # 2. 修复配置文件
    with io.open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    changes = []

    def sub(old, new, tag):
        nonlocal text
        if old in text:
            text = text.replace(old, new, 1)
            changes.append(tag)

    sub('mode: direct', 'mode: rule', 'mode')
    sub('external-controller: 127.0.0.1:39797',
        'external-controller: 127.0.0.1:39798', 'external-controller')
    if 'DOMAIN-SUFFIX,openai.com' not in text:
        anchor = '  - GEOIP, CN, DIRECT'
        if anchor in text:
            text = text.replace(anchor, OPENAI_RULES + anchor, 1)
            changes.append('OpenAI规则x5')
    sub('  - MATCH, 节点选择', f'  - MATCH, {MATCH_NODE}', 'MATCH兜底')

    with io.open(CONFIG_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(f'✅ 配置修改: {changes if changes else "无需修改（已良好）"}')

    # 3. 热加载
    req = urllib.request.Request(
        BASE + '/configs?force=true', method='PUT',
        data=json.dumps({'path': CONFIG_PATH}).encode(),
        headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req, timeout=15)
        print('✅ 热加载: 204')
    except urllib.error.HTTPError as e:
        print(f'❌ 热加载失败: HTTP {e.code} {e.read()[:200]}')
        return

    # 4. 恢复 TUN
    req = urllib.request.Request(
        BASE + '/configs', method='PATCH',
        data=json.dumps({'tun': {'enable': True}}).encode(),
        headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req, timeout=15)
        print('✅ 恢复TUN: 204')
    except urllib.error.HTTPError as e:
        print(f'❌ 恢复TUN失败: HTTP {e.code} {e.read()[:200]}')

    # 5. 验证
    try:
        d = json.load(urllib.request.urlopen(BASE + '/configs', timeout=8))
        print(f'✅ 验证: mode={d["mode"]} | port={d["mixed-port"]} | tun={d["tun"]["enable"]}')
    except Exception as e:
        print(f'⚠️ 验证失败: {e}')

    print('\n修复完成。若仍无法访问，用浏览器开 ChatGPT 或执行:')
    print('  curl -s -o /dev/null -w "%{http_code}" -x http://127.0.0.1:7897 https://chatgpt.com/')


if __name__ == '__main__':
    main()
