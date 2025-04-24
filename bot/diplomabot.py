import os
import logging
import re
import tempfile
import json
import asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import AsyncOpenAI
from slither import Slither
from slither.detectors import all_detectors
from slither.detectors.abstract_detector import AbstractDetector
from telegram import BotCommand
from telegram import ReplyKeyboardMarkup

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ContractAuditorBot:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.error_docs = self._load_error_documentation()
    
    def _load_error_documentation(self) -> dict:
        """Загружает документацию по ошибкам"""
        default_docs = {
            "reentrancy": {
                "description": "Уязвимость повторного входа позволяет вызывать функцию повторно до завершения предыдущего вызова",
                "solution": "1. Используйте паттерн checks-effects-interactions\n2. Применяйте модификатор nonReentrant",
                "severity": "Высокий",
                "references": [
                    "https://swcregistry.io/docs/SWC-107",
                    "https://solidity-by-example.org/hacks/re-entrancy/"
                ]
            }
        }
        try:
            with open('error_docs.json', 'r', encoding='utf-8') as f:
                return {**default_docs, **json.load(f)}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Error loading error docs: {e}, using defaults")
            return default_docs
    
    def _escape_markdown(self, text: str) -> str:
        """Экранирует специальные символы MarkdownV2"""
        if not text:
            return ""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    
    async def analyze_code(self, code: str) -> dict:
        """Анализирует Solidity код"""
        if not code.strip():
            return {"error": "Получен пустой код"}
        
        # Удаляем строки с лицензиями, чтобы они не мешали анализу
        cleaned_code = "\n".join(
            line for line in code.split("\n") 
            if not line.strip().startswith("// SPDX-License-Identifier:")
        )
        
        results = {"slither": {}, "ai": "", "errors": []}
        tmp_path = None
         
        try:
            # Создаем временный файл для Slither
            with tempfile.NamedTemporaryFile(suffix='.sol', delete=False, mode='w', encoding='utf-8') as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            
            # Анализ Slither с таймаутом
            try:
                slither = await asyncio.wait_for(
                    asyncio.to_thread(Slither, tmp_path),
                    timeout=30
                )
                
                for detector in all_detectors.get_detectors():
                    detector = detector()
                    if isinstance(detector, AbstractDetector):
                        issues = await asyncio.to_thread(detector.detect, slither)
                        if issues:
                            detector_name = detector.ARGUMENT
                            results["slither"][detector_name] = issues
                            for issue in issues:
                                if detector_name in self.error_docs:
                                    issue["documentation"] = self.error_docs[detector_name]
                                results["errors"].append(issue)
            except asyncio.TimeoutError:
                results["slither"]["error"] = "Анализ Slither превысил время ожидания (30s)"
            except Exception as e:
                    logger.error(f"Ошибка запуска Slither: {e}")
                    results["slither"]["error"] = f"Ошибка Slither: {str(e)}"
            
            # Анализ AI с таймаутом
            try:
                results["ai"] = await asyncio.wait_for(
                    self._analyze_with_ai(code),
                    timeout=45
                )
            except asyncio.TimeoutError:
                results["ai"] = "Анализ ИИ превысил время ожидания (45s)"
            except Exception as e:
                results["ai"] = f"Ошибка ИИ анализа: {str(e)}"
                
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            results["error"] = f"Системная ошибка: {str(e)}"
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception as e:
                    logger.warning(f"Error deleting temp file: {e}")
        
        return results
    
    async def _analyze_with_ai(self, code: str) -> str:
        """Анализ кода с помощью OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по безопасности смарт-контрактов. Анализируй код на Solidity и выявляй уязвимости. Отвечай на русском."
                    },
                    {
                        "role": "user",
                        "content": f"""Проанализируй этот Solidity код:
1. Найди все уязвимости
2. Для каждой уязвимости укажи:
   - Местоположение (строка/функция)
   - Тип уязвимости
   - Уровень опасности (Низкий/Средний/Высокий)
   - Подробное описание
   - Способы исправления
   - Ссылки на документацию

