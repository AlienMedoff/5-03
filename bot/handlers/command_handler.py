"""
Command Handler for Aether Multi-Agent Bot
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CommandHandler:
    """Handle bot commands"""
    
    def __init__(self):
        self.commands = {
            '/start': self.handle_start,
            '/help': self.handle_help,
            '/status': self.handle_status,
        }
    
    async def handle_command(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command message"""
        try:
            text = message.get('text', '')
            command = text.split()[0].lower()
            
            if command in self.commands:
                return await self.commands[command](message)
            else:
                return await self.handle_unknown(message)
                
        except Exception as e:
            logger.error(f"Error handling command: {e}")
            return {'error': str(e)}
    
    async def handle_start(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /start command"""
        return {
            'text': 'Welcome to Aether Multi-Agent Bot! 🤖\n\nAvailable commands:\n/start - Start bot\n/help - Show help\n/status - Bot status',
            'chat_id': message.get('chat', {}).get('id')
        }
    
    async def handle_help(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /help command"""
        return {
            'text': 'Aether Multi-Agent Bot Help:\n\n/start - Start the bot\n/help - Show this help\n/status - Check bot status\n\nAI Features:\n- Multiple AI models (Claude, Mistral, Groq, Gemini)\n- Smart responses\n- Multi-agent coordination',
            'chat_id': message.get('chat', {}).get('id')
        }
    
    async def handle_status(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /status command"""
        return {
            'text': '🤖 Aether Multi-Agent Bot Status:\n\n✅ Bot is running\n✅ AI models connected\n✅ All systems operational\n\nReady to assist!',
            'chat_id': message.get('chat', {}).get('id')
        }
    
    async def handle_unknown(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown command"""
        return {
            'text': 'Unknown command. Type /help for available commands.',
            'chat_id': message.get('chat', {}).get('id')
        }
