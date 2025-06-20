import asyncio
import os
import logging
import base64
import json
from datetime import datetime
from typing import Optional, Dict, Any
from io import BytesIO

import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import redis

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramImageBot:
    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL)
        self.hf_api_base = "https://api-inference.huggingface.co/models"
        self.default_model = "black-forest-labs/FLUX.1-schnell-Free"
        self.max_prompt_length = 500
        self.rate_limit_per_user = 10  # requests per hour
        
        # Available models organized by category
        self.available_models = {
            # Text to Image Models
            "text_to_image": {
                "black-forest-labs/FLUX.1-pro": {
                    "name": "Flux Pro",
                    "description": "Premium quality image generation with superior detail and accuracy",
                    "category": "Premium",
                    "speed": "Slow",
                    "quality": "Highest"
                },
                "black-forest-labs/FLUX.1-dev": {
                    "name": "Flux1.[dev]",
                    "description": "Development version with cutting-edge features and high quality",
                    "category": "Advanced",
                    "speed": "Medium",
                    "quality": "Very High"
                },
                "black-forest-labs/FLUX.1-schnell": {
                    "name": "Flux1.[schnell]",
                    "description": "Fast generation with excellent quality balance",
                    "category": "Balanced",
                    "speed": "Fast",
                    "quality": "High"
                },
                "black-forest-labs/FLUX.1-schnell-Free": {
                    "name": "Flux1.[schnell] Free",
                    "description": "Free tier fast generation with good quality",
                    "category": "Free",
                    "speed": "Fast",
                    "quality": "Good"
                },
                "Kwai-Kolors/Kolors": {
                    "name": "Kolor",
                    "description": "Advanced model with vibrant color reproduction and artistic flair",
                    "category": "Artistic",
                    "speed": "Medium",
                    "quality": "High"
                },
                "stabilityai/stable-diffusion-3-5-large": {
                    "name": "SD 3.5",
                    "description": "Latest Stable Diffusion with improved text understanding",
                    "category": "Latest",
                    "speed": "Medium",
                    "quality": "Very High"
                },
                "runwayml/stable-diffusion-v1-5": {
                    "name": "SD 1.5",
                    "description": "Reliable and fast classic Stable Diffusion model",
                    "category": "Classic",
                    "speed": "Fast",
                    "quality": "Good"
                },
                "stabilityai/stable-diffusion-xl-base-1.0": {
                    "name": "SDXL",
                    "description": "Extra-large model for high-resolution detailed images",
                    "category": "High-Res",
                    "speed": "Slow",
                    "quality": "Very High"
                }
            },
            
            # Text Processing Models
            "text_to_text": {
                "meta-llama/Llama-2-7b-chat-hf": {
                    "name": "Text to Text",
                    "description": "General purpose text processing and conversation",
                    "category": "General",
                    "speed": "Fast",
                    "quality": "High"
                },
                "prompthero/linkedin-job-title-generator": {
                    "name": "Flux Prompt Enhancer",
                    "description": "Enhances and optimizes prompts for better image generation",
                    "category": "Utility",
                    "speed": "Very Fast",
                    "quality": "High"
                },
                "succinctly/text2image-prompt-generator": {
                    "name": "Text to Image Prompt Generator",
                    "description": "Generates detailed prompts from simple descriptions",
                    "category": "Utility",
                    "speed": "Fast",
                    "quality": "High"
                }
            },
            
            # Image Analysis Models
            "image_to_text": {
                "Salesforce/blip-image-captioning-large": {
                    "name": "Image to Text",
                    "description": "Advanced image analysis and description generation",
                    "category": "Analysis",
                    "speed": "Medium",
                    "quality": "High"
                },
                "microsoft/DiT-3D": {
                    "name": "Image Analyzer Pro",
                    "description": "Detailed image analysis with context understanding",
                    "category": "Professional",
                    "speed": "Medium",
                    "quality": "Very High"
                }
            }
        }
        
        # Default models for each category
        self.default_models = {
            "text_to_image": "black-forest-labs/FLUX.1-schnell-Free",
            "text_to_text": "meta-llama/Llama-2-7b-chat-hf",
            "image_to_text": "Salesforce/blip-image-captioning-large"
        }
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command"""
        welcome_message = """
