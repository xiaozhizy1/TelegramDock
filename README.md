# TelegramDock

一个基于Docker的Telegram机器人系统，支持固定话术回复、用户信息查询、消息转发给管理员等功能。

## 功能特性

- 🤖 **固定话术回复**：`/start` 命令显示欢迎消息和菜单
- 🆔 **用户信息查询**：`/id` 命令显示用户详细信息
- 📨 **消息转发**：自动转发用户消息给管理员
- 💬 **管理员回复**：管理员可直接回复用户消息
- 📱 **多媒体支持**：支持文字、图片、文档、语音等所有消息类型
- 🔧 **配置管理**：基于INI文件的配置系统
- 📊 **数据持久化**：用户数据和消息日志自动保存

## 快速开始

### 1. 创建Telegram机器人

1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取机器人Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 获取管理员ID

1. 在Telegram中找到 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息获取你的用户ID
3. 记录数字ID（格式：`123456789`）

### 3. 部署安装机器人
### docker-compose.yml
```bash
services:
  telegramdock:
    build: .
    image: xiaozhizy/telegramdock:latest
    container_name: telegramdock
    restart: unless-stopped
    volumes:
      - ./config:/app/config
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge

volumes:
  bot-config:
    driver: local
```

### 4. 配置机器人

首次启动后，编辑配置文件：

```bash
# 编辑配置文件
 config/config.ini
```

修改以下配置：
```ini
[bot]
# 从 @BotFather 获取的机器人 Token
bot_token = 你的机器人Token
# 管理员用户 ID，可以从 @userinfobot 获取
admin_id = 你的用户ID
```

### 5. 重启服务

```bash
docker-compose restart
```

## 使用说明

### 用户功能

- **`/start`** - 显示欢迎消息和功能菜单
- **`/id`** - 查看个人用户信息
- **`/menu`** - 显示功能菜单
- **发送消息** - 任何消息都会转发给管理员

### 管理员功能

- **接收转发** - 自动接收所有用户消息
- **回复用户** - 使用格式：`@用户ID 回复内容`
  
  例如：`@123456789 您好，我们已收到您的问题`

### 支持的消息类型

- ✅ 文字消息
- ✅ 图片
- ✅ 文档
- ✅ 语音消息
- ✅ 视频
- ✅ 音频
- ✅ 贴纸
- ✅ 动画

## 配置说明

配置文件位于 `config/config.ini`：

```ini
[bot]
# 机器人Token（必填）
bot_token = YOUR_BOT_TOKEN_HERE
# 管理员用户ID（必填）
admin_id = YOUR_ADMIN_USER_ID_HERE

[messages]
# 消息转发成功提示
forward_success = 📨 您的消息已成功转发给客服人员，我们会尽快回复您！
# 消息转发失败提示
forward_failed = ❌ 消息转发失败，请稍后重试或联系技术支持。
```

## 致谢

### 开源技术支持

本项目基于以下优秀的开源技术构建：

- 🐍 **[Python](https://www.python.org/)** - 强大的编程语言，为机器人提供核心运行环境
- 📱 **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** - 优秀的Telegram Bot API Python库
- 🤖 **[Telegram Bot API](https://core.telegram.org/bots/api)** - Telegram官方提供的机器人接口
- 🐳 **[Docker](https://www.docker.com/)** - 容器化部署解决方案

感谢这些开源项目的贡献者们，让我们能够轻松构建功能强大的Telegram机器人！

## 支持项目

如果这个项目对您有帮助，欢迎支持我们的开发工作！


### 🌟 其他支持方式

- ⭐ **Star** 本项目
- 🐛 **提交Issue** 报告问题或建议
- 🔧 **Pull Request** 贡献代码
- 📢 **分享推荐** 给更多需要的人

### 📞 联系我们

- 📧 **邮箱**：xiaozhizy1@gmail.com
- 💬 **Telegram**：[@your_telegram](https://t.me/TRS1_bot)
- 🐙 **GitHub**：[项目地址](https://github.com/xiaozhizy1/TelegramDock)

---

*您的每一份支持都是我们前进的动力！感谢您的关注和使用！* ❤️

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