Код:
```solidity
{code}
```"""
                    }
                ],
                temperature=0.3,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise

    def format_report(self, results: dict) -> str:
        """Формирует отчет"""
        if "error" in results:
            return f"⚠️ Ошибка: {results['error']}"
        
        report = []
        
        # Заголовок
        report.append(self._escape_markdown("🔍 *Результаты аудита* 🔍\n\n"))
        
        # Ошибки Slither
        if "error" in results.get("slither", {}):
            report.append(f"❌ *Slither:* {self._escape_markdown(results['slither']['error'])}\n\n")
        
        # Найденные уязвимости
        if results.get("slither"):
            report.append(self._escape_markdown("⚙️ *Статический анализ (Slither):*\n"))
            
            for detector, issues in results["slither"].items():
                if detector == "error":
                    continue
                
                detector_name = detector.replace("-", " ").title()
                report.append(f"\n🔴 *{self._escape_markdown(detector_name)}:*\n")
                
                for issue in issues:
                    # Основное описание
                    desc = issue.get("description", "Описание недоступно")
                    report.append(f"• {self._escape_markdown(desc)}\n")
                    
                    # Дополнительная информация
                    if "impact" in issue:
                        report.append(f"  ⚠️ *Уровень:* {self._escape_markdown(issue['impact'])}\n")
                    
                    if "documentation" in issue:
                        doc = issue["documentation"]
                        if "solution" in doc:
                            report.append(f"  🛠 *Решение:* {self._escape_markdown(doc['solution'])}\n")
                        if "references" in doc and doc["references"]:
                            report.append("  📚 *Ссылки:*\n")
                            for ref in doc["references"]:
                                report.append(f"    - {self._escape_markdown(ref)}\n")
        
        # Анализ ИИ
        if results.get("ai"):
            report.append("\n🤖 *Углубленный анализ ИИ:*\n")
            report.append(self._escape_markdown(results["ai"]))
        
        return "".join(report)


async def send_long_message(update: Update, text: str):
    """Отправляет длинное сообщение с разбивкой на части"""
    MAX_LENGTH = 4096
    parts = []
    
    # Разбиваем текст по строкам
    lines = text.split('\n')
    current_part = []
    current_length = 0
    
    for line in lines:
        line_length = len(line) + 1  # +1 для символа переноса строки
        
        if current_length + line_length > MAX_LENGTH:
            parts.append('\n'.join(current_part))
            current_part = []
            current_length = 0
        
        current_part.append(line)
        current_length += line_length
    
    if current_part:
        parts.append('\n'.join(current_part))
    
    # Отправляем части
    for part in parts:
        try:
            await update.message.reply_text(
                part,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.warning(f"Markdown error, sending as plain text: {e}")
            try:
                await update.message.reply_text(
                    part,
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"Failed to send message: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команд /start и /help"""
    help_text = """
🤖 *Smart Contract Auditor Bot* 🤖

Я помогаю находить уязвимости в Solidity смарт-контрактах с помощью:
- Статического анализа (Slither)
- ИИ анализа (GPT-4)

*Как использовать:*
1. Отправьте файл `.sol` с контрактом
2. Или вставьте код прямо в сообщение (должен содержать `pragma` или `contract`)

*Примеры команд:*
/start - показать это сообщение
/sample - получить пример контракта для теста
/help - справка по использованию

*Что я проверяю:*
- Reentrancy (повторный вход)
- Небезопасные вызовы
- Ошибки доступа
- Проблемы с gas
- И многое другое...

Отправьте мне Solidity код для анализа!
"""
    await send_long_message(update, help_text)


