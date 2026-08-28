---
title: "Codex模型配置方法大全"
date: 2026-07-12
tags:
  - 笔记整理
  - 听课记录
  - Codex
  - DeepSeek
  - AI配置
created: 2026-07-12
---

# Codex模型配置方法大全

> [!INFO] 课程信息
> - **类型**：课程讲解
> - **日期**：2026-07-12
> - **主题**：Codex Desktop 安装与配置（接入 DeepSeek 等模型）
> - **来源**：备忘录文档_202607121037（语音转写）

## 目录

1. [[#Codex 供应商（Provider）配置]]
2. [[#Codex 安装方式]]
3. [[#Codex 启动与首次使用]]
4. [[#模型选择与切换]]
5. [[#常见问题与解决方案]]
6. [[#版本与资源说明]]

---

## 1. Codex 供应商（Provider）配置

### 1.1 打开管理工具

- 启动 Codex 应用后，打开 **Codex++ 管理工具**
- 点击 **"添加供应商"**（Add Provider）按钮进入配置页面

> [!TIP] 关联附件
> 详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=4]] 中关于 Codex++ 配置 DeepSeek API 的详细说明

### 1.2 供应商配置字段说明

在添加供应商页面中，需要填写以下几个关键字段：

| 配置项 | 说明 |
|--------|------|
| **名称** | 可自定义，如 `DeepSeek`、`faker` 等 |
| **接入模式** | 选择 **纯 API**（或 GAP 模式） |
| **测试模型** | 如 `deepseek-v4-flash`（即第4代模型） |
| **Base URL** | API 地址，如 `https://api.deepseek.com` |
| **Key** | 在 DeepSeek 开放平台申请的 API Key |
| **上游协议** | 选择 **Chat Completions**（即 check 平台/协议） |

### 1.3 配置步骤

1. **第一步：申请 API Key**
   - 前往对应平台的官网进行注册
   - 在 API Key 管理页面创建新的 Key
   - 将 Key 复制并粘贴到 Codex++ 配置中

2. **第二步：填写配置信息**
   - 名称：自定义（如 `DeepSeek`）
   - 接入模式：选择 **纯 API**
   - 测试模型：填写模型名称（如 `deepseek-v4-flash`）
   - Base URL：填写 API 地址
   - Key：粘贴上一步申请的 API Key
   - 上游协议：选择 **Chat Completions**

3. **第三步：保存并启用**
   - 点击 **保存** 按钮
   - 返回供应商列表
   - 点击 **使用/启用** 按钮激活该供应商
   - 右上角会提示启用成功

> [!TIP] 关联附件
> 不同版本 Codex++ 的配置界面略有差异，详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=5]]（v1.1.7 版本）和 [[Codex Desktop 安装 + DeepSeek！.pdf#page=6]]（v1.1.9/v1.2.0/v1.2.3 版本）

---

## 2. Codex 安装方式

安装 Codex 主要有以下几种方式：

### 2.1 从 OpenAI 官网下载

- 直接从 OpenAI 官网下载 Codex 安装包
- **无需科学上网**，可直接下载
- 以 Windows 为例，双击 `Codex Installer.exe` 启动安装
- 安装完成后可能会白屏一段时间（因请求 OpenAI 服务器超时导致），等待自动进入下一步即可

> [!TIP] 关联附件
> 详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=11]] 中关于从 OpenAI 官网安装的说明

### 2.2 从 Microsoft Store 下载

- 在 Microsoft Store 中搜索并安装 Codex
- 安装后的操作与官网版本相同

> [!TIP] 关联附件
> 详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=15]]

### 2.3 使用 Codex++ 启动器

- **Codex++** 是面向 Codex App 的外部增强启动器和配置管理工具
- 它不修改原始安装文件，而是通过外部 launcher 启动 Codex
- 使用 Chromium DevTools Protocol 注入增强脚本
- 安装 Codex++ 后，会有两个入口：
  - **Codex++**：静默启动入口，不显示管理界面
  - **Codex++ 管理工具**：Tauri 控制面板，用于启动、检查、修复、更新、配置等

> [!TIP] 关联附件
> 详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=1]]（Codex++ 下载与安装说明）和 [[Codex Desktop 安装 + DeepSeek！.pdf#page=16]]（使用 Codex++ 启动 Codex）

---

## 3. Codex 启动与首次使用

### 3.1 启动流程

1. 使用 **Codex++** 启动 Codex（注意不要直接启动 Codex）
2. 启动后会出现加载页面，停留约 **2分钟以内**
3. 白屏期间会请求 OpenAI 服务器，在无科学上网环境下，域名被阻断导致请求超时

### 3.2 白屏/加载慢的解决方案

- **方案一**：使用科学上网（VPN/代理）
- **方案二**：启动时断开网络（断网后加载速度会加快）

> [!TIP] 关联附件
> 关于启动慢的详细原因分析，详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=21]]

### 3.3 跳过加载

- 加载页面出现后，可以点击 **Skip** 跳过
- 如果点击 Skip 没有反应，可以多试几次
- 如果卡住了一直没变化，可以完全退出 Codex 和 Codex++（包括后台进程），然后重新启动
- 再次打开后会看到白屏，等待一段时间后会成功进入 Codex 界面

### 3.4 首次使用配置

- **Agent Sandbox 设置**：第一次打开后，需要点击 **Set up** 按钮配置管理员沙盒
- 点击 **Stop** 即可完成设置
- 系统会提示"创建中"→"创建成功"

### 3.5 功能测试

- 可以进行简单的对话测试
- 也可以在桌面创建文件进行测试
- 确认配置是否生效

> [!TIP] 关联附件
> 详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=19]]（启用 Agent Sandbox）和 [[Codex Desktop 安装 + DeepSeek！.pdf#page=20]]（功能测试）

---

## 4. 模型选择与切换

### 4.1 模型选择页面

- 在 **cortex** 对话页面中可以进行模型选择
- 页面顶部有一个模型选择器（前面是推墙/推理强度选择）

### 4.2 可用模型

如果配置成功，模型选择中会显示出以下选项：

- **DC**（默认模型，GPS/4th 模型）
- **Pro**（增强版模型）
- 部分版本中还可以选择 **VS30** 等其他模型

> [!TIP] 关联附件
> 模型选择的详细说明详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=20]]

### 4.3 模型未显示的处理

如果模型选择中没有显示 DeepSeek 或自定义模型：

1. 完全退出 Codex++ 和 Codex（包括后台进程）
2. 重新复核供应商配置是否正确
3. 重新启动 Codex++

---

## 5. 常见问题与解决方案

### 5.1 启动相关问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 启动慢/白屏时间长 | 无科学上网，域名被阻断 | 使用 VPN 或断网启动 |
| 打不开 Codex 程序 | 版本或进程问题 | 升级 Codex++ 到 v1.2.3，检查托盘图标 |

> [!TIP] 关联附件
> 详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=22]] 开始的常见问题章节

