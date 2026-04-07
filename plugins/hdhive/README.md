# 影巢 HDHive 签到插件

 MoviePilot 插件，支持影巢站点自动签到。

## 功能

- 手动触发签到：`/hdhive_sign`
- 每日自动签到（可配置开启）
- 签到结果消息推送

## 安装

### 方式一：添加到第三方插件仓库

将本仓库添加到 MoviePilot 插件源：

1. MoviePilot → 设置 → 插件 → 添加插件仓库
2. 填入本仓库地址：`https://github.com/kingbb2001/test2`
3. 在插件市场搜索"影巢"安装

### 方式二：手动安装

将 `plugins/hdhive` 目录复制到 MoviePilot 的 `app/plugins/` 目录下。

## 配置

1. 在影巢网页端登录
2. 按 F12 打开开发者工具 → Application → Cookies → 找到 Cookie 值
3. 将完整 Cookie 复制到插件设置中
4. 根据需要开启"自动签到"

## 获取 Cookie

1. 打开 https://hdhive.com 并登录
2. 按 F12 打开开发者工具
3. 切换到 Application（应用程序）标签
4. 左侧选择 Cookies → https://hdhive.com
5. 找到并复制 Cookie 列中的全部内容

## 注意事项

- 请确保 Cookie 有效，失效后需要重新获取
- 自动签到默认时间为每天早上 8:00