async def send_sample(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет пример контракта"""
    sample_code = """
// Пример уязвимого контракта
pragma solidity ^0.8.0;

contract Vulnerable {
    mapping(address => uint) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    // Уязвимая функция вывода
    function withdraw() public {
        uint amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] = 0;
    }
}
"""
    await update.message.reply_text(
        f"Пример контракта для теста:\n```solidity\n{sample_code}\n```",
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений с кодом"""
    text = update.message.text.strip()
    
    # Пропускаем команды
    if text.startswith('/'):
        return
    
    # Проверяем, похоже ли на Solidity код
    if not (re.search(r'\bpragma\s+solidity\b', text, re.I) or 
            re.search(r'\bcontract\s+\w+', text, re.I)):
        await update.message.reply_text(
            "Это не похоже на Solidity код. Отправьте:\n"
            "1. Файл .sol\n"
            "2. Или код, содержащий 'pragma solidity' или 'contract'"
        )
        return
    
    await update.message.reply_text("🔍 Анализирую код... Подождите...")
    
    try:
        bot = context.bot_data.get('auditor')
        if not bot:
            await update.message.reply_text("⚠️ Ошибка: Аудитор не инициализирован.")
            return
        analysis_task = asyncio.create_task(bot.analyze_code(text))
        
        # Отправляем "ожидайте" сообщение
        wait_msg = await update.message.reply_text("⏳ Анализ может занять до 1 минуты...")
        
        results = await analysis_task
        report = bot.format_report(results)
        
        # Удаляем сообщение "ожидайте"
        try:
            await context.bot.delete_message(
                chat_id=update.message.chat_id,
                message_id=wait_msg.message_id
            )
        except Exception as e:
            logger.warning(f"Could not delete wait message: {e}")
        
        await send_long_message(update, report)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        await update.message.reply_text(f"⚠️ Ошибка анализа: {e}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик документов .sol"""
    doc = update.message.document
    
    if not doc.file_name.lower().endswith('.sol'):
        await update.message.reply_text("Пожалуйста, отправьте файл с расширением .sol")
        return
    
    await update.message.reply_text("📥 Загружаю файл...")
    
    temp_path = None
    try:
        # Скачиваем файл
        with tempfile.NamedTemporaryFile(suffix='.sol', delete=False, mode='w', encoding='utf-8') as tmp:
            temp_path = tmp.name
            file = await context.bot.get_file(doc.file_id)
            await file.download_to_drive(temp_path)
            
            # Читаем содержимое
            with open(temp_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            if not code.strip():
                raise ValueError("Файл пустой")
            
            await update.message.reply_text("🔍 Анализирую контракт...")
            
            bot = context.bot_data['auditor']
            results = await bot.analyze_code(code)
            report = bot.format_report(results)
            
            await send_long_message(update, report)
            
    except Exception as e:
        logger.error(f"Document processing failed: {e}", exc_info=True)
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Error deleting temp file: {e}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error("Exception:", exc_info=context.error)
    
    if update and isinstance(update, Update):
        try:
            await update.message.reply_text(
                "⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.\n"
                "Если ошибка повторяется, сообщите разработчику."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

async def set_bot_commands(application):
    """Устанавливает команды для меню Telegram"""
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Помощь"),
        BotCommand("sample", "Пример контракта"),
    ]
    await application.bot.set_my_commands(commands)

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Отправляет приветственное сообщение с кнопками"""
#     keyboard = [
#         ["/start", "/help"],
#         ["/sample"]
#     ]
#     reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

#     text = "👋 Привет! Отправьте мне Solidity-код или загрузите `.sol` файл для анализа."
#     await update.message.reply_text(text, reply_markup=reply_markup)

#async 
def main():
    """Запуск бота"""
    try:
        # Инициализация бота
        application = Application.builder() \
            .token("8145897663:AAF2loUtu7emb0WbUNTyURGbrtOk0mrglsg") \
            .build()
        
        # Инициализация аудитора
        openai_key = os.getenv("OPENAI_API_KEY", "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")
        application.bot_data['auditor'] = ContractAuditorBot(openai_key)
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", start))
        application.add_handler(CommandHandler("sample", send_sample))
        application.add_handler(MessageHandler(filters.ALL, handle_text))
        application.add_handler(MessageHandler(filters.Document.FileExtension("sol"), handle_document))
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)

        #await set_bot_commands(application)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", start))
        application.add_handler(CommandHandler("sample", send_sample))

        
        # Запуск
        logger.info("Starting bot...")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Bot crashed: {e}", exc_info=True)
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    main()