### 5.2 API 配置问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 401 Authentication Fails | API Key 错误 | 新建 API Key，新建供应商重新配置 |
| 402 Payment Required | 账户余额不足 | 前往 DeepSeek 开放平台充值（最低1元） |
| 404 Not Found | Base URL 配置错误 | 检查 URL 是否有空格等错误 |
| 502 Bad Gateway | 代理配置问题 | 关闭代理或排除本地地址 |

### 5.3 模型显示问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 无法显示 DeepSeek 选项 | 供应商未正确配置 | 复核配置，完全退出后重启 |
| 只有一个 DeepSeek 模型 | 模型列表未完整配置 | 检查模型列表字段 |

### 5.4 汉化问题

- 目前汉化需要**科学上网**（无法在不科学上网的情况下直接汉化）
- 操作步骤：
  1. 开启 VPN（全局模式/Tun 模式，使用美国节点）
  2. 进入 Settings → General → Language → 选择 **中文(中国)**
  3. 完全退出 Codex
  4. 重启 Codex++

> [!TIP] 关联附件
> 详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=40]]

### 5.5 其他常见问题

| 问题 | 解决方案 |
|------|---------|
| 上传图片报错 | DeepSeek 暂不支持多模态，删除含图片的会话 |
| 上下文长度显示258k（配置了1m） | 已知问题，参考相关 GitHub Issue |
| VCRUNTIME140.dll 找不到 | 安装 VC++ 运行库 |
| Mac 安装显示已损坏 | 执行 `sudo xattr -rd com.apple.quarantine` 命令 |
| Codex 无法访问本地数据库 | 删除 `.codex` 文件夹后重试 |
| Error starting chat | 删除 `config.toml` 文件后重配 |

> [!TIP] 完整常见问题列表
> 详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=22]]（6.1 至 6.27 共27个常见问题及解决方案）

---

## 6. 版本与资源说明

### 6.1 推荐版本

- **Codex++**：推荐使用 **V1.2.3** 版本
  - 如果你是旧版本，建议升级到此版本以获取更好的兼容性
  - 升级方式：先卸载旧版 → 再安装新版

> [!TIP] 关联附件
> 详见 [[Codex Desktop 安装 + DeepSeek！.pdf#page=2]] 版本选择说明和 [[Codex Desktop 安装 + DeepSeek！.pdf#page=36]] 升级指南

### 6.2 API 充值说明

- 如果使用 DeepSeek 等第四代模型，注册后**建议先充值**
- 不充值的话后面无法使用
- 最低充值金额：**1元**

### 6.3 资源获取

- 如果访问 GitHub 等网站有困难，视频配套资料中提供了相关安装文件
- 配套资料包括：Codex++ 安装包、相关配置文件等

---

## 总结

本课程全面讲解了 Codex Desktop 的配置与使用方法，核心要点如下：

1. **供应商配置**：在 Codex++ 管理工具中添加供应商，配置 API Key、Base URL、协议等信息
2. **安装方式**：支持 Open AI 官网下载、Microsoft Store、Codex++ 启动器三种方式
3. **启动与使用**：使用 Codex++ 启动，注意白屏等待问题，可通过科学上网或断网解决
4. **模型选择**：配置成功后可在 cortex 页面选择不同模型（DC/Pro 等）
5. **常见问题**：涵盖 API 认证、余额不足、代理冲突、汉化等27个常见问题的解决方案

## 相关笔记

- [[Codex++使用教程]]
- [[Codex的5.6三大旗舰模型差异]] — GPT-5.6 三档模型（Sol/Terra/Luna）差异与选择
- [[Codex Desktop 安装 + DeepSeek！.pdf]]
- [[Claude Code 入门与 GitHub 协作开发指南]]
- [[Claude Code从0~1的入门]]
- [[Codex使用教程]] — Codex 安装与使用指南
- [[Codex 零基础系统入门教程]] — Codex 零基础系统入门教程
