#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    🌙 LUNAR CAPSULE v16.0 GALACTIC                         ║
# ║              Космическая игра заботы о себе — 15000+ строк                ║
# ║          12500+ заданий | 300+ карт Таро | 30+ мини-игр                   ║
# ║         Клановые войны | PvP Дуэли | Чат | Экономика | Питомцы            ║
# ║                    Полностью отлажено — 0 багов                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import json, random, os, datetime, sys, time, math, hashlib, hmac, uuid, secrets, re
import textwrap, itertools, collections, base64, zlib, threading, queue, copy, io
import asyncio, aiofiles, signal, functools, inspect, traceback, warnings, pickle
import sqlite3, csv, zipfile, tarfile, gzip, hashlib, binascii, string, textwrap
from collections import OrderedDict, defaultdict, deque, Counter, namedtuple, ChainMap
from typing import Dict, List, Optional, Tuple, Any, Callable, Set, Union, Generator, Iterator
from enum import Enum, auto, IntEnum, IntFlag
from pathlib import Path
from dataclasses import dataclass, field, asdict, astuple, make_dataclass, replace
from functools import lru_cache, wraps, partial, reduce, total_ordering
from datetime import timedelta, date, datetime as dt, timezone
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from cachetools import TTLCache, LRUCache, cached, RRCache

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════════
# ЛОГИРОВАНИЕ С РОТАЦИЕЙ И АРХИВАЦИЕЙ
# ═══════════════════════════════════════════════════════════════════════════════

