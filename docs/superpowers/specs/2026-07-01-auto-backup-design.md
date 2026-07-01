# 全局自动备份设计文档

**日期**: 2026-07-01
**状态**: 已批准
**关联项目**: notify-hooks

---

## 1. 概述

为 notify-hooks 项目添加全局自动备份功能：每次 `git commit` 后自动推送到 GitHub 对应分支，实现代码的实时远程备份。

## 2. 背景

- 项目已有 GitHub 远程仓库（`github.com/Beijongggg/notify-hooks`）
- 当前工作流：手动 `git push`，无自动备份
- 需要：提交即备份，零人工干预

## 3. 分支策略

| 分支 | 用途 |
|------|------|
| `develop` | 日常开发，自动备份推送目标分支（默认） |
| `master` | 稳定正式版，仅手动合并发布时更新 |
| 其他功能分支 | 临时分支，同样自动推送 |

初始化方式：基于 `master` 创建 `develop` 分支并推送建立追踪关系。

## 4. 设计方案（方案一：Git post-commit hook）

### 4.1 脚本文件

**位置**: `hooks/post-commit.sh`（纳入 Git 追踪，随项目分发）
**安装目标**: `.git/hooks/post-commit`（本地 Git hooks 目录，不被 Git 追踪）

### 4.2 核心逻辑

```
1. 获取当前分支名
2. 执行 git push origin HEAD
3. 成功 → 静默退出，无输出
4. 失败 → 追加错误日志到 ~/.claude/hooks/notify_error.log
```

### 4.3 设计要点

- **无声推送**：成功时不产生任何输出，不干扰 commit 流程
- **失败有迹**：失败时写入日志（共用 notify.py 的错误日志路径），不阻塞终端
- **全分支覆盖**：不设分支白名单，所有分支提交后均触发 push
- **认证无感**：remote URL 已内嵌 token，push 全自动无需交互

### 4.4 安装集成

在 `install.md` 中增加自动备份安装步骤：

```bash
cp hooks/post-commit.sh .git/hooks/post-commit
```

并注明：如果已有 `.git/hooks/post-commit` 则需手动合并。

## 5. 不涉及变更

- 不修改 `notify.py`（备份逻辑独立，不强耦合）
- 不修改 `config.example.json`（备份不需配置项）
- 不修改任何现有 Git 设置或工作流

## 6. 恢复方案

如果需要从备份恢复代码：

```bash
git clone https://github.com/Beijongggg/notify-hooks.git
git checkout develop
```

日常开发继续在 `develop` 分支进行。

## 7. 边界情况

| 场景 | 行为 |
|------|------|
| 离线时 commit | push 失败，记录日志，下次 commit 自动重试 |
| `.git/hooks/post-commit` 已被其他工具占用 | 安装时提示手动合并 |
| push 因冲突失败 | 记录日志，手动解决后下次 commit 自动重试 |
| 在 master 上提交 | 同样 push master，无需特殊处理 |