🎨 Welcome to the AI Image Generator Bot!

This bot creates stunning images from your text descriptions using advanced AI models.

**Available Commands:**
/start - Show this welcome message
/help - Get detailed usage instructions
/generate <prompt> - Generate an image from text
/models - View available AI models
/setmodel <model_name> - Set your preferred model
/enhance <prompt> - Enhance your prompt with AI
/settings - Configure your preferences

**Quick Start:**
Simply send me a text description and I'll create an image for you!
You can also send me an image to analyze it!

Example: "A serene mountain landscape at sunset with a crystal clear lake"

Ready to create amazing images? Send me your first prompt! ✨
        """
        
        keyboard = [
            [InlineKeyboardButton("📖 View Help", callback_data='help')],
            [InlineKeyboardButton("🤖 Available Models", callback_data='models')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command"""
        help_text = """
📚 **Detailed Usage Guide**

**Prompt Writing Tips:**
• Be specific and descriptive
• Include style preferences (e.g., "photorealistic", "cartoon", "oil painting")
• Mention colors, lighting, and composition
• Keep prompts under 500 characters for best results

**Example Prompts:**
• "A majestic dragon flying over ancient ruins, fantasy art style"
• "Portrait of a wise old wizard with glowing eyes, digital art"
• "Futuristic cityscape at night with neon lights, cyberpunk style"

**Advanced Features:**
• Use `/setmodel <name>` to set your preferred AI model
• Send `/enhance <prompt>` to improve your prompts with AI
• Send images to get detailed descriptions
• The bot automatically selects optimal models for your prompts
• Images are optimized for Telegram delivery
• Generation typically takes 10-30 seconds

**Rate Limits:**
• Maximum 10 images per hour per user
• This helps ensure fair usage for everyone

Need more help? Just ask me anything! 🤔
        """
        await update.message.reply_text(help_text)
    
    async def models_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /models command"""
        models_text = "🤖 **Available AI Models**\n\n"
        
        # Text to Image Models
        models_text += "🎨 **TEXT TO IMAGE MODELS:**\n"
        for model_id, model_info in self.available_models["text_to_image"].items():
            models_text += f"**{model_info['name']}** ({model_info['category']})\n"
            models_text += f"├ {model_info['description']}\n"
            models_text += f"├ Speed: {model_info['speed']} | Quality: {model_info['quality']}\n"
            models_text += f"└ Command: `/model {model_info['name'].lower().replace(' ', '_')}`\n\n"
        
        # Text Processing Models
        models_text += "📝 **TEXT PROCESSING MODELS:**\n"
        for model_id, model_info in self.available_models["text_to_text"].items():
            models_text += f"**{model_info['name']}** ({model_info['category']})\n"
            models_text += f"├ {model_info['description']}\n"
            models_text += f"└ Command: `/enhance <your_prompt>`\n\n"
        
        # Image Analysis Models
        models_text += "🔍 **IMAGE ANALYSIS MODELS:**\n"
        for model_id, model_info in self.available_models["image_to_text"].items():
            models_text += f"**{model_info['name']}** ({model_info['category']})\n"
            models_text += f"├ {model_info['description']}\n"
            models_text += f"└ Send an image to analyze it\n\n"
        
        models_text += "💡 **Tips:**\n"
        models_text += "• Premium models offer highest quality but slower generation\n"
        models_text += "• Free models are faster and great for quick iterations\n"
        models_text += "• Use `/setmodel <model_name>` to change your default model\n"
        models_text += "• The bot auto-selects the best model if none specified"
        
        # Split message if too long
        if len(models_text) > 4096:
            # Send in chunks
            chunks = [models_text[i:i+4000] for i in range(0, len(models_text), 4000)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(models_text)
    
    def check_rate_limit(self, user_id: int) -> bool:
        """Check if user has exceeded rate limit"""
        key = f"rate_limit:{user_id}"
        current_count = self.redis_client.get(key)
        
        if current_count is None:
            self.redis_client.setex(key, 3600, 1)  # 1 hour TTL
            return True
        
        if int(current_count) >= self.rate_limit_per_user:
            return False
        
        self.redis_client.incr(key)
        return True
    
    def sanitize_prompt(self, prompt: str) -> str:
        """Sanitize and validate the input prompt"""
        # Remove potentially harmful content
        harmful_keywords = ['nsfw', 'explicit', 'nude', 'sexual', 'violent', 'gore']
        
        prompt_lower = prompt.lower()
        for keyword in harmful_keywords:
            if keyword in prompt_lower:
                raise ValueError(f"Content policy violation: {keyword}")
        
        # Trim whitespace and limit length
        prompt = prompt.strip()
        if len(prompt) > self.max_prompt_length:
            prompt = prompt[:self.max_prompt_length].rsplit(' ', 1)[0] + "..."
        
        return prompt
    
    def get_model_by_name(self, model_name: str) -> Optional[str]:
        """Get model ID by name"""
        model_name_lower = model_name.lower().replace(' ', '_').replace('.', '_').replace('[', '').replace(']', '')
        
        # Search through all model categories
        for category in self.available_models.values():
            for model_id, model_info in category.items():
                info_name_lower = model_info['name'].lower().replace(' ', '_').replace('.', '_').replace('[', '').replace(']', '')
                if model_name_lower == info_name_lower or model_name_lower in info_name_lower:
                    return model_id
        return None
    
    def select_optimal_model(self, prompt: str, user_preference: str = None) -> str:
        """Select optimal model based on prompt analysis and user preference"""
        if user_preference:
            model_id = self.get_model_by_name(user_preference)
            if model_id:
                return model_id
        
        # Analyze prompt characteristics
        prompt_lower = prompt.lower()
        
        # High quality/detail requirements
        if any(word in prompt_lower for word in ['detailed', 'high quality', '8k', '4k', 'professional', 'photorealistic']):
            return "black-forest-labs/FLUX.1-pro"
        
        # Artistic/creative prompts
        if any(word in prompt_lower for word in ['artistic', 'painting', 'artwork', 'creative', 'stylized', 'abstract']):
            return "Kwai-Kolors/Kolors"
        
        # Fast generation requests
        if any(word in prompt_lower for word in ['quick', 'fast', 'simple', 'basic']):
            return "black-forest-labs/FLUX.1-schnell-Free"
        
        # Default to balanced option
        return self.default_models["text_to_image"]
    
    def enhance_prompt(self, prompt: str) -> str:
        """Enhance the prompt for better image generation"""
        enhancement_suffixes = [
            "high quality, detailed, professional",
            "8k resolution, sharp focus",
            "beautiful composition, aesthetic"
        ]
        
        # Add quality modifiers if not already present
        if not any(word in prompt.lower() for word in ['quality', 'detailed', 'sharp', '8k']):
            return f"{prompt}, {enhancement_suffixes[0]}"
        
        return prompt
    
    async def enhance_prompt_with_ai(self, prompt: str) -> str:
        """Enhance prompt using AI text-to-text model"""
        model = "succinctly/text2image-prompt-generator"
        url = f"{self.hf_api_base}/{model}"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": f"Enhance this image prompt: {prompt}",
            "parameters": {
                "max_length": 200,
                "temperature": 0.7
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        enhanced = result[0].get('generated_text', prompt)
                        # Clean up the response
                        if enhanced.startswith("Enhance this image prompt:"):
                            enhanced = enhanced.replace("Enhance this image prompt:", "").strip()
                        return enhanced
                return prompt
        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}")
            return self.enhance_prompt(prompt)  # Fallback to simple enhancement
    
    async def generate_image(self, prompt: str, model: str = None) -> Optional[bytes]:
        """Generate image using Hugging Face API"""
        if model is None:
            model = self.default_model
        
        url = f"{self.hf_api_base}/{model}"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    return response.content
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    await asyncio.sleep(10)
                    response = await client.post(url, headers=headers, json=payload)
                    if response.status_code == 200:
                        return response.content
                
                logger.error(f"API error: {response.status_code} - {response.text}")
                return None
                
            except httpx.TimeoutException:
                logger.error("Request timeout while generating image")
                return None
            except Exception as e:
                logger.error(f"Unexpected error during image generation: {e}")
                return None
    
    def process_image(self, image_data: bytes) -> BytesIO:
        """Process and optimize image for Telegram"""
        try:
            # Open and process the image
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            
            # Optimize file size while maintaining quality
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return BytesIO(image_data)
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages as image generation prompts"""
        user_id = update.effective_user.id
        prompt = update.message.text
        
        # Check rate limiting
        if not self.check_rate_limit(user_id):
            await update.message.reply_text(
                "⚠️ Rate limit exceeded. You can generate up to 10 images per hour. "
                "Please try again later."
            )
            return
        
        # Get user's preferred model if set
        user_id = update.effective_user.id
        user_model = self.redis_client.get(f"user_model:{user_id}")
        user_model = user_model.decode('utf-8') if user_model else None
        
        try:
            # Sanitize and enhance the prompt
            sanitized_prompt = self.sanitize_prompt(prompt)
            
            # Select optimal model for this prompt, considering user preference
            selected_model = self.select_optimal_model(sanitized_prompt, user_model)
            
            # Enhance the prompt
            enhanced_prompt = self.enhance_prompt(sanitized_prompt)
            
            # Send processing message with model info
            model_name = next(
                (info['name'] for category in self.available_models.values() 
                 for model_id, info in category.items() if model_id == selected_model),
                selected_model.split('/')[-1]
            )
            
            processing_msg = await update.message.reply_text(
                f"🎨 Generating with **{model_name}**...\n"
                f"📝 Prompt: {sanitized_prompt[:100]}{'...' if len(sanitized_prompt) > 100 else ''}\n"
                f"⏱️ This may take 10-30 seconds."
            )
            
            # Generate the image with selected model
            image_data = await self.generate_image(enhanced_prompt, selected_model)
            
            if image_data:
                # Process and optimize the image
                processed_image = self.process_image(image_data)
                
                # Prepare metadata
                generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                caption = (f"🎨 **Generated Image**\n\n"
                          f"**Prompt:** {sanitized_prompt}\n"
                          f"**Model:** {model_name}\n"
                          f"**Time:** {generation_time}\n"
                          f"**Quality:** {next((info['quality'] for category in self.available_models.values() for model_id, info in category.items() if model_id == selected_model), 'Unknown')}")
                
                # Send the image
                await update.message.reply_photo(
                    photo=processed_image,
                    caption=caption
                )
                
                # Delete processing message
                await processing_msg.delete()
                
                # Log successful generation
                logger.info(f"Image generated for user {user_id}: {sanitized_prompt}")
                
            else:
                await processing_msg.edit_text(
                    "❌ Sorry, I couldn't generate the image. The AI service might be temporarily unavailable. Please try again in a few minutes."
                )
                
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in handle_text_message: {e}")
            await update.message.reply_text(
                "❌ An unexpected error occurred. Please try again later."
            )
    
    async def setmodel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /setmodel command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Please specify a model name.\n"
                "Example: `/setmodel flux_pro`\n"
                "Use `/models` to see available models."
            )
            return
        
        model_name = ' '.join(context.args)
        model_id = self.get_model_by_name(model_name)
        
        if model_id:
            # Store user preference (in production, use database)
            user_id = update.effective_user.id
            self.redis_client.setex(f"user_model:{user_id}", 86400, model_id)  # 24 hours
            
            model_info = next(
                (info for category in self.available_models.values() 
                 for mid, info in category.items() if mid == model_id),
                {"name": model_name, "description": "Custom model"}
            )
            
            await update.message.reply_text(
                f"✅ Default model set to **{model_info['name']}**\n"
                f"📝 {model_info['description']}\n\n"
                f"This preference will be remembered for 24 hours."
            )
        else:
            await update.message.reply_text(
                f"❌ Model '{model_name}' not found.\n"
                f"Use `/models` to see available models."
            )
    
    async def enhance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /enhance command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a prompt to enhance.\n"
                "Example: `/enhance a beautiful sunset`"
            )
            return
        
        original_prompt = ' '.join(context.args)
        
        processing_msg = await update.message.reply_text(
            "🔄 Enhancing your prompt with AI..."
        )
        
        try:
            enhanced_prompt = await self.enhance_prompt_with_ai(original_prompt)
            
            await processing_msg.edit_text(
                f"✨ **Prompt Enhancement**\n\n"
                f"**Original:** {original_prompt}\n\n"
                f"**Enhanced:** {enhanced_prompt}\n\n"
                f"Would you like me to generate an image with the enhanced prompt? "
                f"Just reply 'yes' or send me any message to generate!"
            )
            
            # Store enhanced prompt for potential use
            user_id = update.effective_user.id
            self.redis_client.setex(f"enhanced_prompt:{user_id}", 300, enhanced_prompt)  # 5 minutes
            
        except Exception as e:
            logger.error(f"Error in enhance command: {e}")
            await processing_msg.edit_text(
                "❌ Sorry, I couldn't enhance the prompt right now. "
                "Please try again later."
            )
    
    async def analyze_image(self, image_data: bytes) -> str:
        """Analyze image using image-to-text model"""
        model = self.default_models["image_to_text"]
        url = f"{self.hf_api_base}/{model}"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                files = {"file": ("image.jpg", image_data, "image/jpeg")}
                response = await client.post(url, headers=headers, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get('generated_text', 'Unable to analyze image')
                    return 'Unable to analyze image'
                else:
                    logger.error(f"Image analysis error: {response.status_code}")
                    return 'Unable to analyze image'
                    
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return 'Unable to analyze image'
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages for image analysis"""
        user_id = update.effective_user.id
        
        if not self.check_rate_limit(user_id):
            await update.message.reply_text(
                "⚠️ Rate limit exceeded. Please try again later."
            )
            return
        
        try:
            # Get the photo
            photo = update.message.photo[-1]  # Get highest resolution
            photo_file = await photo.get_file()
            photo_data = await photo_file.download_as_bytearray()
            
            processing_msg = await update.message.reply_text(
                "🔍 Analyzing your image..."
            )
            
            # Analyze the image
            analysis = await self.analyze_image(bytes(photo_data))
            
            await processing_msg.edit_text(
                f"🔍 **Image Analysis**\n\n"
                f"**Description:** {analysis}\n\n"
                f"💡 **Tip:** You can use this description as a prompt to generate similar images!"
            )
            
            # Store analysis for potential prompt use
            self.redis_client.setex(f"image_analysis:{user_id}", 300, analysis)
            
        except Exception as e:
            logger.error(f"Error handling photo: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't analyze the image. Please try again."
            )
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /generate command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a prompt after the command.\n"
                "Example: `/generate A beautiful sunset over mountains`"
            )
            return
        
        prompt = ' '.join(context.args)
        
        # Create a fake message object to reuse the text handler
        update.message.text = prompt
        await self.handle_text_message(update, context)

def main():
    """Start the bot"""
    bot = TelegramImageBot()
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("models", bot.models_command))
    application.add_handler(CommandHandler("generate", bot.generate_command))
    application.add_handler(CommandHandler("setmodel", bot.setmodel_command))
    application.add_handler(CommandHandler("enhance", bot.enhance_command))
    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text_message))
    
    # Start the bot
    logger.info("Starting Telegram Image Generator Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()