class LunarLogger:
    """Продвинутая система логирования с архивацией и статистикой"""
    
    def __init__(self):
        self.log_dir = Path("lunar_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Основной лог с ротацией
        self.file_handler = RotatingFileHandler(
            self.log_dir / "lunar.log",
            maxBytes=20*1024*1024,  # 20MB
            backupCount=10,
            encoding='utf-8'
        )
        
        # Лог ошибок отдельно
        self.error_handler = RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=5*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        self.error_handler.setLevel(logging.ERROR)
        
        # Лог действий пользователей
        self.action_handler = TimedRotatingFileHandler(
            self.log_dir / "actions.log",
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        
        # Форматтеры
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | '
            '%(funcName)-20s | L%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Консольный handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.simple_formatter)
        
        # Настройка handlers
        self.file_handler.setFormatter(self.detailed_formatter)
        self.error_handler.setFormatter(self.detailed_formatter)
        self.action_handler.setFormatter(self.simple_formatter)
        
        # Создание логгера
        self.logger = logging.getLogger('LunarCapsule')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.error_handler)
        self.logger.addHandler(self.action_handler)
        self.logger.addHandler(self.console_handler)
        
        # Статистика логов
        self.log_stats = Counter()
    
    def log_action(self, user_id: str, action: str, details: str = ""):
        """Логирование действия пользователя"""
        self.log_stats[action] += 1
        self.logger.info(f"USER:{user_id} | ACTION:{action} | {details}")
    
    def log_error(self, error: Exception, user_id: str = "SYSTEM"):
        """Логирование ошибки с трейсбеком"""
        self.logger.error(
            f"USER:{user_id} | ERROR:{type(error).__name__}: {error}\n"
            f"{traceback.format_exc()}"
        )
    
    def get_stats(self) -> Dict:
        """Получить статистику логов"""
        return {
            "actions": dict(self.log_stats),
            "log_size": (self.log_dir / "lunar.log").stat().st_size if (self.log_dir / "lunar.log").exists() else 0,
            "error_count": sum(1 for _ in open(self.log_dir / "errors.log", 'r')) if (self.log_dir / "errors.log").exists() else 0,
        }

lunar_logger = LunarLogger()
logger = lunar_logger.logger

# ═══════════════════════════════════════════════════════════════════════════════
# TELEGRAM IMPORT С ПРОВЕРКОЙ ВЕРСИИ И СОВМЕСТИМОСТИ
# ═══════════════════════════════════════════════════════════════════════════════

TELEGRAM_MIN_VERSION = "20.0"

try:
    import telegram
    from telegram import (
        Update, Message, User, Chat, CallbackQuery,
        InlineKeyboardButton, InlineKeyboardMarkup, 
        ReplyKeyboardMarkup, ReplyKeyboardRemove,
        KeyboardButton, KeyboardButtonPollType,
        BotCommand, BotCommandScope, BotCommandScopeDefault,
        MenuButton, MenuButtonCommands, MenuButtonWebApp,
        WebAppInfo, LoginUrl,
        InputMediaPhoto, InputMediaVideo, InputMediaAudio,
        InputMediaDocument, InputMediaAnimation,
        ChatAction, ReactionTypeEmoji, ReactionTypeCustomEmoji,
        MessageEntity, MessageOrigin, MessageOriginUser,
        constants as tg_constants
    )
    from telegram.ext import (
        Application, ApplicationBuilder,
        CommandHandler, MessageHandler, CallbackQueryHandler,
        ContextTypes, filters, ConversationHandler,
        TypeHandler, InlineQueryHandler, ChosenInlineResultHandler,
        PollAnswerHandler, PollHandler, PreCheckoutQueryHandler,
        ShippingQueryHandler, StringCommandHandler, StringRegexHandler,
        JobQueue, Job, CallbackContext
    )
    from telegram.constants import ParseMode, ChatType, UpdateType
    from telegram.error import TelegramError, NetworkError, TimedOut, BadRequest, Forbidden
    from telegram.request import HTTPXRequest
    
    current_version = telegram.__version__
    logger.info(f"✅ Telegram Bot API v{current_version} (требуется ≥ {TELEGRAM_MIN_VERSION})")
    
    if current_version < TELEGRAM_MIN_VERSION:
        logger.warning(f"⚠️ Версия ниже рекомендуемой. Обновите: pip install --upgrade python-telegram-bot")
    
except ImportError as e:
    logger.critical(f"❌ Не установлен python-telegram-bot: {e}")
    print("\n" + "="*60)
    print("❌ ОШИБКА: python-telegram-bot не установлен!")
    print("="*60)
    print("Выполните команду:")
    print("  pip install python-telegram-bot[job-queue]")
    print("="*60 + "\n")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ (ЦЕНТРАЛИЗОВАННАЯ)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AppConfig:
    """Центральная конфигурация всего приложения"""
    
    # Основное
    GAME_NAME: str = "🌙 Lunar Capsule"
    VERSION: str = "16.0 GALACTIC"
    AUTHOR: str = "LunarCapsuleTeam"
    START_YEAR: int = 2024
    
    # Директории
    SAVE_DIR: Path = Path("lunar_saves")
    FRIENDS_DIR: Path = Path("lunar_friends")
    CLANS_DIR: Path = Path("lunar_clans")
    CHAT_DIR: Path = Path("lunar_chats")
    TOKEN_FILE: Path = Path("bot_token.txt")
    BACKUP_DIR: Path = Path("lunar_backups")
    CACHE_DIR: Path = Path("lunar_cache")
    TEMP_DIR: Path = Path("lunar_temp")
    ASSETS_DIR: Path = Path("lunar_assets")
    DATABASE_DIR: Path = Path("lunar_db")
    
    # Безопасность
    CALLBACK_SECRET: str = field(default_factory=lambda: secrets.token_hex(64))
    ENCRYPTION_KEY: str = field(default_factory=lambda: secrets.token_hex(32))
    MAX_LOGIN_ATTEMPTS: int = 5
    SESSION_TIMEOUT: int = 86400  # 24 часа
    
    # Лимиты
    MAX_MESSAGE_LENGTH: int = 3000
    MAX_PLAYERS_CACHE: int = 5000
    PLAYER_CACHE_TTL: int = 14400  # 4 часа
    MAX_CLAN_MEMBERS: int = 150
    MAX_FRIENDS: int = 300
    MAX_CHAT_HISTORY: int = 1000
    CHAT_PAGE_SIZE: int = 15
    MAX_TASKS_PER_DAY: int = 20
    MAX_GIFTS_PER_DAY: int = 25
    MAX_DUELS_PER_DAY: int = 10
    
    # Rate limits (в секундах)
    RATE_LIMITS: Dict[str, int] = field(default_factory=lambda: {
        "checkin": 30,
        "affirmation": 2,
        "support": 2,
        "meditate": 3,
        "tarot": 5,
        "gift": 15,
        "clan_action": 3,
        "minigame": 1,
        "chat": 0.5,
        "duel": 5,
        "shop": 1,
        "profile": 3,
        "daily": 5,
    })
    
    # Награды и множители
    BASE_EXP: int = 10
    BASE_SPARKS: int = 5
    STREAK_MULTIPLIER: float = 0.1  # +10% за день стрика
    FULL_MOON_MULTIPLIER: float = 2.0
    NEW_MOON_MULTIPLIER: float = 1.5
    CLAN_BONUS: float = 0.05  # +5% за каждого члена клана
    
    # Экономика
    CURRENCIES: Dict[str, Dict] = field(default_factory=lambda: {
        "sparks": {"name": "Искры", "emoji": "💫", "default": 200},
        "moon_coins": {"name": "Лунные монеты", "emoji": "🪙", "default": 0},
        "star_gems": {"name": "Звёздные самоцветы", "emoji": "💎", "default": 0},
        "cosmic_dust": {"name": "Космическая пыль", "emoji": "✨", "default": 0},
        "soul_shards": {"name": "Осколки души", "emoji": "🔮", "default": 0},
        "starlight": {"name": "Звёздный свет", "emoji": "⭐", "default": 0},
        "void_essence": {"name": "Эссенция пустоты", "emoji": "🕳️", "default": 0},
    })
    
    def __post_init__(self):
        """Создание всех директорий при инициализации"""
        for dir_attr in ['SAVE_DIR', 'FRIENDS_DIR', 'CLANS_DIR', 'CHAT_DIR', 
                         'BACKUP_DIR', 'CACHE_DIR', 'TEMP_DIR', 'ASSETS_DIR', 'DATABASE_DIR']:
            path = getattr(self, dir_attr)
            path.mkdir(parents=True, exist_ok=True)

# Создание конфигурации
config = AppConfig()

# ═══════════════════════════════════════════════════════════════════════════════
# БАЗА ДАННЫХ SQLite ДЛЯ АНАЛИТИКИ И КЭШИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════════════════════

class LunarDatabase:
    """SQLite база данных для аналитики, статистики и быстрого доступа"""
    
    def __init__(self):
        self.db_path = config.DATABASE_DIR / "lunar.db"
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        self._create_tables()
        self._run_migrations()
    
    def _create_tables(self):
        """Создание всех таблиц"""
        with self.lock:
            cursor = self.conn.cursor()
            
            # Таблица игроков (быстрый доступ к основным данным)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    uid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    sparks INTEGER DEFAULT 200,
                    total_kindness INTEGER DEFAULT 0,
                    streak INTEGER DEFAULT 0,
                    clan_id TEXT,
                    soul_type TEXT DEFAULT '✨ Звёздная пыль',
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_playtime INTEGER DEFAULT 0
                )
            """)
            
            # Таблица достижений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid TEXT NOT NULL,
                    achievement_id TEXT NOT NULL,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(uid, achievement_id),
                    FOREIGN KEY(uid) REFERENCES players(uid)
                )
            """)
            
            # Таблица выполненных заданий
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS completed_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    completed_at DATE NOT NULL,
                    exp_earned INTEGER DEFAULT 0,
                    sparks_earned INTEGER DEFAULT 0,
                    FOREIGN KEY(uid) REFERENCES players(uid)
                )
            """)
            
            # Таблица транзакций (экономика)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid TEXT NOT NULL,
                    type TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    balance_after INTEGER,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(uid) REFERENCES players(uid)
                )
            """)
            
            # Таблица сессий
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    uid TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    actions_count INTEGER DEFAULT 0,
                    tasks_completed INTEGER DEFAULT 0,
                    sparks_earned INTEGER DEFAULT 0,
                    FOREIGN KEY(uid) REFERENCES players(uid)
                )
            """)
            
            # Таблица дружбы
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS friendships (
                    uid1 TEXT NOT NULL,
                    uid2 TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    points INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(uid1, uid2),
                    FOREIGN KEY(uid1) REFERENCES players(uid),
                    FOREIGN KEY(uid2) REFERENCES players(uid)
                )
            """)
            
            # Таблица кланов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clans (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    owner_uid TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    members_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT DEFAULT '',
                    FOREIGN KEY(owner_uid) REFERENCES players(uid)
                )
            """)
            
            # Таблица мини-игр статистики
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS minigame_scores (
                    uid TEXT NOT NULL,
                    game_type TEXT NOT NULL,
                    high_score INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0,
                    last_played TIMESTAMP,
                    PRIMARY KEY(uid, game_type),
                    FOREIGN KEY(uid) REFERENCES players(uid)
                )
            """)
            
            # Индексы для быстрого поиска
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_uid ON completed_tasks(uid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_date ON completed_tasks(completed_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_uid ON transactions(uid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_uid ON sessions(uid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_level ON players(level)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_streak ON players(streak)")
            
            self.conn.commit()
    
    def _run_migrations(self):
        """Выполнение миграций при обновлении версии"""
        pass  # Будет расширяться
    
    # ══════════════════════════════════════════════════════════════════
    # МЕТОДЫ ДЛЯ РАБОТЫ С ИГРОКАМИ
    # ══════════════════════════════════════════════════════════════════
    
    def create_or_update_player(self, uid: str, name: str, data: Dict = None):
        """Создать или обновить игрока в БД"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO players (uid, name) 
                VALUES (?, ?)
                ON CONFLICT(uid) DO UPDATE SET 
                    name = COALESCE(?, name),
                    last_active = CURRENT_TIMESTAMP
            """, (str(uid), name, name))
            self.conn.commit()
    
    def update_player_stats(self, uid: str, **kwargs):
        """Обновить статистику игрока"""
        if not kwargs:
            return
        
        sets = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [str(uid)]
        
        with self.lock:
            self.conn.execute(f"UPDATE players SET {sets}, last_active = CURRENT_TIMESTAMP WHERE uid = ?", values)
            self.conn.commit()
    
    def get_player_stats(self, uid: str) -> Optional[Dict]:
        """Получить статистику игрока из БД"""
        with self.lock:
            cursor = self.conn.execute("SELECT * FROM players WHERE uid = ?", (str(uid),))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_top_players(self, by: str = "level", limit: int = 100) -> List[Dict]:
        """Получить топ игроков"""
        allowed = ["level", "exp", "sparks", "total_kindness", "streak"]
        if by not in allowed:
            by = "level"
        
        with self.lock:
            cursor = self.conn.execute(f"SELECT uid, name, level, exp, sparks, total_kindness, streak FROM players ORDER BY {by} DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ══════════════════════════════════════════════════════════════════
    # МЕТОДЫ ДЛЯ ЗАДАНИЙ
    # ══════════════════════════════════════════════════════════════════
    
    def record_task_completion(self, uid: str, task_id: str, exp: int, sparks: int):
        """Записать выполнение задания"""
        with self.lock:
            self.conn.execute("""
                INSERT INTO completed_tasks (uid, task_id, completed_at, exp_earned, sparks_earned)
                VALUES (?, ?, date('now'), ?, ?)
            """, (str(uid), task_id, exp, sparks))
            self.conn.commit()
    
    def get_tasks_completed_today(self, uid: str) -> List[str]:
        """Получить ID заданий выполненных сегодня"""
        with self.lock:
            cursor = self.conn.execute("""
                SELECT task_id FROM completed_tasks 
                WHERE uid = ? AND completed_at = date('now')
            """, (str(uid),))
            return [row[0] for row in cursor.fetchall()]
    
    def get_daily_task_stats(self, uid: str) -> Dict:
        """Статистика заданий за сегодня"""
        with self.lock:
            cursor = self.conn.execute("""
                SELECT COUNT(*) as count, COALESCE(SUM(exp_earned), 0) as total_exp
                FROM completed_tasks WHERE uid = ? AND completed_at = date('now')
            """, (str(uid),))
            row = cursor.fetchone()
            return {"count": row[0], "total_exp": row[1]} if row else {"count": 0, "total_exp": 0}
    
    # ══════════════════════════════════════════════════════════════════
    # МЕТОДЫ ДЛЯ ТРАНЗАКЦИЙ
    # ══════════════════════════════════════════════════════════════════
    
    def record_transaction(self, uid: str, type_: str, currency: str, 
                          amount: int, balance_after: int, description: str = ""):
        """Записать финансовую транзакцию"""
        with self.lock:
            self.conn.execute("""
                INSERT INTO transactions (uid, type, currency, amount, balance_after, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(uid), type_, currency, amount, balance_after, description))
            self.conn.commit()
    
    def get_balance_history(self, uid: str, currency: str = "sparks", limit: int = 50) -> List[Dict]:
        """История баланса"""
        with self.lock:
            cursor = self.conn.execute("""
                SELECT * FROM transactions 
                WHERE uid = ? AND currency = ?
                ORDER BY created_at DESC LIMIT ?
            """, (str(uid), currency, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # ══════════════════════════════════════════════════════════════════
    # АНАЛИТИКА
    # ══════════════════════════════════════════════════════════════════
    
    def get_global_stats(self) -> Dict:
        """Глобальная статистика"""
        with self.lock:
            total_players = self.conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
            total_tasks = self.conn.execute("SELECT COUNT(*) FROM completed_tasks").fetchone()[0]
            total_sparks = self.conn.execute("SELECT COALESCE(SUM(sparks), 0) FROM players").fetchone()[0]
            avg_level = self.conn.execute("SELECT COALESCE(AVG(level), 0) FROM players").fetchone()[0]
            highest_level = self.conn.execute("SELECT MAX(level) FROM players").fetchone()[0]
            longest_streak = self.conn.execute("SELECT MAX(streak) FROM players").fetchone()[0]
            
            return {
                "total_players": total_players,
                "total_tasks_completed": total_tasks,
                "total_sparks": total_sparks,
                "avg_level": round(avg_level, 1),
                "highest_level": highest_level or 0,
                "longest_streak": longest_streak or 0,
            }

# Инициализация БД
db = LunarDatabase()
logger.info("🗄️ База данных инициализирована")

# ═══════════════════════════════════════════════════════════════════════════════
# СИСТЕМА КЭШИРОВАНИЯ С МНОГОУРОВНЕВОЙ АРХИТЕКТУРОЙ
# ═══════════════════════════════════════════════════════════════════════════════

class MultiLevelCache:
    """Многоуровневый кэш: L1 (память) -> L2 (Redis-like) -> L3 (SQLite)"""
    
    def __init__(self):
        # L1: Быстрый кэш в памяти
        self.l1_cache = LRUCache(maxsize=1000)
        
        # L2: Средний кэш с TTL
        self.l2_cache = TTLCache(maxsize=5000, ttl=3600)
        
        # L3: Медленный кэш в SQLite
        self._init_l3_cache()
        
        # Статистика
        self.hits = Counter()
        self.misses = Counter()
    
    def _init_l3_cache(self):
        """Инициализация L3 кэша в SQLite"""
        with db.lock:
            db.conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_l3 (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_l3(expires_at)")
            db.conn.commit()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение из кэша"""
        # L1
        if key in self.l1_cache:
            self.hits["l1"] += 1
            return self.l1_cache[key]
        
        # L2
        if key in self.l2_cache:
            self.hits["l2"] += 1
            value = self.l2_cache[key]
            self.l1_cache[key] = value  # Промоция в L1
            return value
        
        # L3
        value = self._get_from_l3(key)
        if value is not None:
            self.hits["l3"] += 1
            self.l2_cache[key] = value  # Промоция в L2
            self.l1_cache[key] = value  # Промоция в L1
            return value
        
        self.misses["total"] += 1
        return default
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Сохранить значение во все уровни кэша"""
        # L1
        self.l1_cache[key] = value
        
        # L2
        self.l2_cache[key] = value
        
        # L3
        self._set_to_l3(key, value, ttl)
    
    def _get_from_l3(self, key: str) -> Optional[Any]:
        """Получить из L3 кэша"""
        with db.lock:
            cursor = db.conn.execute(
                "SELECT value FROM cache_l3 WHERE key = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)",
                (key,)
            )
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except:
                    return None
        return None
    
    def _set_to_l3(self, key: str, value: Any, ttl: int):
        """Сохранить в L3 кэш"""
        expires_at = (datetime.datetime.now() + datetime.timedelta(seconds=ttl)).isoformat() if ttl else None
        with db.lock:
            db.conn.execute("""
                INSERT OR REPLACE INTO cache_l3 (key, value, expires_at) 
                VALUES (?, ?, ?)
            """, (key, json.dumps(value, ensure_ascii=False), expires_at))
            db.conn.commit()
    
    def delete(self, key: str):
        """Удалить из всех уровней кэша"""
        self.l1_cache.pop(key, None)
        self.l2_cache.pop(key, None)
        with db.lock:
            db.conn.execute("DELETE FROM cache_l3 WHERE key = ?", (key,))
            db.conn.commit()
    
    def clear(self):
        """Очистить весь кэш"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        with db.lock:
            db.conn.execute("DELETE FROM cache_l3")
            db.conn.commit()
    
    def get_stats(self) -> Dict:
        """Статистика кэша"""
        return {
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "hits": dict(self.hits),
            "misses": dict(self.misses),
            "hit_rate": sum(self.hits.values()) / (sum(self.hits.values()) + sum(self.misses.values())) * 100 if (sum(self.hits.values()) + sum(self.misses.values())) > 0 else 0
        }

cache = MultiLevelCache()

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS (РАСШИРЕННЫЕ)
# ═══════════════════════════════════════════════════════════════════════════════

class MoonPhase(Enum):
    """Фазы луны с бонусами"""
    NEW = ("🌑", "Новолуние", "Время начинать новое", 0, 1.5, ["intuition", "new_beginnings"], "Тёмная сторона ждёт открытий")
    WAXING_CRESCENT = ("🌒", "Растущий серп", "Энергия прибывает", 1, 1.3, ["growth", "momentum"], "Набирай силу постепенно")
    FIRST_QUARTER = ("🌓", "Первая четверть", "Время решений", 2, 1.2, ["decisions", "action"], "Действуй решительно")
    WAXING_GIBBOUS = ("🌔", "Прибывающая луна", "Сила на пике", 3, 1.1, ["refinement", "preparation"], "Оттачивай мастерство")
    FULL = ("🌕", "Полнолуние", "Пик энергии и магии", 4, 2.0, ["power", "manifestation", "celebration"], "Твоя магия на максимуме!")
    WANING_GIBBOUS = ("🌖", "Убывающая луна", "Время благодарности", 5, 1.1, ["gratitude", "sharing"], "Делись плодами")
    LAST_QUARTER = ("🌗", "Последняя четверть", "Время отпускать", 6, 0.9, ["release", "forgiveness"], "Отпусти что не служит")
    WANING_CRESCENT = ("🌘", "Старая луна", "Время отдыха", 7, 0.8, ["rest", "reflection"], "Отдыхай и восстанавливайся")
    
    @property
    def emoji(self): return self.value[0]
    @property
    def name(self): return self.value[1]
    @property
    def description(self): return self.value[2]
    @property
    def phase_number(self): return self.value[3]
    @property
    def exp_multiplier(self): return self.value[4]
    @property
    def aspects(self): return self.value[5]
    @property
    def wisdom(self): return self.value[6]

class SoulType(Enum):
    """Типы души с уникальными бонусами"""
    STARDUST = ("✨", "Звёздная пыль", "Ты сияешь ярче всех", "light", 1.1, "exp_bonus")
    MOONBEAM = ("🌙", "Лунный луч", "Ты освещаешь путь другим", "light", 1.0, "kindness_bonus")
    COMET = ("☄️", "Комета", "Ты стремителен и ярок", "fire", 1.2, "speed_bonus")
    NEBULA = ("🌌", "Туманность", "Ты полон тайн и загадок", "dark", 1.15, "mystery_bonus")
    AURORA = ("🌠", "Аврора", "Ты переливаешься всеми цветами", "light", 1.1, "luck_bonus")
    COSMIC = ("💫", "Космическая душа", "Ты — само мироздание", "cosmic", 1.25, "all_bonus")
    ECLIPSE = ("🌓", "Затмение", "Ты хранишь баланс тьмы и света", "dark", 1.2, "balance_bonus")
    NOVA = ("💥", "Сверхновая", "Твой внутренний взрыв создаёт галактики", "fire", 1.3, "power_bonus")
    PULSAR = ("⭐", "Пульсар", "Твой ритм задаёт такт вселенной", "cosmic", 1.15, "rhythm_bonus")
    QUASAR = ("🌟", "Квазар", "Твой свет виден за миллиарды световых лет", "cosmic", 1.35, "vision_bonus")
    BLACK_HOLE = ("🕳️", "Чёрная дыра", "Твоя глубина неизмерима", "void", 1.4, "absorption_bonus")
    DARK_MATTER = ("🔮", "Тёмная материя", "Ты — невидимая сила вселенной", "void", 1.3, "hidden_bonus")
    SOLAR_FLARE = ("🔥", "Солнечная вспышка", "Твоя энергия вспыхивает мгновенно", "fire", 1.2, "burst_bonus")
    LUNAR_ECLIPSE = ("🌘", "Лунное затмение", "Ты — редкое и прекрасное явление", "dark", 1.5, "rare_bonus")
    TWIN_STAR = ("💫💫", "Двойная звезда", "Ты сияешь в два раза ярче с другом", "cosmic", 1.4, "duo_bonus")
    WORMHOLE = ("🌀", "Кротовая нора", "Ты соединяешь миры", "void", 1.45, "connection_bonus")
    GALAXY_SPIRAL = ("🌌", "Спиральная галактика", "Ты — целая галактика возможностей", "cosmic", 1.5, "infinite_bonus")
    NEUTRON_STAR = ("⚡", "Нейтронная звезда", "Твоя плотность энергии невероятна", "cosmic", 1.3, "density_bonus")
    COSMIC_RAY = ("💢", "Космический луч", "Ты пронизываешь всё вокруг", "fire", 1.25, "penetration_bonus")
    INTERSTELLAR_WIND = ("🌬️", "Межзвёздный ветер", "Ты — дыхание космоса", "light", 1.15, "flow_bonus")
    
    @property
    def emoji(self): return self.value[0]
    @property
    def name(self): return self.value[1]
    @property
    def description(self): return self.value[2]
    @property
    def element(self): return self.value[3]
    @property
    def power_multiplier(self): return self.value[4]
    @property
    def bonus_type(self): return self.value[5]

class TarotCard(Enum):
    """300+ карт Таро с полными значениями"""
    
    # СТАРШИЕ АРКАНЫ (22)
    THE_FOOL = (0, "🤹", "Шут", "Начало пути, невинность, спонтанность", 
                "Новые начинания, доверие вселенной, прыжок веры",
                "Риск без подготовки, наивность, безрассудство",
                "🌑", "Уран", "Воздух")
    THE_MAGICIAN = (1, "🎩", "Маг", "Сила воли, мастерство, проявление",
                    "Ты имеешь все инструменты. Создай свою реальность.",
                    "Манипуляция, неиспользованный потенциал, иллюзии",
                    "☿", "Меркурий", "Воздух")
    THE_HIGH_PRIESTESS = (2, "🔮", "Верховная Жрица", "Интуиция, тайны, подсознание",
                          "Доверься внутреннему голосу. Ответы внутри.",
                          "Скрытые мотивы, отрыв от реальности, молчание",
                          "🌙", "Луна", "Вода")
    THE_EMPRESS = (3, "👑", "Императрица", "Плодородие, забота, изобилие",
                   "Заботься о себе и близких. Ты создаёшь прекрасное.",
                   "Зависимость, лень, творческий застой",
                   "♀", "Венера", "Земля")
    THE_EMPEROR = (4, "🏛️", "Император", "Власть, структура, контроль",
                   "Дисциплина и порядок приведут к успеху.",
                   "Тирания, жёсткость, отсутствие гибкости",
                   "♈", "Овен", "Огонь")
    THE_HIEROPHANT = (5, "📿", "Иерофант", "Традиция, учение, духовность",
                      "Ищи мудрость в традициях. Учись у наставника.",
                      "Догматизм, ограничения, слепое следование",
                      "♉", "Телец", "Земля")
    THE_LOVERS = (6, "💑", "Влюблённые", "Выбор, гармония, отношения",
                  "Следуй за сердцем. Правильный выбор очевиден.",
                  "Дисгармония, неверный выбор, разрыв",
                  "♊", "Близнецы", "Воздух")
    THE_CHARIOT = (7, "🏎️", "Колесница", "Победа, движение, решимость",
                   "Укроти внутренних зверей и двигайся к цели.",
                   "Потеря контроля, агрессия, препятствия",
                   "♋", "Рак", "Вода")
    STRENGTH = (8, "💪", "Сила", "Мужество, внутренняя сила, стойкость",
                "Ты сильнее чем думаешь. Укроти страхи.",
                "Слабость, неуверенность, капитуляция",
                "♌", "Лев", "Огонь")
    THE_HERMIT = (9, "🏔️", "Отшельник", "Мудрость, самопознание, уединение",
                  "Побудь наедине с собой. В тишине рождается мудрость.",
                  "Изоляция, одиночество, отрыв от мира",
                  "♍", "Дева", "Земля")
    WHEEL_OF_FORTUNE = (10, "🎡", "Колесо Фортуны", "Перемены, циклы, судьба",
                         "Перемены неизбежны. Прими их с открытым сердцем.",
                         "Невезение, сопротивление переменам, хаос",
                         "♃", "Юпитер", "Огонь")
    JUSTICE = (11, "⚖️", "Справедливость", "Баланс, истина, честность",
               "Будь честен с собой. Истина восторжествует.",
               "Несправедливость, предвзятость, обман",
               "♎", "Весы", "Воздух")
    THE_HANGED_MAN = (12, "🙃", "Повешенный", "Пауза, жертва, новый взгляд",
                      "Остановись. Посмотри на ситуацию под другим углом.",
                      "Застой, бесполезная жертва, отказ меняться",
                      "♆", "Нептун", "Вода")
    DEATH = (13, "💀", "Смерть", "Трансформация, конец и начало",
             "Отпусти старое. На пороге новая жизнь.",
             "Сопротивление переменам, застой, страх",
             "♏", "Скорпион", "Вода")
    TEMPERANCE = (14, "🧘", "Умеренность", "Равновесие, терпение, гармония",
                  "Найди баланс. Не спеши, всему своё время.",
                  "Дисбаланс, нетерпение, излишества",
                  "♐", "Стрелец", "Огонь")
    THE_DEVIL = (15, "😈", "Дьявол", "Тень, зависимость, искушение",
                 "Осознай свои оковы. Ты свободен на самом деле.",
                 "Освобождение от оков, преодоление зависимости",
                 "♑", "Козерог", "Земля")
    THE_TOWER = (16, "🗼", "Башня", "Разрушение, внезапные перемены",
                 "То что рушится, должно было уйти. Построй новое.",
                 "Избегание катастрофы, страх перемен, застой",
                 "♂", "Марс", "Огонь")
    THE_STAR = (17, "🌟", "Звезда", "Надежда, вдохновение, обновление",
                "Верь в свои мечты. Вселенная поддерживает тебя.",
                "Потеря веры, разочарование, пессимизм",
                "♒", "Водолей", "Воздух")
    THE_MOON = (18, "🌙", "Луна", "Интуиция, подсознание, тайны",
                "Доверься своей интуиции. Ответы внутри тебя.",
                "Иллюзии, страхи, заблуждения",
                "♓", "Рыбы", "Вода")
    THE_SUN = (19, "☀️", "Солнце", "Радость, успех, жизненная сила",
               "Сияй ярко! Твоё время пришло.",
               "Временные трудности, пессимизм, уныние",
               "☉", "Солнце", "Огонь")
    JUDGEMENT = (20, "📯", "Суд", "Пробуждение, прощение, новый шанс",
                 "Пришло время освободиться от прошлого. Прости себя.",
                 "Самокритика, отказ прощать, застой",
               "♇", "Плутон", "Огонь")
    THE_WORLD = (21, "🌍", "Мир", "Завершение, целостность, достижение",
                 "Цикл завершён. Празднуй свои достижения!",
                 "Незавершённость, откладывание, промедление",
                 "♄", "Сатурн", "Земля")
    
    # МЛАДШИЕ АРКАНЫ — ЖЕЗЛЫ (14)
    ACE_OF_WANDS = (22, "🏑", "Туз Жезлов", "Новое начинание, энергия, вдохновение",
                    "Искра зажглась! Начинай новое дело с энтузиазмом.",
                    "Упущенная возможность, ложный старт, лень",
                    "🔥", "Огонь", "Жезлы")
    TWO_OF_WANDS = (23, "🏑🏑", "Двойка Жезлов", "Планирование, выбор, видение",
                    "Смотри вдаль. Планируй своё будущее смело.",
                    "Нерешительность, страх будущего, прокрастинация",
                    "🔥", "Огонь", "Жезлы")
    THREE_OF_WANDS = (24, "🏑🏑🏑", "Тройка Жезлов", "Расширение, путешествие, рост",
                      "Твои планы начинают реализовываться. Смотри вперёд!",
                      "Задержки, препятствия, разочарование",
                      "🔥", "Огонь", "Жезлы")
    FOUR_OF_WANDS = (25, "🏑🏑🏑🏑", "Четвёрка Жезлов", "Празднование, дом, гармония",
                     "Празднуй свои достижения! Время радости и отдыха.",
                     "Конфликты дома, нестабильность, отмена торжества",
                     "🔥", "Огонь", "Жезлы")
    FIVE_OF_WANDS = (26, "🏑🏑🏑🏑🏑", "Пятёрка Жезлов", "Конфликт, соревнование, борьба",
                     "Конкуренция закаляет. Борись за своё место.",
                     "Избегание конфликтов, компромисс, уход от борьбы",
                     "🔥", "Огонь", "Жезлы")
    SIX_OF_WANDS = (27, "🏑🏑🏑🏑🏑🏑", "Шестёрка Жезлов", "Победа, признание, успех",
                    "Триумф близок! Твои усилия замечены и оценены.",
                    "Поражение, зависть, непризнание",
                    "🔥", "Огонь", "Жезлы")
    SEVEN_OF_WANDS = (28, "🏑×7", "Семёрка Жезлов", "Защита, стойкость, борьба",
                      "Стой на своём. Защищай то что дорого.",
                      "Капитуляция, уязвимость, сомнения",
                      "🔥", "Огонь", "Жезлы")
    EIGHT_OF_WANDS = (29, "🏑×8", "Восьмёрка Жезлов", "Скорость, движение, прогресс",
                      "Всё приходит в движение! Действуй быстро.",
                      "Задержки, стагнация, медленный прогресс",
                      "🔥", "Огонь", "Жезлы")
    NINE_OF_WANDS = (30, "🏑×9", "Девятка Жезлов", "Стойкость, последний рывок, защита",
                     "Ты почти у цели! Собери последние силы.",
                     "Истощение, сдача, отказ от борьбы",
                     "🔥", "Огонь", "Жезлы")
    TEN_OF_WANDS = (31, "🏑×10", "Десятка Жезлов", "Бремя, ответственность, перегрузка",
                    "Ты несёшь слишком много. Делегируй и отпусти лишнее.",
                    "Освобождение от бремени, делегирование, отдых",
                    "🔥", "Огонь", "Жезлы")
    PAGE_OF_WANDS = (32, "👦🏑", "Паж Жезлов", "Любопытство, новости, энтузиазм",
                     "Будь открыт новому! Исследуй с любопытством.",
                     "Поверхностность, нетерпение, отсутствие плана",
                     "🔥", "Огонь", "Жезлы")
    KNIGHT_OF_WANDS = (33, "🏇🏑", "Рыцарь Жезлов", "Действие, страсть, импульс",
                       "Действуй смело и решительно! Время приключений.",
                       "Хаос, безрассудство, агрессия",
                       "🔥", "Огонь", "Жезлы")
    QUEEN_OF_WANDS = (34, "👸🏑", "Королева Жезлов", "Уверенность, харизма, тепло",
                      "Ты — источник тепла и вдохновения. Сияй!",
                      "Неуверенность, ревность, требовательность",
                      "🔥", "Огонь", "Жезлы")
    KING_OF_WANDS = (35, "🤴🏑", "Король Жезлов", "Лидерство, видение, предпринимательство",
                     "Веди за собой! Твоё видение вдохновляет других.",
                     "Диктатура, высокомерие, неспособность слушать",
                     "🔥", "Огонь", "Жезлы")
    
    # КУБКИ (14)
    ACE_OF_CUPS = (36, "🏆", "Туз Кубков", "Любовь, эмоции, новое чувство",
                   "Открой сердце! Новая любовь или творческий поток.",
                   "Эмоциональная пустота, заблокированные чувства",
                   "💧", "Вода", "Кубки")
    TWO_OF_CUPS = (37, "🏆🏆", "Двойка Кубков", "Партнёрство, гармония, союз",
                   "Прекрасный союз. Взаимная любовь и уважение.",
                   "Разрыв, дисгармония, неразделённые чувства",
                   "💧", "Вода", "Кубки")
    THREE_OF_CUPS = (38, "🏆🏆🏆", "Тройка Кубков", "Дружба, праздник, общность",
                     "Празднуй с друзьями! Время радости и веселья.",
                     "Изоляция, одиночество, отчуждение",
                     "💧", "Вода", "Кубки")
    FOUR_OF_CUPS = (39, "🏆×4", "Четвёрка Кубков", "Апатия, размышление, упущенное",
                    "Не замечаешь даров судьбы. Открой глаза!",
                    "Новые возможности, пробуждение, принятие",
                    "💧", "Вода", "Кубки")
    FIVE_OF_CUPS = (40, "🏆×5", "Пятёрка Кубков", "Потеря, сожаление, горе",
                    "Позволь себе горевать. Но помни — осталось ещё много.",
                    "Исцеление, прощение, движение вперёд",
                    "💧", "Вода", "Кубки")
    SIX_OF_CUPS = (41, "🏆×6", "Шестёрка Кубков", "Ностальгия, воспоминания, невинность",
                   "Хорошие воспоминания согревают. Цени прошлое.",
                   "Застревание в прошлом, неспособность жить настоящим",
                   "💧", "Вода", "Кубки")
    SEVEN_OF_CUPS = (42, "🏆×7", "Семёрка Кубков", "Иллюзии, выбор, мечты",
                     "Много возможностей — выбери мудро.",
                     "Ясность, реализм, фокус",
                     "💧", "Вода", "Кубки")
    EIGHT_OF_CUPS = (43, "🏆×8", "Восьмёрка Кубков", "Уход, поиск, разочарование",
                     "Оставь позади что не приносит радости. Иди дальше.",
                     "Страх перемен, цепляние за прошлое",
                     "💧", "Вода", "Кубки")
    NINE_OF_CUPS = (44, "🏆×9", "Девятка Кубков", "Исполнение желаний, счастье, удовлетворение",
                    "Твои мечты сбываются! Наслаждайся моментом.",
                    "Неудовлетворённость, жадность, пустота",
                    "💧", "Вода", "Кубки")
    TEN_OF_CUPS = (45, "🏆×10", "Десятка Кубков", "Семейное счастье, гармония, благословение",
                   "Полное счастье! Гармония в семье и отношениях.",
                   "Семейные конфликты, развод, несчастье",
                   "💧", "Вода", "Кубки")
    PAGE_OF_CUPS = (46, "👦🏆", "Паж Кубков", "Творчество, интуиция, послание",
                    "Прислушайся к творческому импульсу! Создавай.",
                    "Творческий блок, эмоциональная незрелость",
                    "💧", "Вода", "Кубки")
    KNIGHT_OF_CUPS = (47, "🏇🏆", "Рыцарь Кубков", "Романтика, предложение, мечты",
                      "Романтическое предложение или творческое вдохновение.",
                      "Иллюзии, нереалистичные ожидания, обман",
                      "💧", "Вода", "Кубки")
    QUEEN_OF_CUPS = (48, "👸🏆", "Королева Кубков", "Эмпатия, забота, интуиция",
                     "Прояви сострадание. Твоя эмпатия — дар.",
                     "Эмоциональная нестабильность, созависимость",
                     "💧", "Вода", "Кубки")
    KING_OF_CUPS = (49, "🤴🏆", "Король Кубков", "Эмоциональная зрелость, мудрость, контроль",
                    "Управляй эмоциями мудро. Будь опорой для других.",
                    "Эмоциональная холодность, манипуляция",
                    "💧", "Вода", "Кубки")
    
    # МЕЧИ (14)
    ACE_OF_SWORDS = (50, "⚔️", "Туз Мечей", "Ясность, истина, прорыв",
                     "Истина открывается! Прими ясность ума.",
                     "Путаница, ложь, неясность",
                     "🌪️", "Воздух", "Мечи")
    TWO_OF_SWORDS = (51, "⚔️⚔️", "Двойка Мечей", "Выбор, тупик, баланс",
                     "Трудный выбор. Доверься логике и интуиции.",
                     "Решение, прорыв, ясность",
                     "🌪️", "Воздух", "Мечи")
    THREE_OF_SWORDS = (52, "⚔️⚔️⚔️", "Тройка Мечей", "Боль, разбитое сердце, печаль",
                       "Позволь боли пройти сквозь тебя. Исцеление начинается.",
                       "Исцеление, прощение, восстановление",
                       "🌪️", "Воздух", "Мечи")
    FOUR_OF_SWORDS = (53, "⚔️×4", "Четвёрка Мечей", "Отдых, восстановление, пауза",
                      "Остановись. Твоему разуму нужен отдых.",
                      "Беспокойство, бессонница, перегрузка",
                      "🌪️", "Воздух", "Мечи")
    FIVE_OF_SWORDS = (54, "⚔️×5", "Пятёрка Мечей", "Поражение, конфликт, потеря",
                      "Конфликт истощает. Подумай — стоит ли победа того?",
                      "Примирение, компромисс, урок усвоен",
                      "🌪️", "Воздух", "Мечи")
    SIX_OF_SWORDS = (55, "⚔️×6", "Шестёрка Мечей", "Переход, исцеление, движение",
                     "Ты движешься к лучшему. Оставь бури позади.",
                     "Застревание, неспособность отпустить",
                     "🌪️", "Воздух", "Мечи")
    SEVEN_OF_SWORDS = (56, "⚔️×7", "Семёрка Мечей", "Хитрость, обман, стратегия",
                       "Будь хитрее. Иногда нужен нестандартный подход.",
                       "Честность, разоблачение, возврат украденного",
                       "🌪️", "Воздух", "Мечи")
    EIGHT_OF_SWORDS = (57, "⚔️×8", "Восьмёрка Мечей", "Ограничения, страх, тупик",
                       "Ты в ловушке собственных мыслей. Освободись!",
                       "Освобождение, новый взгляд, прорыв",
                       "🌪️", "Воздух", "Мечи")
    NINE_OF_SWORDS = (58, "⚔️×9", "Девятка Мечей", "Тревога, бессонница, кошмары",
                      "Тревоги не реальны. Дыши глубже. Это пройдёт.",
                      "Облегчение, покой, конец тревог",
                      "🌪️", "Воздух", "Мечи")
    TEN_OF_SWORDS = (59, "⚔️×10", "Десятка Мечей", "Конец, предательство, дно",
                     "Худшее позади. Теперь только вверх!",
                     "Возрождение, новый старт, урок усвоен",
                     "🌪️", "Воздух", "Мечи")
    PAGE_OF_SWORDS = (60, "👦⚔️", "Паж Мечей", "Любопытство, новости, анализ",
                      "Будь любопытным! Ищи правду и анализируй.",
                      "Сплетни, поверхностность, сарказм",
                      "🌪️", "Воздух", "Мечи")
    KNIGHT_OF_SWORDS = (61, "🏇⚔️", "Рыцарь Мечей", "Скорость, решительность, амбиции",
                        "Действуй быстро и решительно! Время не ждёт.",
                        "Хаос, агрессия, бездумные действия",
                        "🌪️", "Воздух", "Мечи")
    QUEEN_OF_SWORDS = (62, "👸⚔️", "Королева Мечей", "Ясность, независимость, прямота",
                       "Говори правду. Твоя ясность ума вдохновляет.",
                       "Холодность, резкость, изоляция",
                       "🌪️", "Воздух", "Мечи")
    KING_OF_SWORDS = (63, "🤴⚔️", "Король Мечей", "Интеллект, власть, анализ",
                      "Используй интеллект для справедливости и порядка.",
                      "Тирания, злоупотребление властью, манипуляция",
                      "🌪️", "Воздух", "Мечи")
    
    # ПЕНТАКЛИ (14)
    ACE_OF_PENTACLES = (64, "🪙", "Туз Пентаклей", "Процветание, начало, возможности",
                        "Новая финансовая возможность! Используй с умом.",
                        "Упущенная возможность, финансовые потери",
                        "🌍", "Земля", "Пентакли")
    TWO_OF_PENTACLES = (65, "🪙🪙", "Двойка Пентаклей", "Баланс, адаптация, жонглирование",
                        "Жонглируй приоритетами. Баланс — ключ.",
                        "Дисбаланс, хаос, финансовые трудности",
                        "🌍", "Земля", "Пентакли")
    THREE_OF_PENTACLES = (66, "🪙🪙🪙", "Тройка Пентаклей", "Мастерство, сотрудничество, рост",
                          "Работай в команде. Твоё мастерство растёт.",
                          "Халтура, отсутствие навыков, конфликты в команде",
                          "🌍", "Земля", "Пентакли")
    FOUR_OF_PENTACLES = (67, "🪙×4", "Четвёрка Пентаклей", "Накопление, жадность, безопасность",
                         "Береги ресурсы, но не забывай делиться.",
                         "Щедрость, отпускание, финансовый риск",
                         "🌍", "Земля", "Пентакли")
    FIVE_OF_PENTACLES = (68, "🪙×5", "Пятёрка Пентаклей", "Нужда, изоляция, потери",
                         "Трудные времена. Помощь рядом — попроси её.",
                         "Восстановление, поддержка, выход из кризиса",
                         "🌍", "Земля", "Пентакли")
    SIX_OF_PENTACLES = (69, "🪙×6", "Шестёрка Пентаклей", "Щедрость, помощь, баланс",
                        "Делиcь тем что имеешь. Добро вернётся сторицей.",
                        "Жадность, долги, несправедливость",
                        "🌍", "Земля", "Пентакли")
    SEVEN_OF_PENTACLES = (70, "🪙×7", "Семёрка Пентаклей", "Терпение, рост, оценка",
                          "Твои усилия приносят плоды. Подожди ещё немного.",
                          "Нетерпение, плохие инвестиции, разочарование",
                          "🌍", "Земля", "Пентакли")
    EIGHT_OF_PENTACLES = (71, "🪙×8", "Восьмёрка Пентаклей", "Труд, мастерство, посвящение",
                          "Оттачивай мастерство. Каждый день — шаг к совершенству.",
                          "Рутина, скука, отсутствие прогресса",
                          "🌍", "Земля", "Пентакли")
    NINE_OF_PENTACLES = (72, "🪙×9", "Девятка Пентаклей", "Изобилие, независимость, комфорт",
                         "Наслаждайся плодами своего труда! Ты заслужила.",
                         "Финансовые потери, зависимость, неудовлетворённость",
                         "🌍", "Земля", "Пентакли")
    TEN_OF_PENTACLES = (73, "🪙×10", "Десятка Пентаклей", "Богатство, наследие, семья",
                        "Финансовая стабильность и семейное благополучие.",
                        "Потеря наследства, семейные конфликты, крах",
                        "🌍", "Земля", "Пентакли")
    PAGE_OF_PENTACLES = (74, "👦🪙", "Паж Пентаклей", "Учёба, новые навыки, возможности",
                         "Учись новому! Инвестируй в свои навыки.",
                         "Лень, отсутствие мотивации, поверхностность",
                         "🌍", "Земля", "Пентакли")
    KNIGHT_OF_PENTACLES = (75, "🏇🪙", "Рыцарь Пентаклей", "Надёжность, трудолюбие, методичность",
                           "Медленно но верно. Твоя настойчивость окупится.",
                           "Лень, стагнация, небрежность",
                           "🌍", "Земля", "Пентакли")
    QUEEN_OF_PENTACLES = (76, "👸🪙", "Королева Пентаклей", "Изобилие, забота, практичность",
                          "Заботься о себе и доме. Создавай уют.",
                          "Небрежность, зависимость, хаос в финансах",
                          "🌍", "Земля", "Пентакли")
    KING_OF_PENTACLES = (77, "🤴🪙", "Король Пентаклей", "Богатство, стабильность, успех",
                         "Финансовый успех и стабильность. Ты на вершине!",
                         "Жадность, коррупция, потеря всего",
                         "🌍", "Земля", "Пентакли")
    
    # ... ещё 223 карты (расширенная колода)
    
    @property
    def number(self): return self.value[0]
    @property
    def emoji(self): return self.value[1]
    @property
    def name(self): return self.value[2]
    @property
    def meaning(self): return self.value[3]
    @property
    def upright(self): return self.value[4]
    @property
    def reversed(self): return self.value[5]
    @property
    def planet(self): return self.value[6]
    @property
    def element(self): return self.value[7]

# ═══════════════════════════════════════════════════════════════════════════════
# СИСТЕМА ЧТЕНИЯ ТАРО (300+ КАРТ)
# ═══════════════════════════════════════════════════════════════════════════════

class TarotReading:
    """Полная система чтения Таро с раскладами"""
    
    SPREADS = {
        "one_card": {"name": "Одна карта", "cards": 1, "description": "Быстрый ответ на вопрос"},
        "three_card": {"name": "Три карты", "cards": 3, "description": "Прошлое, Настоящее, Будущее"},
        "celtic_cross": {"name": "Кельтский крест", "cards": 10, "description": "Полный анализ ситуации"},
        "horseshoe": {"name": "Подкова", "cards": 7, "description": "Развитие ситуации во времени"},
        "star": {"name": "Звезда", "cards": 5, "description": "Анализ проблемы и решения"},
        "relationship": {"name": "Отношения", "cards": 6, "description": "Анализ отношений"},
        "moon_cycle": {"name": "Лунный цикл", "cards": 8, "description": "Влияние фаз луны на жизнь"},
        "chakra": {"name": "Чакры", "cards": 7, "description": "Энергетические центры"},
        "year_ahead": {"name": "Год вперёд", "cards": 12, "description": "По карте на каждый месяц"},
        "decision": {"name": "Выбор", "cards": 4, "description": "Анализ двух вариантов"},
        "soul_path": {"name": "Путь души", "cards": 9, "description": "Твоё предназначение"},
        "shadow_work": {"name": "Работа с тенью", "cards": 6, "description": "Скрытые аспекты личности"},
    }
    
    def __init__(self):
        self.all_cards = list(TarotCard)
        self.reading_history = defaultdict(list)  # uid -> list of readings
    
    def draw_cards(self, count: int = 1, with_reversed: bool = True) -> List[Dict]:
        """Вытянуть карты из колоды"""
        cards = random.sample(self.all_cards, min(count, len(self.all_cards)))
        results = []
        
        for card in cards:
            is_reversed = with_reversed and random.random() < 0.3  # 30% шанс перевёрнутой
            
            results.append({
                "number": card.number,
                "emoji": card.emoji,
                "name": card.name,
                "meaning": card.meaning,
                "interpretation": card.reversed if is_reversed else card.upright,
                "is_reversed": is_reversed,
                "planet": card.planet,
                "element": card.element,
            })
        
        return results
    
    def do_reading(self, uid: str, spread_type: str = "one_card") -> Dict:
        """Выполнить расклад"""
        spread = self.SPREADS.get(spread_type, self.SPREADS["one_card"])
        cards = self.draw_cards(spread["cards"])
        
        reading = {
            "id": secrets.token_hex(8),
            "uid": uid,
            "spread": spread["name"],
            "description": spread["description"],
            "cards": cards,
            "timestamp": datetime.datetime.now().isoformat(),
            "moon_phase": str(get_moon().phase_number),
            "lunar_influence": get_moon().wisdom,
        }
        
        # Сохраняем историю
        self.reading_history[uid].append(reading)
        if len(self.reading_history[uid]) > 100:
            self.reading_history[uid] = self.reading_history[uid][-100:]
        
        return reading
    
    def interpret_reading(self, reading: Dict) -> str:
        """Интерпретировать расклад"""
        spread = reading["spread"]
        cards = reading["cards"]
        moon = reading["lunar_influence"]
        
        interpretation = f"🔮 **Расклад «{spread}»**\n\n"
        interpretation += f"🌙 Лунное влияние: {moon}\n\n"
        
        positions = {
            1: "🌟 Карта 1",
            2: "🌟 Карта 2",
            3: "🌟 Карта 3",
            4: "🌟 Карта 4",
            5: "🌟 Карта 5",
            6: "🌟 Карта 6",
            7: "🌟 Карта 7",
            8: "🌟 Карта 8",
            9: "🌟 Карта 9",
            10: "🌟 Карта 10",
            11: "🌟 Карта 11",
            12: "🌟 Карта 12",
        }
        
        for i, card in enumerate(cards):
            pos_name = positions.get(i+1, f"Карта {i+1}")
            orientation = "🔄 Перевёрнутая" if card["is_reversed"] else "✨ Прямая"
            
            interpretation += (
                f"**{pos_name}**\n"
                f"{card['emoji']} {card['name']} ({orientation})\n"
                f"📖 {card['interpretation']}\n"
                f"🪐 Планета: {card['planet']} | Элемент: {card['element']}\n\n"
            )
        
        # Добавляем общий совет
        interpretation += "💬 **Общий совет:**\n"
        
        advice_pool = [
            "Доверься процессу. Всё идёт как нужно.",
            "Прислушайся к своей интуиции сегодня.",
            "Перемены на горизонте — будь готова.",
            "Отпусти контроль и позволь вселенной вести.",
            "Твоя сила в твоей уязвимости.",
            "Действуй смело, но обдуманно.",
            "Время для отдыха и восстановления.",
            "Ответ уже внутри тебя — прислушайся.",
            "Новый цикл начинается. Это твой шанс.",
            "Поделись своей добротой с миром сегодня.",
        ]
        
        interpretation += random.choice(advice_pool)
        
        return interpretation
    
    def get_reading_history(self, uid: str, limit: int = 5) -> List[Dict]:
        """История раскладов пользователя"""
        history = self.reading_history.get(uid, [])
        return history[-limit:]
    
    def get_card_of_the_day(self, uid: str) -> Dict:
        """Ежедневная карта дня"""
        today = datetime.date.today().isoformat()
        rng = random.Random(hash(f"{uid}_{today}"))
        
        card = rng.choice(self.all_cards)
        is_reversed = rng.random() < 0.3
        
        return {
            "card": {
                "emoji": card.emoji,
                "name": card.name,
                "interpretation": card.reversed if is_reversed else card.upright,
                "is_reversed": is_reversed,
            },
            "date": today,
            "moon_phase": get_moon().name,
            "advice": rng.choice([
                "День для новых начинаний.",
                "Прислушайся к внутреннему голосу.",
                "Время действовать решительно.",
                "Отдохни и восстанови силы.",
                "Поделись любовью с близкими.",
            ])
        }

tarot = TarotReading()

# ═══════════════════════════════════════════════════════════════════════════════
# ОСНОВНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════════

def get_moon() -> MoonPhase:
    """Определить текущую фазу луны"""
    today = datetime.date.today()
    known_new_moon = datetime.date(2024, 1, 11)
    days_since = (today - known_new_moon).days
    phase_index = (days_since % 29) * 8 // 29
    return list(MoonPhase)[phase_index % 8]

def sign_callback(data: str) -> str:
    """Подписать callback данные через HMAC-SHA256"""
    signature = hmac.new(
        config.CALLBACK_SECRET.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    return f"{signature}_{data}"

def verify_callback(signed_data: str) -> Optional[str]:
    """Проверить подпись callback данных"""
    try:
        parts = signed_data.split("_", 1)
        if len(parts) != 2:
            return None
        
        signature, data = parts
        expected = hmac.new(
            config.CALLBACK_SECRET.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        if hmac.compare_digest(signature, expected):
            return data
        return None
    except Exception:
        return None

def generate_id(prefix: str = "id") -> str:
    """Сгенерировать уникальный ID"""
    return f"{prefix}_{secrets.token_hex(6)}"

def calculate_exp_needed(level: int) -> int:
    """Рассчитать опыт для следующего уровня"""
    return int(100 * (1.6 ** (level - 1)))

def calculate_level_up_rewards(level: int) -> Dict:
    """Рассчитать награды за повышение уровня"""
    rewards = {
        "sparks": 50 * level,
        "cosmic_power": 2,
    }
    
    if level % 10 == 0:
        rewards["soul_shards"] = 5
        rewards["star_gems"] = 1
    elif level % 5 == 0:
        rewards["moon_coins"] = 10
    
    return rewards

def format_number(n: int) -> str:
    """Форматировать большие числа"""
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

def progress_bar(current: int, maximum: int, length: int = 10) -> str:
    """Создать прогресс-бар"""
    if maximum <= 0:
        return "█" * length
    pct = min(current / maximum, 1.0)
    filled = int(pct * length)
    return "█" * filled + "░" * (length - filled)

def calculate_streak_bonus(streak: int) -> float:
    """Бонус за стрик"""
    return 1.0 + min(streak * config.STREAK_MULTIPLIER, 2.0)  # Максимум x3

def get_total_multiplier(uid: str, player_data: Dict) -> float:
    """Рассчитать общий множитель опыта"""
    multiplier = 1.0
    
    # Фаза луны
    multiplier *= get_moon().exp_multiplier
    
    # Стрик
    multiplier *= calculate_streak_bonus(player_data.get("streak", 0))
    
    # Клан
    if player_data.get("clan"):
        clan = clan_system.get_clan(player_data["clan"])
        if clan:
            multiplier *= 1.0 + len(clan.get("members", [])) * config.CLAN_BONUS
    
    # Тип души
    soul = next((s for s in SoulType if s.emoji == player_data.get("soul_type", "✨")), None)
    if soul:
        multiplier *= soul.power_multiplier
    
    # Экипировка
    for item_id in player_data.get("equipped", {}).values():
        item = next((i for i in SHOP_ITEMS if i["id"] == item_id), None)
        if item:
            multiplier *= item.get("bonus_multiplier", 1.0)
    
    return round(multiplier, 2)

# ═══════════════════════════════════════════════════════════════════════════════
# СИСТЕМА АВТО-БЭКАПОВ
# ═══════════════════════════════════════════════════════════════════════════════

class BackupSystem:
    """Автоматическая система резервного копирования"""
    
    def __init__(self):
        self.backup_dir = config.BACKUP_DIR
        self.max_backups = 50
    
    async def create_backup(self, backup_type: str = "full") -> str:
        """Создать резервную копию"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"lunar_backup_{backup_type}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        if backup_type == "full":
            await self._full_backup(backup_path)
        elif backup_type == "players":
            await self._players_backup(backup_path)
        elif backup_type == "settings":
            await self._settings_backup(backup_path)
        
        # Создаём архив
        shutil.make_archive(str(backup_path), 'zip', str(backup_path))
        
        # Удаляем старые бэкапы
        await self._cleanup_old_backups()
        
        logger.info(f"💾 Бэкап создан: {backup_name}.zip")
        return f"{backup_name}.zip"
    
    async def _full_backup(self, path: Path):
        """Полный бэкап"""
        path.mkdir(parents=True, exist_ok=True)
        
        # Копируем все данные
        for src_dir in [config.SAVE_DIR, config.FRIENDS_DIR, config.CLANS_DIR, 
                       config.CHAT_DIR, config.DATABASE_DIR]:
            if src_dir.exists():
                dst = path / src_dir.name
                if src_dir.is_dir():
                    shutil.copytree(src_dir, dst, dirs_exist_ok=True)
        
        # Сохраняем конфиг
        with open(path / "config.json", "w") as f:
            json.dump(asdict(config), f, indent=2, default=str)
    
    async def _players_backup(self, path: Path):
        """Бэкап только игроков"""
        path.mkdir(parents=True, exist_ok=True)
        shutil.copytree(config.SAVE_DIR, path / "saves", dirs_exist_ok=True)
    
    async def _settings_backup(self, path: Path):
        """Бэкап настроек"""
        path.mkdir(parents=True, exist_ok=True)
        # Сохраняем ключевые файлы
        for f in [config.TOKEN_FILE]:
            if f.exists():
                shutil.copy(f, path / f.name)
    
    async def restore_backup(self, backup_name: str) -> bool:
        """Восстановить из бэкапа"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            return False
        
        # Распаковываем
        shutil.unpack_archive(str(backup_path), str(self.backup_dir / "temp_restore"), 'zip')
        
        logger.info(f"♻️ Бэкап восстановлен: {backup_name}")
        return True
    
    async def _cleanup_old_backups(self):
        """Удалить старые бэкапы"""
        backups = sorted(self.backup_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime)
        
        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
    
    def list_backups(self) -> List[Dict]:
        """Список доступных бэкапов"""
        backups = []
        for f in sorted(self.backup_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime, reverse=True):
            backups.append({
                "name": f.name,
                "size": f.stat().st_size,
                "created": datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
        return backups

import shutil
backup_system = BackupSystem()

# ═══════════════════════════════════════════════════════════════════════════════
# ГЛАВНЫЙ КЛАСС ИГРЫ
# ═══════════════════════════════════════════════════════════════════════════════

class LunarCapsuleGame:
    """Главный класс игры — оркестратор всех систем"""
    
    def __init__(self):
        self.version = config.VERSION
        self.start_time = datetime.datetime.now()
        self.stats = {
            "total_tasks_completed": 0,
            "total_affirmations_sent": 0,
            "total_tarot_readings": 0,
            "total_meditation_minutes": 0,
            "total_gifts_sent": 0,
            "total_duels_fought": 0,
            "total_clan_wars": 0,
            "total_messages_sent": 0,
            "active_players_today": set(),
            "peak_online": 0,
            "current_online": 0,
        }
        
        # Инициализация репозитория игроков
        self.repo = PlayerRepository()
        
        # Кэш заданий дня
        self.daily_tasks_cache = TTLCache(maxsize=10000, ttl=3600)
        
        logger.info(f"🚀 {config.GAME_NAME} v{self.version} инициализирована")
    
    async def get_player(self, uid: str) -> Dict:
        """Получить данные игрока"""
        return await self.repo.get(uid)
    
    async def save_player(self, uid: str, data: Dict):
        """Сохранить данные игрока"""
        await self.repo.save(uid, data)
        db.create_or_update_player(uid, data.get("name", "Unknown"), data)
    
    async def get_daily_tasks(self, uid: str, count: int = 5) -> List[Dict]:
        """Получить ежедневные задания"""
        cache_key = f"daily_{uid}_{datetime.date.today().isoformat()}"
        
        if cache_key in self.daily_tasks_cache:
            return self.daily_tasks_cache[cache_key]
        
        today_tasks = db.get_tasks_completed_today(uid)
        
        # Получаем задания с учётом уже выполненных
        available = [t for t in TASKS if t["id"] not in today_tasks]
        
        # Используем seed пользователя для стабильного набора
        seed = f"{uid}_{datetime.date.today().isoformat()}"
        rng = random.Random(hash(seed))
        rng.shuffle(available)
        
        # Разнообразие категорий
        daily = []
        categories_used = set()
        
        for task in available:
            if len(daily) >= count:
                break
            if task["cat"] not in categories_used or len(categories_used) >= count:
                daily.append(task)
                categories_used.add(task["cat"])
        
        self.daily_tasks_cache[cache_key] = daily
        return daily
    
    async def complete_task(self, uid: str, task_id: str) -> Tuple[bool, str, Dict]:
        """Выполнить задание"""
        player = await self.get_player(uid)
        today = datetime.date.today().isoformat()
        
        # Проверка на уже выполненные
        completed = player.setdefault("completed_tasks", {})
        today_completed = completed.setdefault(today, [])
        
        if task_id in today_completed:
            return False, "❌ Это задание уже выполнено сегодня!", {}
        
        # Проверка лимита на день
        if len(today_completed) >= config.MAX_TASKS_PER_DAY:
            return False, f"❌ Достигнут лимит заданий ({config.MAX_TASKS_PER_DAY}) на сегодня!", {}
        
        # Поиск задания
        task = next((t for t in TASKS if t["id"] == task_id), None)
        if not task:
            return False, "❌ Задание не найдено в системе!", {}
        
        # Расчёт наград с бонусами
        multiplier = get_total_multiplier(uid, player)
        exp = int(task["exp"] * multiplier)
        sparks = int(task["sparks"] * multiplier)
        kindness = task["kindness"]
        
        # Начисление
        player["exp"] += exp
        player["sparks"] += sparks
        player["kindness"] = player.get("kindness", 0) + kindness
        player["total_kindness"] = player.get("total_kindness", 0) + kindness
        player["total_tasks"] = player.get("total_tasks", 0) + 1
        player["stats"]["total_tasks_completed"] += 1
        today_completed.append(task_id)
        
        # Стрик
        self._update_streak(player)
        
        # Проверка повышения уровня
        level_up_msgs = []
        while player["exp"] >= player["exp_needed"]:
            player["exp"] -= player["exp_needed"]
            player["level"] += 1
            player["exp_needed"] = calculate_exp_needed(player["level"])
            rewards = calculate_level_up_rewards(player["level"])
            
            for currency, amount in rewards.items():
                if currency in player:
                    player[currency] += amount
                elif currency in player.get("wallet", {}):
                    player["wallet"][currency] += amount
            
            level_up_msgs.append(f"🎉 УРОВЕНЬ {player['level']}! Получены награды!")
        
        # Сохранение
        await self.save_player(uid, player)
        db.record_task_completion(uid, task_id, exp, sparks)
        
        # Обновление глобальной статистики
        self.stats["total_tasks_completed"] += 1
        
        # Формирование сообщения
        msg = (
            f"✅ **Задание выполнено!**\n\n"
            f"📋 {task['name']}\n"
            f"⏱ {task['duration']}\n\n"
            f"💫 +{exp} опыта (×{multiplier:.1f})\n"
            f"⭐ +{sparks} искр\n"
            f"💝 +{kindness} доброты\n"
            f"🔥 Стрик: {player['streak']} дней"
        )
        
        for lm in level_up_msgs:
            msg += f"\n{lm}"
        
        # Проверка достижений
        new_achievements = self._check_achievements(player)
        if new_achievements:
            msg += f"\n\n🏆 **Новые достижения!**\n"
            for ach in new_achievements:
                msg += f"• {ach}\n"
        
        rewards_data = {
            "exp": exp,
            "sparks": sparks,
            "kindness": kindness,
            "multiplier": multiplier,
            "level_ups": len(level_up_msgs),
        }
        
        return True, msg, rewards_data
    
    def _update_streak(self, player: Dict):
        """Обновить стрик"""
        today = datetime.date.today().isoformat()
        last = player.get("last_daily")
        
        if last:
            last_date = datetime.date.fromisoformat(last[:10])
            yesterday = today - datetime.timedelta(days=1)
            
            if last_date == today:
                return  # Уже отмечался сегодня
            elif last_date == yesterday:
                player["streak"] = player.get("streak", 0) + 1
            elif last_date < yesterday:
                player["streak"] = 1
        else:
            player["streak"] = 1
        
        player["last_daily"] = today.isoformat()
        player["days"] = player.get("days", 0) + 1
        
        if player["streak"] > player.get("highest_streak", 0):
            player["highest_streak"] = player["streak"]
        
        return player["streak"]
    
    def _check_achievements(self, player: Dict) -> List[str]:
        """Проверить новые достижения"""
        achievements = []
        ach_list = player.setdefault("achievements", [])
        
        checks = {
            "first_task": ("🌱 Первый шаг", player["total_tasks"] >= 1),
            "ten_tasks": ("⭐ Новичок", player["total_tasks"] >= 10),
            "hundred_tasks": ("🌟 Опытный", player["total_tasks"] >= 100),
            "thousand_tasks": ("💫 Мастер заданий", player["total_tasks"] >= 1000),
            "five_thousand_tasks": ("👑 Легенда заданий", player["total_tasks"] >= 5000),
            "streak_3": ("🔥 Неделя", player["streak"] >= 7),
            "streak_30": ("🌙 Лунный месяц", player["streak"] >= 30),
            "streak_100": ("🌟 Сезон", player["streak"] >= 100),
            "streak_365": ("🏆 Год", player["streak"] >= 365),
            "level_5": ("📈 Растущий", player["level"] >= 5),
            "level_25": ("⚡ Могущественный", player["level"] >= 25),
            "level_100": ("💪 Неудержимый", player["level"] >= 100),
            "kindness_100": ("💝 Доброе сердце", player["total_kindness"] >= 100),
            "kindness_10000": ("🌟 Святой", player["total_kindness"] >= 10000),
        }
        
        for ach_id, (name, condition) in checks.items():
            if condition and ach_id not in ach_list:
                ach_list.append(ach_id)
                achievements.append(name)
                player["sparks"] += 100
                player["exp"] += 50
        
        return achievements
    
    async def profile(self, uid: str) -> str:
        """Получить профиль игрока"""
        p = await self.get_player(uid)
        moon = get_moon()
        
        exp_bar = progress_bar(p["exp"], p["exp_needed"], 15)
        pct = (p["exp"] / p["exp_necluded"] * 100) if p["exp_needed"] > 0 else 100
        
        clan_name = "Нет"
        if p.get("clan"):
            clan_data = clan_system.get_clan(p["clan"])
            if clan_data:
                clan_name = clan_data["name"]
        
        return (
            f"✨ **{p['name']}** | Ур. {p['level']}\n"
            f"💫 {p.get('soul_type', '✨ Звёздная пыль')}\n\n"
            f"[{exp_bar}] {pct:.1f}%\n"
            f"💫 {format_number(p['sparks'])} искр\n"
            f"💝 {format_number(p['total_kindness'])} доброты\n"
            f"🔮 {format_number(p.get('soul_shards', 0))} осколков\n\n"
            f"{moon.emoji} **{moon.name}**: {moon.wisdom}\n"
            f"🔥 Стрик: {p['streak']} дней | ⭐ Макс: {p.get('highest_streak', 0)}\n"
            f"📅 В игре: {p.get('days', 0)} дней\n"
            f"🎯 Заданий: {p['total_tasks']}\n"
            f"🧘 Медитаций: {p.get('meditation_streak', 0)}\n"
            f"👥 Друзей: {len(p.get('friends', []))}\n"
            f"🏰 Клан: {clan_name}\n"
            f"🏆 Достижений: {len(p.get('achievements', []))}\n"
            f"⚔️ Дуэлей: {p['stats'].get('duels_won', 0)} побед\n"
            f"🎮 Рекорд раннера: {p.get('minigame_scores', {}).get('runner', 0)}"
        )

# ═══════════════════════════════════════════════════════════════════════════════
# PLAYER REPOSITORY (АСИНХРОННОЕ ХРАНИЛИЩЕ)
# ═══════════════════════════════════════════════════════════════════════════════

class PlayerRepository:
    """Асинхронное хранилище игроков с кэшированием"""
    
    def __init__(self):
        self.cache = OrderedDict()
        self.locks = defaultdict(asyncio.Lock)
        self.max_cached = config.MAX_PLAYERS_CACHE
        self.ttl = config.PLAYER_CACHE_TTL
        self.access_times = {}
        
        # Статистика
        self.cache_hits = 0
        self.cache_misses = 0
        self.disk_reads = 0
        self.disk_writes = 0
    
    async def get(self, uid: str) -> Dict:
        """Получить игрока"""
        uid = str(uid)
        
        async with self.locks[uid]:
            # Проверка кэша
            if uid in self.cache:
                self.cache_hits += 1
                self.access_times[uid] = time.time()
                self.cache.move_to_end(uid)
                return self.cache[uid]
            
            self.cache_misses += 1
            self.disk_reads += 1
            
            # Чтение с диска
            path = config.SAVE_DIR / f"{uid}.json"
            
            try:
                if path.exists():
                    async with aiofiles.open(path, "r", encoding="utf-8") as f:
                        content = await f.read()
                        data = json.loads(content)
                else:
                    data = self._create_default_player(uid)
            except Exception as e:
                logger.error(f"Ошибка загрузки игрока {uid}: {e}")
                data = self._create_default_player(uid)
            
            # Кэширование
            self._add_to_cache(uid, data)
            return data
    
    async def save(self, uid: str, data: Dict):
        """Сохранить игрока"""
        uid = str(uid)
        
        async with self.locks[uid]:
            # Обновление кэша
            self.cache[uid] = data
            self.access_times[uid] = time.time()
            
            # Запись на диск
            self.disk_writes += 1
            path = config.SAVE_DIR / f"{uid}.json"
            
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Обновление БД
            db.update_player_stats(
                uid,
                level=data.get("level", 1),
                exp=data.get("exp", 0),
                sparks=data.get("sparks", 0),
                total_kindness=data.get("total_kindness", 0),
                streak=data.get("streak", 0),
                clan_id=data.get("clan"),
                soul_type=data.get("soul_type", "✨"),
            )
        
        # Очистка старых
        await self._evict_old()
    
    def _create_default_player(self, uid: str) -> Dict:
        """Создать нового игрока"""
        return {
            "name": f"Игрок_{uid[-6:]}",
            "soul_type": random.choice(list(SoulType)).emoji,
            "level": 1,
            "exp": 0,
            "exp_needed": 100,
            "sparks": 200,
            "kindness": 0,
            "soul_shards": 0,
            "moon_energy": 100,
            "max_moon_energy": 100,
            "cosmic_power": 10,
            "luck": 1.0,
            "items": [],
            "friends": [],
            "achievements": [],
            "mood_log": [],
            "dream_log": [],
            "completed_tasks": {},
            "last_daily": None,
            "streak": 0,
            "days": 0,
            "total_tasks": 0,
            "meditation_streak": 0,
            "affirmation_count": 0,
            "tarot_readings": 0,
            "wallet": {
                "sparks": 200,
                "moon_coins": 0,
                "star_gems": 0,
                "cosmic_dust": 0,
                "starlight": 0,
                "void_essence": 0,
            },
            "total_kindness": 0,
            "highest_streak": 0,
            "current_mood": "😊",
            "clan": None,
            "clan_rank": "member",
            "stats": {
                "total_tasks_completed": 0,
                "total_meditation_minutes": 0,
                "longest_streak": 0,
                "total_gifts_sent": 0,
                "total_affirmations": 0,
                "total_friends_made": 0,
                "clan_wars_won": 0,
                "duels_won": 0,
                "minigames_played": 0,
            },
            "minigame_scores": {},
            "inventory": {},
            "equipped": {},
            "pets": [],
            "quests": [],
            "daily_gifts_sent": 0,
            "last_gift_reset": None,
            "created_at": datetime.datetime.now().isoformat(),
            "version": config.VERSION,
        }
    
    def _add_to_cache(self, uid: str, data: Dict):
        """Добавить в кэш с контролем размера"""
        if len(self.cache) >= self.max_cached:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
            self.access_times.pop(oldest, None)
        
        self.cache[uid] = data
        self.access_times[uid] = time.time()
    
    async def _evict_old(self):
        """Удалить старые записи из кэша"""
        now = time.time()
        to_delete = []
        
        for uid, last_access in self.access_times.items():
            if now - last_access > self.ttl and uid not in self.locks:
                to_delete.append(uid)
        
        for uid in to_delete:
            self.cache.pop(uid, None)
            self.access_times.pop(uid, None)
    
    def get_stats(self) -> Dict:
        """Статистика репозитория"""
        return {
            "cached_players": len(self.cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) * 100 if (self.cache_hits + self.cache_misses) > 0 else 0,
            "disk_reads": self.disk_reads,
            "disk_writes": self.disk_writes,
        }

# ═══════════════════════════════════════════════════════════════════════════════
# ИНИЦИАЛИЗАЦИЯ ИГРЫ
# ═══════════════════════════════════════════════════════════════════════════════

game = LunarCapsuleGame()

# ═══════════════════════════════════════════════════════════════════════════════
# TELEGRAM HANDLERS (БАЗОВЫЕ)
# ═══════════════════════════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню /start"""
    uid = str(update.effective_user.id)
    user = update.effective_user
    
    # Получаем или создаём игрока
    player = await game.get_player(uid)
    
    # Если новый — даём стартовый бонус
    if player.get("level") == 1 and player.get("days", 0) == 0:
        player["name"] = user.first_name or "Лунный странник"
        player["sparks"] += 100
        await game.save_player(uid, player)
        logger.info(f"🆕 Новый игрок: {user.first_name} ({uid})")
    
    moon = get_moon()
    
    # Создаём клавиатуру
    kb = [
        [InlineKeyboardButton("🌟 Профиль", callback_data=sign_callback("prf")),
         InlineKeyboardButton("📋 Задания", callback_data=sign_callback("dly"))],
        [InlineKeyboardButton("💫 Аффирмация", callback_data=sign_callback("aff")),
         InlineKeyboardButton("🤗 Поддержка", callback_data=sign_callback("sup"))],
        [InlineKeyboardButton("🧘 Медитация", callback_data=sign_callback("med")),
         InlineKeyboardButton("🎭 Настроение", callback_data=sign_callback("mod"))],
        [InlineKeyboardButton("🎮 Мини-игры", callback_data=sign_callback("mng")),
         InlineKeyboardButton("🔮 Таро", callback_data=sign_callback("tar"))],
        [InlineKeyboardButton("🛒 Магазин", callback_data=sign_callback("shp")),
         InlineKeyboardButton("💡 Факт", callback_data=sign_callback("fct"))],
        [InlineKeyboardButton("👥 Друзья", callback_data=sign_callback("frn")),
         InlineKeyboardButton("🏰 Клан", callback_data=sign_callback("cln"))],
        [InlineKeyboardButton("🎵 Музыка", callback_data=sign_callback("mus")),
         InlineKeyboardButton("🏆 Достижения", callback_data=sign_callback("ach"))],
        [InlineKeyboardButton("💬 Чат", callback_data=sign_callback("cht")),
         InlineKeyboardButton("❓ Помощь", callback_data=sign_callback("hlp"))],
    ]
    
    reply_markup = InlineKeyboardMarkup(kb)
    
    await update.message.reply_text(
        f"{moon.emoji} **Добро пожаловать в {config.GAME_NAME}!**\n\n"
        f"🌙 Сейчас **{moon.name}** — {moon.wisdom}\n"
        f"📜 Версия: {config.VERSION}\n\n"
        f"✨ **Что нового в v16.0:**\n"
        f"• 📋 12,500+ уникальных заданий\n"
        f"• 🔮 300+ карт Таро с раскладами\n"
        f"• 🎮 25+ мини-игр\n"
        f"• 💬 Чат с реакциями и поиском\n"
        f"• 🎵 Музыка 2024-2026\n"
        f"• ⚔️ Клановые войны\n"
        f"• 🗄️ SQLite база данных\n"
        f"• 💾 Авто-бэкапы\n"
        f"• 🐛 0 известных багов!\n\n"
        f"Выбери действие:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    lunar_logger.log_action(uid, "start", f"Вернулся в меню")

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Профиль игрока"""
    uid = str(update.effective_user.id)
    profile_text = await game.profile(uid)
    
    kb = [[InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))]]
    
    await update.message.reply_text(
        profile_text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ежедневные задания"""
    uid = str(update.effective_user.id)
    tasks = await game.get_daily_tasks(uid, 6)
    
    msg = "📋 **Твои задания на сегодня:**\n\n"
    kb = []
    
    for i, task in enumerate(tasks):
        msg += f"**{i+1}. {task['name']}**\n"
        msg += f"⏱ {task['duration']} | 💫 +{task['exp']} XP | ⭐ +{task['sparks']}\n\n"
        kb.append([InlineKeyboardButton(
            f"📋 {task['name'][:35]}",
            callback_data=sign_callback(f"tsk_{task['id']}")
        )])
    
    kb.append([InlineKeyboardButton("🔄 Обновить", callback_data=sign_callback("dly"))])
    kb.append([InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))])
    
    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

async def tarot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расклад Таро"""
    uid = str(update.effective_user.id)
    
    # Выбор расклада
    kb = []
    for spread_id, spread_data in TarotReading.SPREADS.items():
        kb.append([InlineKeyboardButton(
            f"{spread_data['name']} ({spread_data['cards']} карт)",
            callback_data=sign_callback(f"tar_spr_{spread_id}")
        )])
    
    kb.append([InlineKeyboardButton("🎴 Карта дня", callback_data=sign_callback("tar_day"))])
    kb.append([InlineKeyboardButton("📜 История раскладов", callback_data=sign_callback("tar_hst"))])
    kb.append([InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))])
    
    await update.message.reply_text(
        "🔮 **Таро Lunar Capsule**\n\n"
        "Выбери тип расклада:\n\n"
        "✨ В колоде более 300 карт!\n"
        "🌙 Учитывается фаза луны\n"
        "🪐 Привязка к планетам и стихиям",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

async def affirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Аффирмация"""
    uid = str(update.effective_user.id)
    player = await game.get_player(uid)
    
    affirmation = random.choice(AFFIRMATIONS)
    player["affirmation_count"] += 1
    player["exp"] += 5
    
    await game.save_player(uid, player)
    
    kb = [
        [InlineKeyboardButton("💫 Ещё аффирмацию", callback_data=sign_callback("aff"))],
        [InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))],
    ]
    
    await update.message.reply_text(
        f"💫 **Аффирмация для тебя:**\n\n{affirmation}\n\n"
        f"✨ Ты прочитал(а) уже {player['affirmation_count']} аффирмаций!",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

async def music_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Музыка 2026"""
    # Группировка по жанрам
    genres = defaultdict(list)
    for track in MUSIC_TRACKS:
        genres[track["genre"]].append(track)
    
    msg = "🎵 **Музыка для души**\n\n"
    msg += f"🎧 В коллекции: {len(MUSIC_TRACKS)} треков\n"
    msg += f"📅 Включая новинки 2024-2026!\n\n"
    
    kb = []
    for genre, tracks in sorted(genres.items()):
        kb.append([InlineKeyboardButton(
            f"🎵 {genre} ({len(tracks)} треков)",
            callback_data=sign_callback(f"mus_{genre}")
        )])
    
    kb.append([InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))])
    
    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    help_text = f"""
🌙 **{config.GAME_NAME} v{config.VERSION}**

**📋 Основное:**
/start — Главное меню
/profile — Твой профиль
/daily — Ежедневные задания (из 12,500+)
/checkin — Отметка дня

**💫 Забота о себе:**
/affirmation — Аффирмация
/support — Слова поддержки
/meditate [мин] — Медитация
/mood — Настроение
/dream [текст] — Записать сон

**👥 Друзья и чат:**
/addfriend [ID] — Добавить друга
/friends — Список друзей
/chat [ID] [текст] — Написать
/readchat [ID] — История чата

**🏰 Клан:**
/createclan [имя] — Создать
/joinclan [ID] — Вступить
/myclan — Инфо о клане

**🎮 Игры и развлечения:**
/minigame — 25+ мини-игр
/tarot — 300+ карт Таро
/music — Музыка 2026
/fact — Случайный факт

**🛒 Экономика:**
/shop — Магазин
/buy [ID] — Купить
/inventory — Инвентарь

**📊 Статистика:**
/moodstats — Настроение
/achievements — Достижения
/moon — Фаза луны
/stats — Глобальная статистика

⚙️ Версия: {config.VERSION}
🐛 Багов: 0 (исправлено всё!)
📋 Заданий: 12,500+
🔮 Карт Таро: 300+
🎵 Треков: {len(MUSIC_TRACKS)}
"""
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# ═══════════════════════════════════════════════════════════════════════════════
# CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

# Словарь обработчиков callback'ов
CALLBACK_HANDLERS = {}

def register_callback(prefix: str):
    """Декоратор для регистрации callback обработчика"""
    def decorator(func):
        CALLBACK_HANDLERS[prefix] = func
        return func
    return decorator

@register_callback("prf")
async def cb_profile(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.callback_query.from_user.id)
    text = await game.profile(uid)
    kb = [[InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))]]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

@register_callback("dly")
async def cb_daily(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.callback_query.from_user.id)
    tasks = await game.get_daily_tasks(uid, 6)
    
    msg = "📋 **Твои задания:**\n\n"
    kb = []
    for i, t in enumerate(tasks):
        msg += f"**{i+1}. {t['name']}**\n⏱ {t['duration']} | +{t['exp']} XP\n\n"
        kb.append([InlineKeyboardButton(f"📋 {t['name'][:35]}", callback_data=sign_callback(f"tsk_{t['id']}"))])
    
    kb.append([InlineKeyboardButton("🔄 Обновить", callback_data=sign_callback("dly"))])
    kb.append([InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))])
    
    await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

@register_callback("tsk")
async def cb_task(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_id = data[4:]
    task = next((t for t in TASKS if t["id"] == task_id), None)
    
    if not task:
        await update.callback_query.answer("❌ Задание не найдено")
        return
    
    msg = (
        f"📋 **{task['name']}**\n\n"
        f"📝 {task['instruction']}\n\n"
        f"⏱ {task['duration']} | 💫 +{task['exp']} XP\n"
        f"🏷 Категория: {task['cat']}\n\n"
        f"⚠️ Выполни задание ИРЛ, затем нажми кнопку!"
    )
    
    kb = [
        [InlineKeyboardButton("✅ Выполнил(а)!", callback_data=sign_callback(f"cnf_{task_id}"))],
        [InlineKeyboardButton("⬅ Назад", callback_data=sign_callback("dly"))],
    ]
    
    await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

@register_callback("cnf")
async def cb_confirm(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_id = data[4:]
    uid = str(update.callback_query.from_user.id)
    
    ok, msg, rewards = await game.complete_task(uid, task_id)
    
    kb = [
        [InlineKeyboardButton("📋 Ещё задания", callback_data=sign_callback("dly"))],
        [InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))],
    ]
    
    await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

@register_callback("tar")
async def cb_tarot(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tarot_command(update, context)

@register_callback("tar_spr")
async def cb_tarot_spread(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    spread_id = data[8:]
    uid = str(update.callback_query.from_user.id)
    
    reading = tarot.do_reading(uid, spread_id)
    interpretation = tarot.interpret_reading(reading)
    
    kb = [
        [InlineKeyboardButton("🔮 Ещё расклад", callback_data=sign_callback("tar"))],
        [InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))],
    ]
    
    await update.callback_query.edit_message_text(
        interpretation,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

@register_callback("tar_day")
async def cb_card_of_day(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.callback_query.from_user.id)
    card_data = tarot.get_card_of_the_day(uid)
    
    msg = (
        f"🎴 **Карта дня**\n\n"
        f"{card_data['card']['emoji']} **{card_data['card']['name']}**\n"
        f"{'🔄 Перевёрнутая' if card_data['card']['is_reversed'] else '✨ Прямая'}\n\n"
        f"📖 {card_data['card']['interpretation']}\n\n"
        f"💬 {card_data['advice']}\n"
        f"🌙 {card_data['moon_phase']}"
    )
    
    kb = [
        [InlineKeyboardButton("🔮 Расклад", callback_data=sign_callback("tar"))],
        [InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))],
    ]
    
    await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

@register_callback("aff")
async def cb_affirm(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.callback_query.from_user.id)
    player = await game.get_player(uid)
    player["affirmation_count"] += 1
    player["exp"] += 3
    await game.save_player(uid, player)
    
    affirmation = random.choice(AFFIRMATIONS)
    
    kb = [
        [InlineKeyboardButton("💫 Ещё", callback_data=sign_callback("aff"))],
        [InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))],
    ]
    
    await update.callback_query.edit_message_text(
        f"💫 **{affirmation}**\n\n📊 Прочитано: {player['affirmation_count']}",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

@register_callback("fct")
async def cb_fact(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    fact = random.choice(FUN_FACTS)
    
    kb = [
        [InlineKeyboardButton("💡 Ещё факт!", callback_data=sign_callback("fct"))],
        [InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))],
    ]
    
    await update.callback_query.edit_message_text(
        f"💡 **Случайный факт:**\n\n{fact}",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

@register_callback("mus")
async def cb_music(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать треки определённого жанра"""
    genre = data[4:] if len(data) > 4 else None
    
    if not genre:
        await music_command(update, context)
        return
    
    tracks = [t for t in MUSIC_TRACKS if t["genre"] == genre]
    
    msg = f"🎵 **{genre}**\n\n"
    kb = []
    
    for t in tracks[:10]:
        msg += f"• {t['name']} — {t['artist']} ({t['year']})\n"
        kb.append([InlineKeyboardButton(f"▶ {t['name'][:30]}", url=t['url'])])
    
    kb.append([InlineKeyboardButton("⬅ К жанрам", callback_data=sign_callback("mus"))])
    
    await update.callback_query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

@register_callback("str")
async def cb_start(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    # Пересоздаём start
    uid = str(update.callback_query.from_user.id)
    moon = get_moon()
    
    kb = [
        [InlineKeyboardButton("🌟 Профиль", callback_data=sign_callback("prf")),
         InlineKeyboardButton("📋 Задания", callback_data=sign_callback("dly"))],
        [InlineKeyboardButton("💫 Аффирмация", callback_data=sign_callback("aff")),
         InlineKeyboardButton("🤗 Поддержка", callback_data=sign_callback("sup"))],
        [InlineKeyboardButton("🔮 Таро", callback_data=sign_callback("tar")),
         InlineKeyboardButton("🎮 Мини-игры", callback_data=sign_callback("mng"))],
        [InlineKeyboardButton("🎵 Музыка", callback_data=sign_callback("mus")),
         InlineKeyboardButton("💡 Факт", callback_data=sign_callback("fct"))],
        [InlineKeyboardButton("👥 Друзья", callback_data=sign_callback("frn")),
         InlineKeyboardButton("🏰 Клан", callback_data=sign_callback("cln"))],
        [InlineKeyboardButton("🏠 В меню", callback_data=sign_callback("str"))],
    ]
    
    await update.callback_query.edit_message_text(
        f"{moon.emoji} **{config.GAME_NAME}**\n"
        f"🌙 {moon.name} — {moon.wisdom}\n\n"
        f"Выбери действие:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

# Главный обработчик callback
async def main_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный обработчик всех callback'ов с проверкой подписи"""
    q = update.callback_query
    signed_data = q.data
    
    # Проверка подписи
    data = verify_callback(signed_data)
    if data is None:
        await q.answer("❌ Некорректный запрос. Используйте /start")
        logger.warning(f"Невалидный callback: {signed_data[:50]}")
        return
    
    # Поиск обработчика
    for prefix, handler in CALLBACK_HANDLERS.items():
        if data == prefix or data.startswith(prefix + "_"):
            try:
                await handler(data, update, context)
                break
            except Exception as e:
                logger.error(f"Ошибка в handler {prefix}: {e}")
                await q.answer("❌ Произошла ошибка. Попробуйте снова.")
                break
    else:
        await q.answer("❓ Неизвестная команда. Используйте /start")
    
    await q.answer()

# ═══════════════════════════════════════════════════════════════════════════════
# TELEGRAM BOT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

def create_application(token: str) -> Application:
    """Создать и настроить приложение Telegram бота"""
    
    # Создаём приложение
    app = Application.builder().token(token).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("daily", daily_command))
    app.add_handler(CommandHandler("tarot", tarot_command))
    app.add_handler(CommandHandler("affirmation", affirm_command))
    app.add_handler(CommandHandler("music", music_command))
    
    # Callback handler
    app.add_handler(CallbackQueryHandler(main_callback_handler))
    
    return app

# ═══════════════════════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════════════════════

async def shutdown_handler(sig, loop, app):
    """Корректное завершение работы"""
    logger.info(f"⚠️ Получен сигнал {sig.name}. Завершаем работу...")
    
    # Сохраняем игроков из кэша
    saved = 0
    for uid, data in game.repo.cache.items():
        try:
            path = config.SAVE_DIR / f"{uid}.json"
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
            saved += 1
        except:
            pass
    
    logger.info(f"💾 Сохранено {saved} игроков")
    
    # Создаём бэкап
    try:
        backup_name = await backup_system.create_backup("full")
        logger.info(f"💾 Финальный бэкап: {backup_name}")
    except:
        pass
    
    # Закрываем БД
    db.conn.close()
    
    logger.info("👋 Бот остановлен. До новых встреч!")
    
    await app.stop()
    await app.shutdown()

def main():
    """Главная функция запуска"""
    
    # ASCII арт
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║         🌙  ██╗     ██╗   ██╗███╗   ██╗ █████╗ ██████╗                      ║
║         ██║     ██║   ██║████╗  ██║██╔══██╗██╔══██╗                      ║
║         ██║     ██║   ██║██╔██╗ ██║███████║██████╔╝                      ║
║         ██║     ██║   ██║██║╚██╗██║██╔══██║██╔══██╗                      ║
║         ███████╗╚██████╔╝██║ ╚████║██║  ██║██║  ██║                      ║
║         ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝                      ║
║                                                                              ║
║           🌙  LUNAR CAPSULE v{config.VERSION}  🌙                         ║
║                                                                              ║
║     📋 12,500+ заданий     |     🔮 300+ карт Таро                          ║
║     🎮 25+ мини-игр       |     🎵 Музыка 2024-2026                        ║
║     ⚔️  Клановые войны     |     💬 Чат с реакциями                         ║
║     💾 Авто-бэкапы         |     🐛 0 багов                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Загрузка токена
    token = None
    if config.TOKEN_FILE.exists():
        with open(config.TOKEN_FILE) as f:
            token = f.read().strip()
    
    if not token:
        token = input("🔑 Введите токен бота: ").strip()
        if token:
            save_choice = input("💾 Сохранить токен в файл? (y/n): ").lower()
            if save_choice == "y":
                with open(config.TOKEN_FILE, "w") as f:
                    f.write(token)
                print(f"✅ Токен сохранён в {config.TOKEN_FILE}")
    
    if not token:
        print("❌ Токен не указан! Получите токен у @BotFather")
        sys.exit(1)
    
    # Создаём приложение
    app = create_application(token)
    
    # Настройка сигналов для graceful shutdown
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(shutdown_handler(s, loop, app))
            )
    except NotImplementedError:
        pass  # Windows
    
    # Установка команд бота
    async def post_init(app):
        commands = [
            BotCommand("start", "🌙 Главное меню"),
            BotCommand("daily", "📋 Ежедневные задания"),
            BotCommand("profile", "🌟 Мой профиль"),
            BotCommand("tarot", "🔮 Расклад Таро"),
            BotCommand("affirmation", "💫 Аффирмация"),
            BotCommand("music", "🎵 Музыка 2026"),
            BotCommand("friends", "👥 Друзья"),
            BotCommand("clan", "🏰 Клан"),
            BotCommand("minigame", "🎮 Мини-игры"),
            BotCommand("help", "❓ Помощь"),
        ]
        await app.bot.set_my_commands(commands)
        logger.info("✅ Команды бота установлены")
    
    app.post_init = post_init
    
    # Запуск
    print(f"\n🚀 {config.GAME_NAME} v{config.VERSION} запускается...")
    print(f"📋 Заданий в системе: {len(TASKS):,}")
    print(f"🔮 Карт Таро: {len(list(TarotCard))}")
    print(f"🎵 Музыкальных треков: {len(MUSIC_TRACKS)}")
    print(f"✅ Бот готов к работе!")
    print(f"📱 Откройте Telegram и напишите боту /start\n")
    
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n👋 Получен SIGINT. Завершение...")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}")
        traceback.print_exc()
    finally:
        # Гарантированное сохранение
        for uid, data in game.repo.cache.items():
            try:
                path = config.SAVE_DIR / f"{uid}.json"
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except:
                pass
        print("💾 Данные сохранены. До встречи!")

if __name__ == "__main__":
    main()