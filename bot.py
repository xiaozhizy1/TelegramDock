#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TelegramDock - Telegram机器人系统
功能：
1. /start 命令回复固定话术
2. /id 命令显示用户信息
3. 消息转发给管理员
4. 菜单系统
5. 配置文件和数据持久化
"""

import os
import json
import logging
import configparser
from datetime import datetime
from logging.handlers import RotatingFileHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

class TelegramBot:
    def __init__(self):
        # 设置基本日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 初始化配置
        self.config = configparser.ConfigParser()
        
        # 检查并创建配置（但不退出）
        self.config_complete = self.check_and_create_config()
        
        # 始终加载配置（即使不完整）
        self.load_config()
        self.setup_logging()
        self.setup_directories()
        
    def check_and_create_config(self):
        """检查并创建配置文件，返回配置是否完整"""
        config_path = 'config/config.ini'
        
        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(config_path):
            self.logger.info(f"配置文件不存在，创建默认配置: {config_path}")
            self.create_default_config(config_path)
            self.logger.warning("=" * 60)
            self.logger.warning("🔧 首次运行检测到，已创建默认配置文件")
            self.logger.warning("📝 请尽快配置机器人信息:")
            self.logger.warning("1. 编辑 config/config.ini 文件")
            self.logger.warning("2. 设置正确的 bot_token (从 @BotFather 获取)")
            self.logger.warning("3. 设置正确的 admin_id (从 @userinfobot 获取)")
            self.logger.warning("4. 重新启动容器: docker-compose restart")
            self.logger.warning("⚠️  机器人将使用默认配置运行，功能可能受限")
            self.logger.warning("=" * 60)
            return False
            
        # 检查配置是否完整
        temp_config = configparser.ConfigParser()
        temp_config.read(config_path, encoding='utf-8')
        
        try:
            bot_token = temp_config.get('bot', 'bot_token')
            admin_id = temp_config.get('bot', 'admin_id')
            
            if bot_token == 'YOUR_BOT_TOKEN_HERE' or admin_id == 'YOUR_ADMIN_USER_ID_HERE':
                self.logger.warning("=" * 60)
                self.logger.warning("⚠️  配置文件需要完善")
                self.logger.warning("📝 请尽快配置机器人信息:")
                self.logger.warning("1. 编辑 config/config.ini 文件")
                self.logger.warning("2. 设置正确的 bot_token (从 @BotFather 获取)")
                self.logger.warning("3. 设置正确的 admin_id (从 @userinfobot 获取)")
                self.logger.warning("4. 重新启动容器: docker-compose restart")
                self.logger.warning("⚠️  机器人将使用默认配置运行，功能可能受限")
                self.logger.warning("=" * 60)
                return False
                
        except Exception as e:
            self.logger.error(f"配置文件格式错误: {e}")
            return False
            
        return True
    
    def create_default_config(self, config_path):
        """创建默认配置文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        os.makedirs('config/logs', exist_ok=True)
        os.makedirs('config/data', exist_ok=True)
        
        default_config = """[bot]
# 从 @BotFather 获取的机器人 Token
bot_token = YOUR_BOT_TOKEN_HERE
# 管理员用户 ID，可以从 @userinfobot 获取
admin_id = YOUR_ADMIN_USER_ID_HERE

[messages]
# 欢迎消息（在代码中定义，此处保留用于扩展）
start_message = 欢迎使用TelegramDock智能客服系统！
# 消息转发成功提示
forward_success = 📨 您的消息已成功转发给客服人员，我们会尽快回复您！
# 消息转发失败提示
forward_failed = ❌ 消息转发失败，请稍后重试或联系技术支持。

[logging]
# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = INFO
# 日志格式
log_format = %%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s
# 日志文件路径
log_file = config/logs/bot.log
# 单个日志文件最大大小 (MB)
max_log_size = 10
# 保留的日志文件数量
backup_count = 5

[data]
# 用户数据文件路径
user_data_file = config/data/users.json
# 消息日志文件路径
message_log_file = config/data/messages.json
"""
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(default_config)
    
    def load_config(self):
        """加载配置文件"""
        config_path = 'config/config.ini'
        self.config.read(config_path, encoding='utf-8')
        
        # 加载配置，如果是默认值则使用占位符
        try:
            self.bot_token = self.config.get('bot', 'bot_token')
            admin_id_str = self.config.get('bot', 'admin_id')
            
            # 如果是默认配置，设置为None或默认值
            if self.bot_token == 'YOUR_BOT_TOKEN_HERE':
                self.bot_token = None
                
            if admin_id_str == 'YOUR_ADMIN_USER_ID_HERE':
                self.admin_id = None
            else:
                try:
                    self.admin_id = int(admin_id_str)
                except ValueError:
                    self.admin_id = None
                    
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            self.bot_token = None
            self.admin_id = None
    
    def setup_logging(self):
        """设置日志系统"""
        try:
            # 创建日志目录
            log_dir = os.path.dirname(self.config.get('logging', 'log_file'))
            os.makedirs(log_dir, exist_ok=True)
            
            # 配置日志
            log_level = getattr(logging, self.config.get('logging', 'log_level'))
            log_format = self.config.get('logging', 'log_format')
            log_file = self.config.get('logging', 'log_file')
            max_size = self.config.getint('logging', 'max_log_size') * 1024 * 1024  # MB to bytes
            backup_count = self.config.getint('logging', 'backup_count')
            
            # 创建logger
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(log_level)
            
            # 清除现有处理器
            self.logger.handlers.clear()
            
            # 创建文件处理器（轮转日志）
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # 创建格式器
            formatter = logging.Formatter(log_format)
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
        except Exception as e:
            print(f"日志系统初始化失败: {e}")
            # 创建一个基本的logger
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
    
    def setup_directories(self):
        """创建必要的目录"""
        data_dir = os.path.dirname(self.config.get('data', 'user_data_file'))
        os.makedirs(data_dir, exist_ok=True)
    
    def load_user_data(self):
        """加载用户数据"""
        user_data_file = self.config.get('data', 'user_data_file')
        try:
            if os.path.exists(user_data_file):
                with open(user_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"加载用户数据失败: {e}")
        return {}
    
    def save_user_data(self, user_data):
        """保存用户数据"""
        user_data_file = self.config.get('data', 'user_data_file')
        try:
            with open(user_data_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存用户数据失败: {e}")
    
    def log_message(self, user_id, username, message_type, content):
        """记录消息日志"""
        message_log_file = self.config.get('data', 'message_log_file')
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'username': username,
            'message_type': message_type,
            'content': content[:100] if len(content) > 100 else content  # 限制长度
        }
        
        try:
            # 读取现有日志
            messages = []
            if os.path.exists(message_log_file):
                with open(message_log_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            
            # 添加新日志
            messages.append(log_entry)
            
            # 保持最近1000条记录
            if len(messages) > 1000:
                messages = messages[-1000:]
            
            # 保存日志
            with open(message_log_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"记录消息日志失败: {e}")
    
    def update_user_info(self, user):
        """更新用户信息"""
        user_data = self.load_user_data()
        user_id = str(user.id)
        
        user_info = {
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language_code': user.language_code,
            'last_seen': datetime.now().isoformat(),
            'message_count': user_data.get(user_id, {}).get('message_count', 0) + 1
        }
        
        user_data[user_id] = user_info
        self.save_user_data(user_data)
        return user_info
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /start 命令"""
        user = update.effective_user
        self.logger.info(f"用户 {user.id} ({user.username}) 使用了 /start 命令")
        
        # 更新用户信息
        self.update_user_info(user)
        
        # 记录消息日志
        self.log_message(user.id, user.username, 'command', '/start')
        
        # 欢迎消息（直接在代码中定义）
        start_message = """🤖 欢迎使用TelegramDock智能客服系统！我是您的专属AI助手，随时为您提供全方位服务支持。

• 🌟 **核心服务功能**：
• 📊 实时查询用户账户信息与状态
• 💬 智能转接专业客服团队
• 🛠️ 提供系统基础服务与技术支持
• 📋 处理常见问题与业务咨询
• 🔍 快速检索相关帮助文档

• 🚀 **快速开始**：
使用下方智能菜单导航或直接输入相关命令，我将立即为您提供精准的个性化服务。无论是技术问题、还是业务咨询，我都能为您提供专业高效的解决方案！

💡 提示：您可以随时输入关键词或描述问题，我会智能识别并提供最佳服务路径。"""
        
        # 创建内联键盘菜单
        keyboard = [
            [InlineKeyboardButton("🆔 查看我的信息", callback_data='get_id')],
            [InlineKeyboardButton("📞 联系客服", callback_data='contact_support')],
            [InlineKeyboardButton("ℹ️ 帮助", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            start_message,
            reply_markup=reply_markup
        )

    async def get_user_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /id 命令"""
        user = update.effective_user
        self.logger.info(f"用户 {user.id} ({user.username}) 使用了 /id 命令")
        
        # 更新用户信息
        user_info = self.update_user_info(user)
        
        # 记录消息日志
        self.log_message(user.id, user.username, 'command', '/id')
        
        username = user.username if user.username else "未设置用户名"
        first_name = user.first_name if user.first_name else "未知"
        last_name = user.last_name if user.last_name else ""
        full_name = f"{first_name} {last_name}".strip()
        
        id_message = f"""
👤 您的用户信息：

🏷️ 用户名：{full_name}
🆔 用户ID：`{user.id}`
🌐 语言：{user.language_code if user.language_code else '未知'}
📊 消息数量：{user_info['message_count']}
⏰ 最后活跃：{user_info['last_seen'][:19]}
"""
        
        await update.message.reply_text(id_message, parse_mode='Markdown')

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理内联键盘回调"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        self.logger.info(f"用户 {user.id} ({user.username}) 点击了按钮: {query.data}")
        
        # 记录消息日志
        self.log_message(user.id, user.username, 'callback', query.data)
        
        if query.data == 'get_id':
            # 更新用户信息
            user_info = self.update_user_info(user)
            
            username = user.username if user.username else "未设置用户名"
            first_name = user.first_name if user.first_name else "未知"
            last_name = user.last_name if user.last_name else ""
            full_name = f"{first_name} {last_name}".strip()
            
            id_message = f"""
👤 您的用户信息：

🏷️ 用户名：{full_name}
🆔 用户ID：`{user.id}`
🌐 语言：{user.language_code if user.language_code else '未知'}
📊 消息数量：{user_info['message_count']}
⏰ 最后活跃：{user_info['last_seen'][:19]}
"""
            await query.edit_message_text(id_message, parse_mode='Markdown')
            
        elif query.data == 'contact_support':
            support_message = """
📞 联系客服

请直接发送您的问题或需求，我们的客服人员会尽快回复您。

您可以发送：
• 文字消息
• 图片
• 文档
• 语音消息

我们会在收到消息后第一时间处理。
"""
            await query.edit_message_text(support_message)
            
        elif query.data == 'help':
            help_message = """
ℹ️ 使用帮助

可用命令：
/start - 显示主菜单
/id - 查看您的用户信息
/menu - 显示菜单

功能说明：
• 发送任何消息都会转发给客服人员
• 客服人员会直接回复您的消息
• 支持发送文字、图片、文档等多种格式

如有问题，请随时联系我们！
"""
            await query.edit_message_text(help_message)

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """显示菜单"""
        user = update.effective_user
        self.logger.info(f"用户 {user.id} ({user.username}) 使用了 /menu 命令")
        
        # 记录消息日志
        self.log_message(user.id, user.username, 'command', '/menu')
        
        keyboard = [
            [InlineKeyboardButton("🆔 查看我的信息", callback_data='get_id')],
            [InlineKeyboardButton("📞 联系客服", callback_data='contact_support')],
            [InlineKeyboardButton("ℹ️ 帮助", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 请选择您需要的服务：",
            reply_markup=reply_markup
        )

    async def forward_to_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """转发用户消息给管理员"""
        user = update.effective_user
        message = update.message
        
        # 更新用户信息
        self.update_user_info(user)
        
        # 记录消息日志
        if message.text:
            message_content = message.text
            message_type = 'text'
        elif message.photo:
            message_content = "[图片]"
            message_type = 'photo'
        elif message.document:
            message_content = f"[文档: {message.document.file_name or '未知文件'}]"
            message_type = 'document'
        elif message.voice:
            message_content = "[语音消息]"
            message_type = 'voice'
        elif message.video:
            message_content = "[视频]"
            message_type = 'video'
        elif message.audio:
            message_content = "[音频]"
            message_type = 'audio'
        elif message.sticker:
            message_content = f"[贴纸: {message.sticker.emoji or ''}]"
            message_type = 'sticker'
        elif message.animation:
            message_content = "[动画]"
            message_type = 'animation'
        else:
            message_content = "[未知消息类型]"
            message_type = 'unknown'
            
        self.log_message(user.id, user.username, message_type, message_content)
        self.logger.info(f"用户 {user.id} ({user.username}) 发送消息: {message_content}")
        
        # 构建转发消息的头部信息
        user_info = f"""
📨 收到用户消息

👤 用户：@{user.username if user.username else '未设置用户名'}
🆔 ID：{user.id}
📝 姓名：{user.first_name} {user.last_name if user.last_name else ''}
⏰ 时间：{message.date.strftime('%Y-%m-%d %H:%M:%S')}

💬 消息内容：
"""
        
        try:
            # 发送用户信息给管理员
            await context.bot.send_message(
                chat_id=self.admin_id,
                text=user_info
            )
            
            # 转发原始消息给管理员
            await message.forward(chat_id=self.admin_id)
            
            # 给用户发送确认消息
            success_message = self.config.get('messages', 'forward_success')
            await message.reply_text(success_message)
            
            self.logger.info(f"已转发用户 {user.id} 的消息给管理员 {self.admin_id}")
            
        except Exception as e:
            self.logger.error(f"转发消息失败: {e}")
            failed_message = self.config.get('messages', 'forward_failed')
            await message.reply_text(failed_message)

    async def handle_admin_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理管理员回复用户的消息"""
        if update.effective_user.id != self.admin_id:
            return
        
        message = update.message
        if not message.text:
            return
            
        # 检查是否是回复用户的格式: @用户ID 消息内容
        if message.text.startswith('@'):
            try:
                parts = message.text.split(' ', 1)
                if len(parts) >= 2:
                    user_id_str = parts[0][1:]  # 移除@符号
                    reply_content = parts[1]
                    target_user_id = int(user_id_str)
                    
                    # 发送消息给目标用户
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=f"📨 客服回复：\n\n{reply_content}"
                    )
                    
                    # 给管理员发送确认
                    await message.reply_text(f"✅ 已回复用户 {target_user_id}")
                    
                    self.logger.info(f"管理员回复用户 {target_user_id}: {reply_content}")
                    
            except (ValueError, IndexError) as e:
                await message.reply_text("❌ 回复格式错误，请使用: @用户ID 消息内容")
                self.logger.error(f"管理员回复格式错误: {e}")
            except Exception as e:
                await message.reply_text(f"❌ 发送失败: {str(e)}")
                self.logger.error(f"管理员回复发送失败: {e}")

    async def handle_no_admin_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理未配置管理员时的消息"""
        user = update.effective_user
        message = update.message
        
        # 更新用户信息
        self.update_user_info(user)
        
        # 记录消息日志
        if message.text:
            message_content = message.text
            message_type = 'text'
        elif message.photo:
            message_content = "[图片]"
            message_type = 'photo'
        elif message.document:
            message_content = f"[文档: {message.document.file_name or '未知文件'}]"
            message_type = 'document'
        elif message.voice:
            message_content = "[语音消息]"
            message_type = 'voice'
        elif message.video:
            message_content = "[视频]"
            message_type = 'video'
        elif message.audio:
            message_content = "[音频]"
            message_type = 'audio'
        elif message.sticker:
            message_content = f"[贴纸: {message.sticker.emoji or ''}]"
            message_type = 'sticker'
        elif message.animation:
            message_content = "[动画]"
            message_type = 'animation'
        else:
            message_content = "[未知消息类型]"
            message_type = 'unknown'
            
        self.log_message(user.id, user.username, message_type, message_content)
        self.logger.info(f"用户 {user.id} ({user.username}) 发送消息: {message_content}")
        
        # 提示用户管理员未配置
        await message.reply_text(
            "📨 您的消息已收到！\n\n"
            "⚠️ 系统提示：管理员联系方式尚未配置，"
            "请联系系统管理员完成配置后重新发送消息。\n\n"
            "感谢您的理解！"
        )

    def run(self):
        """启动机器人"""
        self.logger.info("机器人启动中...")
        
        # 检查配置是否完整
        if not self.bot_token:
            self.logger.error("❌ bot_token 未配置，机器人无法启动")
            self.logger.error("请编辑 config/config.ini 文件，设置正确的 bot_token")
            # 保持运行状态，每30秒检查一次配置
            import time
            while True:
                self.logger.warning("⏳ 等待配置完成... (每30秒检查一次)")
                time.sleep(30)
                # 重新检查配置
                if self.check_and_create_config():
                    self.load_config()
                    if self.bot_token:
                        self.logger.info("✅ 检测到配置更新，重新启动机器人...")
                        break
            
        try:
            # 创建应用
            application = Application.builder().token(self.bot_token).build()
            
            # 添加处理器
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("id", self.get_user_id))
            application.add_handler(CommandHandler("menu", self.show_menu))
            application.add_handler(CallbackQueryHandler(self.handle_callback))
            
            # 管理员消息处理器（仅在admin_id配置时添加）
            if self.admin_id:
                application.add_handler(MessageHandler(
                    filters.TEXT & filters.User(self.admin_id) & ~filters.COMMAND,
                    self.handle_admin_reply
                ))
                
                # 普通用户消息处理器（排除命令和管理员）
                application.add_handler(MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.User(self.admin_id),
                    self.forward_to_admin
                ))
                
                # 处理多媒体消息（仅非管理员用户）
                application.add_handler(MessageHandler(
                    (filters.PHOTO | filters.Document.ALL | filters.VOICE | filters.VIDEO | filters.AUDIO | filters.Sticker.ALL | filters.ANIMATION) & ~filters.COMMAND & ~filters.User(self.admin_id),
                    self.forward_to_admin
                ))
            else:
                self.logger.warning("⚠️  admin_id 未配置，消息转发功能将不可用")
                # 添加通用消息处理器，处理所有类型的消息
                application.add_handler(MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.handle_no_admin_message
                ))
                
                # 添加多媒体消息处理器（图片、文档、语音、视频等）
                application.add_handler(MessageHandler(
                    (filters.PHOTO | filters.Document.ALL | filters.VOICE | filters.VIDEO | filters.AUDIO | filters.Sticker.ALL | filters.ANIMATION) & ~filters.COMMAND,
                    self.handle_no_admin_message
                ))
            
            self.logger.info("机器人已启动，正在监听消息...")
            
            # 启动机器人
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            self.logger.error(f"机器人启动失败: {e}")
            raise

def main():
    """主函数"""
    try:
        bot = TelegramBot()
        # 始终尝试运行机器人，让run方法处理配置问题
        bot.run()
    except Exception as e:
        print(f"启动失败: {e}")
        return 1
    return 0

if __name__ == '__main__':
    exit(main())