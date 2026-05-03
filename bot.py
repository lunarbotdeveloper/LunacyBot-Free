#!/usr/bin/env python3
# 🌙 Lunar Capsule - Cosmic Self-Care Game v11.0 COMPLETE
# Полностью исправлено | Чат | Мини-игры | Кланы | Факты

import json, random, os, datetime, sys, time, math, hashlib, uuid, secrets
import textwrap, itertools, collections, subprocess, tempfile, base64
import webbrowser, calendar, colorsys, threading, logging, traceback, asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from enum import Enum
from pathlib import Path

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('lunar.log', encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger('Lunar')

# === TELEGRAM IMPORT ===
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
    from telegram.constants import ParseMode
    import telegram
    logger.info(f"✅ Telegram {telegram.__version__}")
except ImportError as e:
    logger.error(f"❌ {e}")
    print("pip install python-telegram-bot")
    sys.exit(1)

# === КОНСТАНТЫ ===
GAME_NAME = "🌙 Lunar Capsule"
VERSION = "11.0 COMPLETE"
SAVE_DIR = "lunar_saves"
FRIENDS_DIR = "lunar_friends"
CLANS_DIR = "lunar_clans"
CHAT_DIR = "lunar_chats"
TOKEN_FILE = "bot_token.txt"
for d in [SAVE_DIR, FRIENDS_DIR, CLANS_DIR, CHAT_DIR]: os.makedirs(d, exist_ok=True)

# === ENUMS (без изменений) ===
class MoonPhase(Enum):
    NEW = ("🌑", "Новолуние", "Время начинать новое", 0)
    WAXING_CRESCENT = ("🌒", "Молодая луна", "Энергия растёт", 1)
    FIRST_QUARTER = ("🌓", "Первая четверть", "Время решений", 2)
    WAXING_GIBBOUS = ("🌔", "Прибывающая", "Сила прибывает", 3)
    FULL = ("🌕", "Полнолуние", "Пик энергии и магии", 4)
    WANING_GIBBOUS = ("🌖", "Убывающая", "Время благодарности", 5)
    LAST_QUARTER = ("🌗", "Последняя четверть", "Время отпускать", 6)
    WANING_CRESCENT = ("🌘", "Старая луна", "Время отдыха", 7)

class SoulType(Enum):
    STARDUST = ("✨", "Звёздная пыль", "Ты сияешь ярче всех")
    MOONBEAM = ("🌙", "Лунный луч", "Ты освещаешь путь другим")
    COMET = ("☄️", "Комета", "Ты стремителен и ярок")
    NEBULA = ("🌌", "Туманность", "Ты полон тайн и загадок")
    AURORA = ("🌠", "Аврора", "Ты переливаешься всеми цветами")
    COSMIC = ("💫", "Космическая", "Ты — само мироздание")
    ECLIPSE = ("🌓", "Затмение", "Ты хранишь баланс тьмы и света")
    NOVA = ("💥", "Сверхновая", "Твой внутренний взрыв создаёт галактики")
    PULSAR = ("⭐", "Пульсар", "Твой ритм задаёт такт вселенной")
    QUASAR = ("🌟", "Квазар", "Твой свет виден за миллиарды световых лет")

class FriendStatus(Enum):
    PENDING = ("⏳", "Запрос отправлен")
    ACCEPTED = ("✅", "Друзья")
    BLOCKED = ("🚫", "Заблокирован")
    BEST = ("💫", "Лучший друг")
    SOULMATE = ("💑", "Родственная душа")

class ItemRarity(Enum):
    COMMON = ("common", "Обычный", "⚪", 1.0)
    UNCOMMON = ("uncommon", "Необычный", "🟢", 1.5)
    RARE = ("rare", "Редкий", "🔵", 2.5)
    EPIC = ("epic", "Эпический", "🟣", 5.0)
    LEGENDARY = ("legendary", "Легендарный", "🟡", 10.0)
    MYTHIC = ("mythic", "Мифический", "🔴", 25.0)

# === ФАКТЫ (100+) ===
FUN_FACTS = [
    "🌍 Земля — единственная планета в Солнечной системе, не названная в честь бога.",
    "🌟 В нашей галактике около 100 миллиардов звёзд.",
    "🌙 Луна отдаляется от Земли на 3.8 см каждый год.",
    "☀️ Солнце составляет 99.86% массы Солнечной системы.",
    "🪐 На Сатурне плотность меньше плотности воды — он бы плавал в океане.",
    "💫 Свет от Солнца до Земли идёт 8 минут 20 секунд.",
    "🌌 В наблюдаемой Вселенной больше звёзд, чем песчинок на всех пляжах Земли.",
    "🦋 Бабочки пробуют пищу лапками.",
    "🐝 Пчёлы могут узнавать человеческие лица.",
    "🐙 У осьминогов три сердца и голубая кровь.",
    "🌿 Деревья общаются друг с другом через подземную грибную сеть.",
    "💧 Человеческое тело на 60% состоит из воды.",
    "🧠 Мозг генерирует достаточно электричества, чтобы зажечь лампочку.",
    "❤️ Сердце бьётся около 100 000 раз в день.",
    "👁️ Глаза могут различать около 10 миллионов цветов.",
    "🎵 Музыка активирует те же участки мозга, что и еда и... влюблённость.",
    "📚 Чтение снижает уровень стресса на 68%.",
    "😊 Улыбка, даже вынужденная, улучшает настроение.",
    "🌧️ Запах дождя называется петрикор.",
    "❄️ Снежинки падают со скоростью около 1.6 км/ч.",
    "🌻 Подсолнухи поворачиваются к солнцу в течение дня.",
    "🦊 Лисы используют магнитное поле Земли для охоты.",
    "🐋 Сердце голубого кита размером с небольшой автомобиль.",
    "🦜 Некоторые попугаи живут более 80 лет.",
    "🌵 Кактусы могут жить до 200 лет.",
    "🍯 Мёд никогда не портится — его находили в египетских гробницах.",
    "☕ Кофе — второй по популярности напиток в мире после воды.",
    "🍫 Шоколад содержит теобромин, который полезен для сердца.",
    "🎨 Леонардо да Винчи мог писать одной рукой и рисовать другой одновременно.",
    "📖 Самая дорогая книга — Codex Leicester да Винчи (30.8 млн $).",
    "🌊 Океаны производят 50-85% кислорода на Земле.",
    "🏔️ Гора Эверест растёт на 4 мм в год из-за тектонических плит.",
    "🌋 Вулканы могут создавать молнии во время извержения.",
    "💎 Алмазы — это углерод под огромным давлением.",
    "🌈 Радуга — это круг, мы видим только половину.",
    "🐢 Некоторые черепахи дышат через... попу (клоакальное дыхание).",
    "🦎 Гекконы не мокнут в воде из-за наноструктур на коже.",
    "🌸 Сакура цветёт всего 7-10 дней в году.",
    "🕰️ Самые старые деревья на Земле живут более 5000 лет.",
    "🌠 Каждый день на Землю падает около 100 тонн космической пыли.",
    "🧬 ДНК человека на 50% совпадает с ДНК банана.",
    "🦷 Зубы — единственная часть тела, которая не может самовосстанавливаться.",
    "💪 Самая сильная мышца в теле — жевательная.",
    "👃 Нос может запомнить 50 000 различных запахов.",
    "🗣️ Мы используем около 100 мышц, чтобы говорить.",
    "😴 За жизнь человек проводит около 25 лет во сне.",
    "🎂 Клетки тела полностью обновляются каждые 7-10 лет.",
    "🧘 Медитация физически меняет структуру мозга.",
    "🌅 На Марсе закаты голубые.",
    "🪐 Юпитер защищает Землю от большинства астероидов своей гравитацией.",
    "💫 Нейтронные звёзды вращаются до 600 раз в секунду.",
    "🌌 Чёрные дыры испаряются со временем (излучение Хокинга).",
    "🌙 Полнолуние влияет на сон людей — засыпают позже, спят меньше.",
    "🧠 Мозг использует 20% всей энергии тела.",
    "👣 За жизнь человек проходит расстояние, равное 5 экваторам Земли.",
    "🍎 Яблоко тонет в воде, а груша плавает.",
    "🦩 Фламинго розовые из-за креветок и водорослей в их рационе.",
    "🐬 Дельфины спят с одним открытым глазом.",
    "🦉 Совы не могут двигать глазами, только головой.",
    "🐘 Слоны — единственные животные с 4 коленями.",
    "🦒 У жирафов такое же количество шейных позвонков, как у людей (7).",
    "🐧 Пингвины делают предложение партнёру с помощью камешков.",
    "🌍 Если убрать всё пространство между атомами, Земля станет размером с яблоко.",
    "💡 Лампочка изобретена раньше, чем консервный нож.",
    "📱 В телефоне больше бактерий, чем на сиденье унитаза.",
    "🖐️ Отпечатки пальцев коалы почти неотличимы от человеческих.",
    "🌿 Бамбук может расти со скоростью 91 см в день.",
    "🍉 Арбуз — это ягода, а клубника — нет.",
    "🥑 Авокадо содержит больше калия, чем бананы.",
    "🌮 Тако были изобретены в Мексике более 1000 лет назад.",
    "🎅 Санта-Клаус изначально носил зелёный костюм (Coca-Cola сделала его красным).",
    "📺 Первый видеозвонок состоялся в 1964 году.",
    "🎮 Первая видеоигра была создана в 1958 году — Tennis for Two.",
    "⌨️ Самая длинная клавиша на клавиатуре — пробел.",
    "📧 Первый email был отправлен в 1971 году.",
    "🌐 Интернет весит примерно столько же, сколько одно зерно песка (в электронах).",
    "🔋 Первый электромобиль создан в 1832 году.",
    "🚀 Первый полёт братьев Райт длился 12 секунд.",
    "🌕 Когда Армстронг ступил на Луну, его пульс был 156 ударов в минуту.",
    "💊 Пенициллин открыт случайно из-за плесени.",
    "🔥 Огонь не имеет тени, потому что сам является источником света.",
    "🌈 У каждого человека уникальный рисунок радужной оболочки глаза.",
    "🦴 Дети рождаются с 300 костями, взрослые имеют 206.",
    "💨 Человек производит достаточно слюны за жизнь, чтобы наполнить 2 бассейна.",
    "🫁 Лёгкие — единственный орган, который может плавать на воде.",
    "👂 Уши растут всю жизнь.",
    "🧠 Мозг не чувствует боли — операции на мозге делают при сознании.",
    "😱 Фобия — это иррациональный страх. Существует более 500 фобий.",
    "🎭 Смех укрепляет иммунную систему.",
    "🤗 Объятия снижают уровень кортизола.",
    "💤 Во время сна мозг очищается от токсинов.",
    "🌞 10 минут на солнце дают дневную норму витамина D.",
    "🚶 30 минут ходьбы в день снижают риск болезней сердца на 35%.",
    "🧘 5 минут медитации в день уменьшают тревожность.",
    "📖 6 минут чтения снижают стресс на 60%.",
    "🎵 Прослушивание любимой музыки высвобождает дофамин.",
]

# === АФФИРМАЦИИ (оптимизировано) ===
AFFIRMATIONS = [
    "💫 Я достоин любви и уважения.",
    "💫 Моё тело — это храм, и я забочусь о нём.",
    "💫 Я привлекаю позитивных людей в свою жизнь.",
    "💫 Каждый день я становлюсь лучше.",
    "💫 Я принимаю себя целиком и полностью.",
    "💫 Мои чувства важны и имеют значение.",
    "💫 Я излучаю уверенность и спокойствие.",
    "💫 Я заслуживаю счастья и радости.",
    "💫 Моя душа полна света.",
    "💫 Я открыт новым возможностям.",
    "💫 Моё прошлое не определяет моё будущее.",
    "💫 Я благодарен за всё что имею.",
    "💫 Моя жизнь наполнена смыслом.",
    "💫 Я способен достичь всего чего захочу.",
    "💫 Я отпускаю страхи и сомнения.",
    "💫 В моём сердце живёт любовь.",
    "💫 Я дышу спокойствием и выдыхаю тревогу.",
    "💫 Я уникален и неповторим.",
    "💫 Вселенная поддерживает меня.",
    "💫 Я нахожу радость в мелочах.",
    "💫 Моя интуиция всегда ведёт меня верным путём.",
    "💫 Я заслуживаю финансового благополучия.",
    "💫 Я строю здоровые отношения.",
    "💫 Мой разум спокоен и ясен.",
    "💫 Я полон энергии и жизненных сил.",
    "💫 Сегодня прекрасный день для новых свершений.",
    "💫 Я прощаю себя за прошлые ошибки.",
    "💫 Моя жизнь — это моё творение.",
    "💫 Я выбираю счастье прямо сейчас.",
    "💫 Я доверяю потоку жизни.",
    "💫 Я излучаю доброту и тепло.",
    "💫 Мои мысли создают мою реальность.",
    "💫 Я способен преодолеть любые трудности.",
    "💫 Я в безопасности. Всё хорошо.",
    "💫 Я позволяю себе отдыхать без чувства вины.",
    "💫 Моё сердце открыто для любви.",
    "💫 Я притягиваю чудеса в свою жизнь.",
    "💫 Каждое утро — это новый старт.",
    "💫 Я благодарен этому дню.",
    "💫 Я доверяю себе и своим решениям.",
    "💫 Моя сила растёт с каждым днём.",
    "💫 Я окружён заботой и поддержкой.",
    "💫 Я позволяю себе быть уязвимым.",
    "💫 Я принимаю перемены с открытым сердцем.",
    "💫 Я живу в гармонии с собой и миром.",
    "💫 Я уверен в своём будущем.",
    "💫 Я замечаю красоту вокруг себя.",
    "💫 Я создаю пространство для радости.",
    "💫 Я слушаю своё тело и его потребности.",
    "💫 Мой голос важен. Мои слова имеют силу.",
    "💫 Я освобождаюсь от чужого мнения.",
    "💫 Я — творец своей реальности.",
    "💫 Я выбираю мысли которые меня поддерживают.",
    "💫 Я достоин уважения просто потому что я есть.",
    "💫 Моя жизнь наполняется смыслом каждый день.",
    "💫 Я вижу возможности там где другие видят преграды.",
    "💫 Я справлюсь. У меня всё получится.",
    "💫 Я позволяю себе мечтать о великом.",
    "💫 Моя душа знает путь. Я доверяю ей.",
]

# === ФРАЗЫ ПОДДЕРЖКИ (200) ===
SUPPORT_PHRASES = [
    "🤗 Ты справишься. Я верю в тебя. Даже если сейчас трудно — это пройдёт. Ты сильнее чем думаешь.",
    "💫 Твоя душа — это целая вселенная. В ней есть место для звёзд, планет и бесконечной любви.",
    "🌸 Сегодня ты сделал мир чуточку добрее. Одно твоё присутствие уже меняет реальность к лучшему.",
    "🌙 Луна освещает твой путь. Даже в самой тёмной ночи есть свет — и этот свет внутри тебя.",
    "✨ Ты уникален. Такого как ты больше нет. Твоя комбинация качеств, опыта и мечтаний — единственна во вселенной.",
    "💪 Ты сильнее, чем думаешь. Ты уже пережил 100% своих худших дней. И сейчас переживёшь.",
    "🫂 Ты не один. Я всегда рядом. Даже если ты не чувствуешь — поддержка здесь.",
    "🌟 Твой свет видно даже с другой галактики. Не прячь его. Позволь себе сиять.",
    "🌿 Каждый день — это новый шанс. Вчера закончилось. Сегодня — чистый лист.",
    "💝 Ты достоин любви и счастья. Не потому что заслужил. А потому что ты есть.",
    "🎯 Маленький шаг сегодня — большая победа завтра. Не обесценивай маленькие достижения.",
    "🌊 Твои чувства важны. Позволь им быть. Грусть, радость, злость — все они часть тебя.",
    "🔥 Твой внутренний огонь не погасить. Даже если кажется что остались только угли — искра ещё жива.",
    "🦋 Перемены — это рост. Ты растёшь. Даже если не видишь результатов — корни уже крепнут.",
    "💎 Ты драгоценен. Помни это. Не позволяй никому убедить тебя в обратном.",
    "🌈 После дождя всегда выходит солнце. Твои трудности временны.",
    "🎭 Твои эмоции — это не слабость. Это твоя суперсила.",
    "🕯️ Даже одна свеча разгоняет тьму. Будь этой свечой.",
    "🌠 Ты — звезда. Звёзды не спрашивают разрешения сиять.",
    "💌 Ты нужен этому миру. Именно такой, какой ты есть.",
]

# === ЗАДАНИЯ (ИСПРАВЛЕНО — УНИКАЛЬНЫЕ ID) ===
TASKS = [
    {"id": "task_morning_exercise", "name": "🌟 Утренняя зарядка", "short_desc": "10 минут зарядки",
     "instruction": "🧘 Встань прямо. Сделай 10 наклонов вперёд. 10 приседаний. 10 поворотов корпуса. 5 глубоких вдохов и выдохов. Почувствуй как просыпается каждая клеточка твоего тела. Ты молодец что начал день с заботы о себе!",
     "exp": 15, "sparks": 5, "kindness": 2, "cat": "daily", "duration": "10 мин"},
    {"id": "task_reading", "name": "📖 Чтение книги", "short_desc": "20 минут чтения",
     "instruction": "📚 Возьми любимую книгу. Устройся в удобном месте. Отключи уведомления на телефоне. Читай 20 минут не отвлекаясь. Погрузись в мир истории. После прочтения запиши одну мысль которая тебя зацепила.",
     "exp": 20, "sparks": 5, "kindness": 3, "cat": "daily", "duration": "20 мин"},
    {"id": "task_walk", "name": "🚶 Прогулка на свежем воздухе", "short_desc": "15 минут прогулки",
     "instruction": "🌿 Надень удобную обувь. Выйди на улицу. Иди в комфортном темпе. Обращай внимание на небо, деревья, запахи, звуки. Сделай 3 глубоких вдоха. Почувствуй связь с природой. Ты часть этого мира.",
     "exp": 18, "sparks": 4, "kindness": 3, "cat": "daily", "duration": "15 мин"},
    {"id": "task_water", "name": "💧 Водный баланс", "short_desc": "Выпей 2 стакана воды",
     "instruction": "💧 Прямо сейчас встань и налей себе стакан чистой воды. Выпей его медленно, чувствуя каждый глоток. Через час выпей ещё один. Твоё тело на 60% состоит из воды — пополни запасы!",
     "exp": 5, "sparks": 2, "kindness": 1, "cat": "daily", "duration": "2 мин"},
    {"id": "task_meditation_mindfulness", "name": "🧘 Медитация осознанности", "short_desc": "5 минут тишины",
     "instruction": "🧘 Сядь удобно. Закрой глаза. Сделай 5 глубоких вдохов. Сосредоточь всё внимание на дыхании. Мысли будут приходить — это нормально. Мягко возвращай внимание к дыханию. Ты не твои мысли. Ты — наблюдатель.",
     "exp": 12, "sparks": 8, "kindness": 4, "cat": "daily", "duration": "5 мин"},
    {"id": "task_gratitude_journal", "name": "📝 Дневник благодарности", "short_desc": "Запиши 3 благодарности",
     "instruction": "📝 Возьми красивый блокнот или открой заметки в телефоне. Напиши 3 вещи за которые ты благодарен сегодня. Это могут быть люди, события, вкусная еда, тёплая постель, здоровье. Почувствуй как тепло благодарности наполняет сердце.",
     "exp": 15, "sparks": 5, "kindness": 5, "cat": "daily", "duration": "5 мин"},
    {"id": "task_music_meditation", "name": "🎵 Музыкальная медитация", "short_desc": "Послушай любимую музыку",
     "instruction": "🎵 Выбери одну любимую песню или спокойную мелодию. Надень наушники. Закрой глаза. Позволь музыке проникнуть в каждую клеточку. Следи за мелодией, ритмом, инструментами. Если хочется — танцуй!",
     "exp": 10, "sparks": 3, "kindness": 2, "cat": "daily", "duration": "10 мин"},
    {"id": "task_compliments", "name": "🤗 День комплиментов", "short_desc": "Скажи 3 комплимента",
     "instruction": "🤗 Скажи один комплимент себе (вслух, глядя в зеркало). Скажи комплимент тому кто рядом. Напиши комплимент другу в мессенджере. Твои слова имеют огромную силу — используй их во благо!",
     "exp": 10, "sparks": 3, "kindness": 6, "cat": "daily", "duration": "5 мин"},
    {"id": "task_plants", "name": "🌿 Забота о растениях", "short_desc": "Полей и поговори с цветами",
     "instruction": "🌿 Найди все растения в доме. Проверь влажность почвы. Полей те что сухие. Протри листья от пыли. Поговори с каждым растением — скажи что оно красивое и ты благодарен ему за кислород и уют.",
     "exp": 8, "sparks": 3, "kindness": 3, "cat": "daily", "duration": "10 мин"},
    {"id": "task_sleep_ritual", "name": "😴 Ритуал здорового сна", "short_desc": "Ложись на 30 минут раньше",
     "instruction": "😴 За час до сна выключи все экраны. Прими тёплый душ. Надень удобную пижаму. Проветри комнату. Ложись в кровать. Сделай 5 глубоких вдохов. Поблагодари прошедший день. Сладких снов, звёздочка.",
     "exp": 25, "sparks": 5, "kindness": 2, "cat": "daily", "duration": "весь вечер"},
    {"id": "task_creative_hour", "name": "🎨 Творческий час", "short_desc": "30 минут творчества",
     "instruction": "🎨 Выбери любое творческое занятие: рисование, письмо, музыка, рукоделие, кулинария. Посвяти этому 30 минут. Не думай о результате — важен процесс. Позволь своему внутреннему творцу проявиться. Ты создаёшь что-то уникальное!",
     "exp": 25, "sparks": 5, "kindness": 5, "cat": "daily", "duration": "30 мин"},
    {"id": "task_digital_detox", "name": "📱 Цифровой детокс", "short_desc": "1 час без телефона",
     "instruction": "📱 Отложи телефон. Выключи уведомления. Проведи час без экранов. Займись чем-то осязаемым: почитай бумажную книгу, погуляй, приготовь еду, приберись. Почувствуй свободу от информационного шума. Ты — не твой телефон.",
     "exp": 20, "sparks": 4, "kindness": 3, "cat": "daily", "duration": "1 час"},
    {"id": "task_reflection", "name": "🕯️ Вечерняя рефлексия", "short_desc": "10 минут рефлексии",
     "instruction": "🕯️ Зажги свечу. Сядь в тишине. Вспомни прошедший день. Что было хорошего? Чему ты научился? За что ты благодарен? Что можно сделать завтра лучше? Запиши 3 главных вывода дня. Каждый день — урок.",
     "exp": 15, "sparks": 5, "kindness": 3, "cat": "daily", "duration": "10 мин"},
    {"id": "task_self_massage", "name": "💆 Самомассаж", "short_desc": "5 минут заботы о теле",
     "instruction": "💆 Разомни плечи, шею, руки. Помассируй виски, лицо, ступни. Используй масло или крем если есть. Поблагодари своё тело за всё что оно делает для тебя. Твоё тело заслуживает заботы и любви.",
     "exp": 10, "sparks": 5, "kindness": 3, "cat": "daily", "duration": "5 мин"},
    {"id": "task_mindful_tea", "name": "☕ Осознанное чаепитие", "short_desc": "Выпей чай осознанно",
     "instruction": "☕ Завари любимый чай. Сядь удобно. Держи чашку двумя руками. Чувствуй тепло. Вдыхай аромат. Пей маленькими глотками. Никуда не спеши. Эти 10 минут только для тебя.",
     "exp": 10, "sparks": 5, "kindness": 2, "cat": "daily", "duration": "10 мин"},
]

# === МАГАЗИН (упрощён) ===
SHOP_ITEMS = [
    {"id": "item_lunar_crystal", "name": "Лунный кристалл", "cost": 50, "type": "consumable",
     "rarity": "common", "rarity_name": "Обычный", "emoji": "⚪",
     "description": "Увеличивает опыт на 20", "effect": "+20 опыта"},
    {"id": "item_star_dust", "name": "Звёздная пыль", "cost": 100, "type": "consumable",
     "rarity": "uncommon", "rarity_name": "Необычный", "emoji": "🟢",
     "description": "Увеличивает искры на 50", "effect": "+50 искр"},
    {"id": "item_calm_elixir", "name": "Эликсир спокойствия", "cost": 200, "type": "consumable",
     "rarity": "rare", "rarity_name": "Редкий", "emoji": "🔵",
     "description": "Восстанавливает 50 лунной энергии", "effect": "+50 энергии"},
    {"id": "item_guardian_amulet", "name": "Амулет хранителя", "cost": 500, "type": "equipment",
     "rarity": "epic", "rarity_name": "Эпический", "emoji": "🟣",
     "description": "+10 к космической силе", "effect": "+10 cosmic power"},
    {"id": "item_cosmic_compass", "name": "Космический компас", "cost": 1000, "type": "equipment",
     "rarity": "legendary", "rarity_name": "Легендарный", "emoji": "🟡",
     "description": "Удваивает опыт за задания", "effect": "x2 опыт"},
    {"id": "item_soul_mirror", "name": "Зеркало души", "cost": 2500, "type": "artifact",
     "rarity": "mythic", "rarity_name": "Мифический", "emoji": "🔴",
     "description": "Открывает все достижения", "effect": "Открывает достижения"},
]

# === МУЗЫКА ===
MUSIC_TRACKS = [
    {"id": "t1", "name": "🌙 Лунная соната (Бетховен)", "genre": "Классика", "mood": "😌", "url": "https://youtu.be/4Tr0otuiQuU"},
    {"id": "t2", "name": "🌟 Clair de Lune (Дебюсси)", "genre": "Классика", "mood": "🤔", "url": "https://youtu.be/WNcsUNKlAKw"},
    {"id": "t3", "name": "🌊 Weightless (Marconi Union)", "genre": "Эмбиент", "mood": "😴", "url": "https://youtu.be/UfcAVejslrU"},
    {"id": "t4", "name": "🔥 Experience (Einaudi)", "genre": "Инструментальная", "mood": "🤩", "url": "https://youtu.be/hN_q-_nGfvE"},
    {"id": "t5", "name": "🌸 River Flows in You", "genre": "Фортепиано", "mood": "😊", "url": "https://youtu.be/7maJOI3QMu0"},
]

# === ДАННЫЕ ИГРОКА ===
DEFAULT_PLAYER = {
    "name": "Хранительница тепла", "soul_type": "✨ Звёздная пыль",
    "level": 1, "exp": 0, "exp_needed": 100,
    "sparks": 200, "kindness": 0, "soul_shards": 0,
    "moon_energy": 100, "max_moon_energy": 100, "cosmic_power": 10,
    "items": [], "friends": [], "achievements": [],
    "mood_log": [], "dream_log": [],
    "daily_tasks": {}, "completed_tasks_today": [], "last_daily": None,
    "streak": 0, "days": 0, "total_tasks": 0,
    "meditation_streak": 0, "affirmation_count": 0, "tarot_readings": 0,
    "wallet": {"sparks": 200, "moon_coins": 0, "star_gems": 0},
    "total_kindness": 0, "highest_streak": 0,
    "current_mood": "😊", "clan": None,
    "stats": {"total_tasks_completed": 0, "total_meditation_minutes": 0, "longest_streak": 0,
              "total_gifts_sent": 0, "total_affirmations": 0, "total_friends_made": 0},
    "minigame_scores": {"space_runner": 0, "star_collector": 0, "moon_quiz": 0},
}

def load(uid):
    path = os.path.join(SAVE_DIR, f"{uid}.json")
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
                for k, v in DEFAULT_PLAYER.items():
                    if k not in d: d[k] = v
                return d
        except: pass
    return DEFAULT_PLAYER.copy()

def save(uid, data):
    with open(os.path.join(SAVE_DIR, f"{uid}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# === СИСТЕМА ДРУЗЕЙ (ПОЛНОСТЬЮ ИСПРАВЛЕНА) ===
class FriendSystem:
    def __init__(self):
        self.friends_file = os.path.join(FRIENDS_DIR, "friends.json")
        self.requests_file = os.path.join(FRIENDS_DIR, "requests.json")
        for fpath in [self.friends_file, self.requests_file]:
            if not os.path.exists(fpath):
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump({}, f)
    
    def _load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    
    def _save(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_pending_requests(self, uid: str) -> List[Dict]:
        reqs = self._load(self.requests_file)
        return reqs.get(str(uid), [])
    
    def get_friends(self, uid: str) -> List[Dict]:
        friends = self._load(self.friends_file)
        user_friends = friends.get(str(uid), {})
        result = []
        for fid, data in user_friends.items():
            if data.get("status") in ["✅", "💫", "💑"]:
                result.append({"friend_id": fid, **data})
        return result
    
    def send_request(self, from_id: str, from_name: str, to_id: str) -> Tuple[bool, str]:
        from_id = str(from_id)
        to_id = str(to_id)
        
        if from_id == to_id:
            return False, "❌ Нельзя добавить себя в друзья"
        
        if not os.path.exists(os.path.join(SAVE_DIR, f"{to_id}.json")):
            return False, "❌ Пользователь не найден в системе. Попроси друга запустить бота: /start"
        
        friends = self._load(self.friends_file)
        my_friends = friends.get(from_id, {})
        if to_id in my_friends:
            status = my_friends[to_id].get("status")
            if status in ["✅", "💫", "💑"]:
                return False, "❌ Вы уже друзья"
            if status == "⏳":
                return False, "⏳ Запрос уже отправлен"
        
        reqs = self._load(self.requests_file)
        if to_id not in reqs:
            reqs[to_id] = []
        for r in reqs[to_id]:
            if r.get("from") == from_id:
                return False, "⏳ Запрос уже отправлен"
        
        now = datetime.datetime.now().isoformat()
        reqs[to_id].append({
            "from": from_id,
            "from_name": from_name,
            "timestamp": now,
            "status": "pending"
        })
        self._save(self.requests_file, reqs)
        
        if from_id not in friends:
            friends[from_id] = {}
        friends[from_id][to_id] = {
            "friend_id": to_id,
            "name": "...",
            "status": "⏳",
            "friendship_points": 0,
            "gifts_sent": 0,
            "gifts_received": 0,
            "first_met": now,
            "last_interaction": now
        }
        self._save(self.friends_file, friends)
        
        return True, f"✅ Запрос в друзья отправлен! Попроси друга проверить /friendrequests"
    
    def accept_request(self, my_id: str, my_name: str, from_id: str) -> Tuple[bool, str]:
        my_id = str(my_id)
        from_id = str(from_id)
        
        reqs = self._load(self.requests_file)
        my_reqs = reqs.get(my_id, [])
        found = False
        new_reqs = []
        for r in my_reqs:
            if r.get("from") == from_id:
                found = True
            else:
                new_reqs.append(r)
        
        if not found:
            return False, "❌ Запрос не найден. Возможно, он был отменён."
        
        reqs[my_id] = new_reqs
        self._save(self.requests_file, reqs)
        
        sender_data = load(from_id)
        sender_name = sender_data.get("name", "Друг")
        now = datetime.datetime.now().isoformat()
        
        friends = self._load(self.friends_file)
        
        if my_id not in friends:
            friends[my_id] = {}
        friends[my_id][from_id] = {
            "friend_id": from_id,
            "name": sender_name,
            "status": "✅",
            "friendship_points": 10,
            "gifts_sent": 0,
            "gifts_received": 0,
            "first_met": now,
            "last_interaction": now,
            "level": sender_data.get("level", 1),
            "soul_type": sender_data.get("soul_type", "")
        }
        
        if from_id not in friends:
            friends[from_id] = {}
        friends[from_id][my_id] = {
            "friend_id": my_id,
            "name": my_name,
            "status": "✅",
            "friendship_points": 10,
            "gifts_sent": 0,
            "gifts_received": 0,
            "first_met": now,
            "last_interaction": now,
            "level": load(my_id).get("level", 1),
            "soul_type": load(my_id).get("soul_type", "")
        }
        
        self._save(self.friends_file, friends)
        
        for uid, fid in [(my_id, from_id), (from_id, my_id)]:
            p = load(uid)
            if "friends" not in p:
                p["friends"] = []
            if fid not in p["friends"]:
                p["friends"].append(fid)
            p["stats"]["total_friends_made"] = p["stats"].get("total_friends_made", 0) + 1
            save(uid, p)
        
        return True, f"✅ Вы и {sender_name} теперь друзья! 🎉"
    
    def decline_request(self, my_id: str, from_id: str) -> Tuple[bool, str]:
        my_id = str(my_id)
        from_id = str(from_id)
        
        reqs = self._load(self.requests_file)
        my_reqs = reqs.get(my_id, [])
        new_reqs = [r for r in my_reqs if r.get("from") != from_id]
        
        if len(new_reqs) == len(my_reqs):
            return False, "❌ Запрос не найден"
        
        reqs[my_id] = new_reqs
        self._save(self.requests_file, reqs)
        
        return True, "✅ Запрос отклонён"
    
    def send_gift(self, from_id: str, to_id: str) -> Tuple[bool, str]:
        from_id = str(from_id)
        to_id = str(to_id)
        
        friends = self._load(self.friends_file)
        my_friends = friends.get(from_id, {})
        
        if to_id not in my_friends:
            return False, "❌ Вы не друзья"
        
        status = my_friends[to_id].get("status")
        if status not in ["✅", "💫", "💑"]:
            return False, "❌ Вы не друзья"
        
        sparks = random.randint(20, 100)
        kindness = random.randint(5, 20)
        to_player = load(to_id)
        to_player["sparks"] = to_player.get("sparks", 0) + sparks
        to_player["kindness"] = to_player.get("kindness", 0) + kindness
        to_player["total_kindness"] = to_player.get("total_kindness", 0) + kindness
        save(to_id, to_player)
        
        my_friends[to_id]["gifts_sent"] = my_friends[to_id].get("gifts_sent", 0) + 1
        my_friends[to_id]["friendship_points"] = my_friends[to_id].get("friendship_points", 0) + 5
        my_friends[to_id]["last_interaction"] = datetime.datetime.now().isoformat()
        friends[from_id] = my_friends
        self._save(self.friends_file, friends)
        
        p = load(from_id)
        p["stats"]["total_gifts_sent"] = p["stats"].get("total_gifts_sent", 0) + 1
        save(from_id, p)
        
        return True, f"🎁 Подарок отправлен другу! Он получил +{sparks} искр и +{kindness} доброты!"
    
    def check_requests(self, uid: str) -> int:
        reqs = self._load(self.requests_file)
        return len(reqs.get(str(uid), []))

friend_system = FriendSystem()

# === СИСТЕМА ЧАТА С ДРУЗЬЯМИ ===
class ChatSystem:
    def __init__(self):
        self.chat_file = os.path.join(CHAT_DIR, "chats.json")
        if not os.path.exists(self.chat_file):
            with open(self.chat_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
    
    def send_message(self, from_id: str, to_id: str, text: str) -> Tuple[bool, str]:
        from_id = str(from_id)
        to_id = str(to_id)
        
        # Проверка дружбы
        friends = friend_system.get_friends(from_id)
        is_friend = any(f["friend_id"] == to_id for f in friends)
        if not is_friend:
            return False, "❌ Вы можете писать только друзьям"
        
        chats = self._load()
        chat_key = self._get_chat_key(from_id, to_id)
        
        if chat_key not in chats:
            chats[chat_key] = []
        
        chats[chat_key].append({
            "from": from_id,
            "to": to_id,
            "text": text,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Храним последние 100 сообщений
        if len(chats[chat_key]) > 100:
            chats[chat_key] = chats[chat_key][-100:]
        
        self._save(chats)
        return True, "✅ Сообщение отправлено!"
    
    def get_messages(self, uid1: str, uid2: str, limit: int = 20) -> List[Dict]:
        chats = self._load()
        chat_key = self._get_chat_key(str(uid1), str(uid2))
        messages = chats.get(chat_key, [])
        return messages[-limit:]
    
    def _get_chat_key(self, uid1: str, uid2: str) -> str:
        return "-".join(sorted([str(uid1), str(uid2)]))
    
    def _load(self):
        try:
            with open(self.chat_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    
    def _save(self, data):
        with open(self.chat_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

chat_system = ChatSystem()

# === СИСТЕМА КЛАНОВ ===
class ClanSystem:
    def __init__(self):
        self.clans_file = os.path.join(CLANS_DIR, "clans.json")
        if not os.path.exists(self.clans_file):
            with open(self.clans_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
    
    def create_clan(self, owner_id: str, owner_name: str, clan_name: str) -> Tuple[bool, str]:
        clans = self._load()
        
        if any(c["name"].lower() == clan_name.lower() for c in clans.values()):
            return False, "❌ Клан с таким названием уже существует"
        
        # Проверка, не состоит ли уже в клане
        for cid, cdata in clans.items():
            if str(owner_id) in cdata.get("members", []):
                return False, "❌ Вы уже состоите в клане. Используйте /leaveclan чтобы выйти"
        
        clan_id = str(uuid.uuid4())[:8]
        clans[clan_id] = {
            "id": clan_id,
            "name": clan_name,
            "owner": str(owner_id),
            "owner_name": owner_name,
            "members": [str(owner_id)],
            "member_names": {str(owner_id): owner_name},
            "created": datetime.datetime.now().isoformat(),
            "level": 1,
            "exp": 0,
            "description": ""
        }
        
        self._save(clans)
        
        # Обновляем игрока
        p = load(owner_id)
        p["clan"] = clan_id
        save(owner_id, p)
        
        return True, f"✅ Клан **{clan_name}** создан! ID: `{clan_id}`\nПриглашай друзей: /claninvite [ID друга]"
    
    def join_clan(self, uid: str, clan_id: str) -> Tuple[bool, str]:
        clans = self._load()
        
        if clan_id not in clans:
            return False, "❌ Клан не найден"
        
        if str(uid) in clans[clan_id]["members"]:
            return False, "❌ Вы уже в этом клане"
        
        # Проверка
        for cid, cdata in clans.items():
            if str(uid) in cdata.get("members", []):
                return False, "❌ Вы уже состоите в другом клане"
        
        if len(clans[clan_id]["members"]) >= 20:
            return False, "❌ Клан полон (макс 20 участников)"
        
        clans[clan_id]["members"].append(str(uid))
        p = load(uid)
        clans[clan_id]["member_names"][str(uid)] = p.get("name", "Участник")
        
        self._save(clans)
        
        p["clan"] = clan_id
        save(uid, p)
        
        return True, f"✅ Вы вступили в клан **{clans[clan_id]['name']}**!"
    
    def leave_clan(self, uid: str) -> Tuple[bool, str]:
        clans = self._load()
        p = load(uid)
        clan_id = p.get("clan")
        
        if not clan_id or clan_id not in clans:
            return False, "❌ Вы не состоите в клане"
        
        if clans[clan_id]["owner"] == str(uid):
            return False, "❌ Лидер не может покинуть клан. Используйте /disbandclan"
        
        clans[clan_id]["members"].remove(str(uid))
        del clans[clan_id]["member_names"][str(uid)]
        
        self._save(clans)
        
        p["clan"] = None
        save(uid, p)
        
        return True, f"✅ Вы покинули клан **{clans[clan_id]['name']}**"
    
    def get_clan_info(self, clan_id: str) -> Optional[Dict]:
        clans = self._load()
        return clans.get(clan_id)
    
    def get_my_clan(self, uid: str) -> Optional[Dict]:
        p = load(uid)
        clan_id = p.get("clan")
        if clan_id:
            return self.get_clan_info(clan_id)
        return None
    
    def _load(self):
        try:
            with open(self.clans_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    
    def _save(self, data):
        with open(self.clans_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

clan_system = ClanSystem()

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
def get_moon():
    today = datetime.date.today()
    known = datetime.date(2024, 1, 11)
    days = (today - known).days
    idx = (days % 29) * 8 // 29
    return list(MoonPhase)[idx % 8]

def fmt(n):
    if n >= 1000000: return f"{n/1000000:.1f}M"
    if n >= 1000: return f"{n/1000:.1f}K"
    return str(n)

def progress_bar(exp, need):
    if need <= 0: return 100, "██████████"
    p = min(exp/need*100, 100)
    f = int(p/10)
    return p, "█"*f + "░"*(10-f)

def exp_needed(lvl):
    return int(100 * (1.5 ** (lvl-1)))

def update_streak(p):
    today = datetime.date.today().isoformat()
    last = p.get("last_daily")
    if last:
        ld = datetime.date.fromisoformat(last[:10])
        yd = datetime.date.today() - datetime.timedelta(days=1)
        if ld == yd: p["streak"] = p.get("streak", 0) + 1
        elif ld < yd: p["streak"] = 1
    else: p["streak"] = 1
    p["last_daily"] = today
    p["days"] = p.get("days", 0) + 1
    if p["streak"] > p.get("highest_streak", 0): p["highest_streak"] = p["streak"]
    if p["streak"] > p.get("stats", {}).get("longest_streak", 0): p["stats"]["longest_streak"] = p["streak"]
    return p["streak"]

def lvl_up(p):
    messages = []
    while p["exp"] >= p["exp_needed"]:
        p["exp"] -= p["exp_needed"]
        p["level"] += 1
        p["exp_needed"] = exp_needed(p["level"])
        p["sparks"] += 50 * p["level"]
        p["cosmic_power"] = p.get("cosmic_power", 10) + 2
        if p["level"] % 10 == 0:
            p["soul_shards"] += 5
            p["wallet"]["star_gems"] = p["wallet"].get("star_gems", 0) + 1
            messages.append(f"🎉 УРОВЕНЬ {p['level']}! +5 осколков души и 1 звёздный самоцвет!")
        elif p["level"] % 5 == 0:
            p["wallet"]["moon_coins"] = p["wallet"].get("moon_coins", 0) + 10
            messages.append(f"🎉 УРОВЕНЬ {p['level']}! +10 лунных монет!")
        else:
            messages.append(f"🎉 УРОВЕНЬ {p['level']}! +{50 * p['level']} искр!")
    return messages

def check_ach(p):
    unlocked = []
    s = p.get("stats", {})
    checks = {
        "first_step": ("🌱 Первый шаг", s.get("total_tasks_completed", 0) >= 1),
        "ten_tasks": ("⭐ 10 заданий", s.get("total_tasks_completed", 0) >= 10),
        "hundred_tasks": ("🌟 100 заданий", s.get("total_tasks_completed", 0) >= 100),
        "streak_3": ("🔥 Стрик 3 дня", p.get("streak", 0) >= 3),
        "streak_7": ("🌟 Стрик 7 дней", p.get("streak", 0) >= 7),
        "streak_30": ("🌙 Стрик 30 дней", p.get("streak", 0) >= 30),
        "level_5": ("📈 Уровень 5", p.get("level", 1) >= 5),
        "level_10": ("🎯 Уровень 10", p.get("level", 1) >= 10),
        "level_25": ("🏆 Уровень 25", p.get("level", 1) >= 25),
        "first_friend": ("👋 Первый друг", len(p.get("friends", [])) >= 1),
        "five_friends": ("👥 5 друзей", len(p.get("friends", [])) >= 5),
        "first_meditation": ("🧘 Первая медитация", p.get("meditation_streak", 0) >= 1),
        "ten_meditations": ("🕉️ 10 медитаций", p.get("meditation_streak", 0) >= 10),
        "first_affirmation": ("💫 Первая аффирмация", p.get("affirmation_count", 0) >= 1),
        "fifty_affirmations": ("✨ 50 аффирмаций", p.get("affirmation_count", 0) >= 50),
        "first_gift": ("🎁 Первый подарок", s.get("total_gifts_sent", 0) >= 1),
        "kindness_100": ("💝 100 доброты", p.get("total_kindness", 0) >= 100),
        "kindness_1000": ("🌟 1000 доброты", p.get("total_kindness", 0) >= 1000),
        "dreamer": ("🌌 Мечтатель", len(p.get("dream_log", [])) >= 10),
    }
    for ach_id, (name, cond) in checks.items():
        if cond and ach_id not in p.get("achievements", []):
            p["achievements"].append(ach_id)
            unlocked.append(name)
            p["sparks"] += 50
            p["exp"] += 25
    return unlocked

# === КЛАСС ИГРЫ ===
class Game:
    def __init__(self):
        self.players = {}
        self.minigames = {}  # Активные мини-игры
    
    def gp(self, uid):
        uid = str(uid)
        if uid not in self.players: self.players[uid] = load(uid)
        return self.players[uid]
    
    def sp(self, uid):
        save(str(uid), self.players.get(str(uid), DEFAULT_PLAYER))
    
    def profile(self, uid):
        p = self.gp(uid)
        pr, bar = progress_bar(p.get("exp", 0), p.get("exp_needed", 100))
        m = get_moon()
        clan_info = ""
        if p.get("clan"):
            clan = clan_system.get_clan_info(p["clan"])
            if clan:
                clan_info = f"\n🏰 Клан: **{clan['name']}**"
        return f"""
✨ **{p['name']}** | Ур.{p['level']} | {p.get('soul_type', '')}
[{bar}] {pr:.0f}%
💫 Искры: {fmt(p.get('sparks',0))} | 💝 Доброта: {p.get('total_kindness',0)}
💎 Осколки: {p.get('soul_shards',0)} | 🌙 Энергия: {p.get('moon_energy',100)}/{p.get('max_moon_energy',100)}
{m.value[0]} **{m.value[1]}**: {m.value[2]}
🔥 Стрик: {p.get('streak',0)} дн. | 📅 Дней: {p.get('days',0)}
🎯 Заданий: {p.get('total_tasks',0)} | 🧘 Медитаций: {p.get('meditation_streak',0)}
💫 Аффирмаций: {p.get('affirmation_count',0)} | 🔮 Таро: {p.get('tarot_readings',0)}
👥 Друзей: {len(p.get('friends',[]))} | 🏆 Достижений: {len(p.get('achievements',[]))}{clan_info}
"""
    
    def daily_tasks(self, uid, n=5):
        today = datetime.date.today().isoformat()
        rng = random.Random(hash(f"{uid}_{today}"))
        daily = [t for t in TASKS if t["cat"] == "daily"]
        return rng.sample(daily, min(n, len(daily)))
    
    def complete(self, uid, task_id):
        p = self.gp(uid)
        t = next((x for x in TASKS if x["id"] == task_id), None)
        if not t: return False, "❌ Задание не найдено"
        
        completed = p.get("completed_tasks_today", [])
        if task_id in completed:
            return False, "❌ Это задание уже выполнено сегодня! Возвращайся завтра."
        
        return True, t
    
    def confirm_complete(self, uid, task_id):
        p = self.gp(uid)
        t = next((x for x in TASKS if x["id"] == task_id), None)
        if not t: return False, "❌ Ошибка"
        
        p["exp"] += t["exp"]
        p["sparks"] += t["sparks"]
        p["kindness"] += t["kindness"]
        p["total_kindness"] += t["kindness"]
        p["total_tasks"] += 1
        p.setdefault("stats", {})["total_tasks_completed"] = p["stats"].get("total_tasks_completed", 0) + 1
        p.setdefault("completed_tasks_today", []).append(task_id)
        
        update_streak(p)
        lvl_msgs = lvl_up(p)
        ach = check_ach(p)
        
        msg = f"✅ **Задание выполнено!**\n\n📋 {t['name']}\n📝 {t['instruction'][:200]}...\n\n"
        msg += f"💫 +{t['exp']} опыта\n⭐ +{t['sparks']} искр\n💝 +{t['kindness']} доброты"
        
        if lvl_msgs:
            for m in lvl_msgs:
                msg += f"\n{m}"
        if ach:
            msg += f"\n\n🏆 **Новые достижения:**\n" + "\n".join(f"• {a}" for a in ach)
        
        self.sp(uid)
        return True, msg
    
    def checkin(self, uid):
        p = self.gp(uid)
        s = update_streak(p)
        rwd = 10 + s*2
        if s >= 7: rwd += 50
        if s >= 30: rwd += 200
        if s >= 100: rwd += 500
        p["sparks"] += rwd
        p["exp"] += s
        ach = check_ach(p)
        self.sp(uid)
        m = get_moon()
        msg = f"🌟 **Ежедневная отметка!**\n🔥 Стрик: {s} дн.\n💫 +{rwd} искр | +{s} опыта\n{m.value[0]} {m.value[1]}: {m.value[2]}"
        if ach: msg += f"\n\n🏆 Новые достижения:\n" + "\n".join(f"• {a}" for a in ach)
        return msg
    
    def affirm(self, uid):
        p = self.gp(uid)
        p["affirmation_count"] += 1
        p["stats"]["total_affirmations"] = p["stats"].get("total_affirmations", 0) + 1
        p["exp"] += 5
        check_ach(p)
        self.sp(uid)
        return f"💫 **Аффирмация для тебя:**\n\n{random.choice(AFFIRMATIONS)}"
    
    def support(self, uid):
        p = self.gp(uid)
        p["exp"] += 3
        self.sp(uid)
        return random.choice(SUPPORT_PHRASES)
    
    def meditate(self, uid, mins=5):
        p = self.gp(uid)
        p["meditation_streak"] += 1
        p.setdefault("stats", {})["total_meditation_minutes"] = p["stats"].get("total_meditation_minutes", 0) + mins
        p["exp"] += mins*2
        p["sparks"] += mins
        p["moon_energy"] = min(p.get("moon_energy", 100) + mins, p.get("max_moon_energy", 100))
        ach = check_ach(p)
        self.sp(uid)
        msg = f"🧘 **Медитация {mins} мин.**\n💫 +{mins*2} опыта | +{mins} искр\n🌙 +{mins} лунной энергии\nВсего медитаций: {p['meditation_streak']}"
        if ach: msg += f"\n\n🏆 Новые достижения:\n" + "\n".join(f"• {a}" for a in ach)
        return msg
    
    def mood(self, uid, mood):
        p = self.gp(uid)
        p.setdefault("mood_log", []).append({"ts": datetime.datetime.now().isoformat(), "mood": mood, "moon": get_moon().value[1]})
        p["exp"] += 5
        p["current_mood"] = mood
        ach = check_ach(p)
        self.sp(uid)
        m = get_moon()
        msg = f"📝 **Настроение записано!**\n{mood}\n🌙 {m.value[0]} {m.value[1]}: {m.value[2]}"
        if ach: msg += f"\n\n🏆 Новые достижения:\n" + "\n".join(f"• {a}" for a in ach)
        return msg
    
    def dream(self, uid, text):
        p = self.gp(uid)
        p.setdefault("dream_log", []).append({"ts": datetime.datetime.now().isoformat(), "dream": text})
        p["exp"] += 10
        ach = check_ach(p)
        self.sp(uid)
        msg = f"🌌 **Сон записан!**\n📝 Всего снов: {len(p['dream_log'])}"
        if ach: msg += f"\n\n🏆 Новые достижения:\n" + "\n".join(f"• {a}" for a in ach)
        return msg
    
    def moodstats(self, uid):
        p = self.gp(uid)
        log = p.get("mood_log", [])
        if not log: return "📊 Пока нет записей о настроении. Используй /mood!"
        counts = {}
        for e in log[-30:]:
            m = e.get("mood", "😊")
            counts[m] = counts.get(m, 0) + 1
        msg = "📊 **Статистика настроения (30 дней):**\n\n"
        for mood, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * cnt
            msg += f"{mood}: {bar} ({cnt})\n"
        msg += f"\n📝 Всего записей: {len(log)}"
        return msg
    
    def tarot(self, uid):
        p = self.gp(uid)
        cards = [
            ("🌟", "Звезда", "Надежда, вдохновение, обновление", "Верь в свои мечты. Вселенная поддерживает тебя."),
            ("🌙", "Луна", "Интуиция, подсознание, тайны", "Доверься своей интуиции. Ответы внутри тебя."),
            ("☀️", "Солнце", "Радость, успех, жизненная сила", "Сияй ярко! Твоё время пришло."),
            ("👑", "Императрица", "Плодородие, забота, изобилие", "Заботься о себе и близких. Ты создаёшь прекрасное."),
            ("💪", "Сила", "Мужество, внутренняя сила, стойкость", "Ты сильнее чем думаешь. Укроти внутренних зверей."),
            ("🌍", "Мир", "Завершение, целостность, достижение", "Цикл завершён. Празднуй свои достижения."),
            ("🎩", "Маг", "Проявление, сила воли, мастерство", "У тебя есть все инструменты. Создай свою реальность."),
            ("🔮", "Верховная жрица", "Тайны, интуиция, знание", "Прислушайся к внутреннему голосу. Он знает путь."),
            ("💀", "Смерть", "Трансформация, конец и начало", "Отпусти старое. На пороге новая жизнь."),
        ]
        em, name, meaning, advice = random.choice(cards)
        pos = random.choice(["прямая", "перевёрнутая"])
        if pos == "перевёрнутая":
            meaning = f"Теневая сторона: {meaning}"
            advice = f"Урок: {advice}"
        p["tarot_readings"] += 1
        p["exp"] += 10
        self.sp(uid)
        return f"🔮 **Карта Таро: {em} {name}** ({pos})\n\n📖 Значение: {meaning}\n💬 Совет: {advice}\n\n💫 +10 опыта"
    
    def buy(self, uid, item_id):
        p = self.gp(uid)
        item = next((i for i in SHOP_ITEMS if i["id"] == item_id), None)
        if not item: return False, "❌ Предмет не найден"
        if p.get("sparks", 0) < item["cost"]:
            return False, f"❌ Недостаточно искр. Нужно {item['cost']}, у вас {p.get('sparks', 0)}"
        p["sparks"] -= item["cost"]
        p.setdefault("items", []).append(item["id"])
        # Применяем эффект
        if item["type"] == "consumable":
            if "опыта" in item["effect"]:
                p["exp"] += 20
            elif "искр" in item["effect"]:
                p["sparks"] += 50
            elif "энергии" in item["effect"]:
                p["moon_energy"] = min(p["moon_energy"] + 50, p["max_moon_energy"])
        elif item["type"] == "equipment":
            p["cosmic_power"] += 10
        self.sp(uid)
        return True, f"✅ Куплено: {item['emoji']} **{item['name']}** за {item['cost']}💫\n{item['description']}\n{item['effect']}"
    
    def inventory(self, uid):
        p = self.gp(uid)
        items = p.get("items", [])
        if not items: return "🎒 Ваш инвентарь пуст. Купите что-нибудь в /shop!"
        counts = {}
        for iid in items:
            counts[iid] = counts.get(iid, 0) + 1
        msg = "🎒 **Ваш инвентарь:**\n\n"
        for iid, cnt in counts.items():
            item = next((i for i in SHOP_ITEMS if i["id"] == iid), None)
            if item:
                msg += f"{item['emoji']} {item['name']} x{cnt}\n"
        msg += f"\n📦 Всего предметов: {len(items)}"
        return msg
    
    # === МИНИ-ИГРЫ ===
    def space_runner(self, uid, action=None):
        """Мини-игра: Космический бегун"""
        p = self.gp(uid)
        
        if uid not in self.minigames:
            self.minigames[uid] = {}
        
        if "space_runner" not in self.minigames[uid] or action == "start":
            self.minigames[uid]["space_runner"] = {
                "distance": 0,
                "energy": 3,
                "score": 0,
                "active": True
            }
            return f"🚀 **Космический бегун**\n\n🏃 Дистанция: 0\n⚡ Энергия: 3\n\nВыбери действие:", [
                [InlineKeyboardButton("🏃 Бежать", callback_data="minigame_space_runner_run"),
                 InlineKeyboardButton("⭐ Ускориться", callback_data="minigame_space_runner_boost")],
                [InlineKeyboardButton("🛑 Закончить", callback_data="minigame_space_runner_end")]
            ]
        
        game_data = self.minigames[uid]["space_runner"]
        
        if not game_data.get("active"):
            return "Игра завершена. Начни заново!", None
        
        if action == "run":
            game_data["distance"] += random.randint(10, 30)
            game_data["score"] += random.randint(5, 15)
            game_data["energy"] -= 1
        elif action == "boost":
            if game_data["energy"] >= 2:
                game_data["distance"] += random.randint(30, 60)
                game_data["score"] += random.randint(20, 40)
                game_data["energy"] -= 2
            else:
                return "❌ Недостаточно энергии для ускорения!", None
        elif action == "end":
            score = game_data["score"]
            game_data["active"] = False
            p["sparks"] += score
            p.setdefault("minigame_scores", {})["space_runner"] = max(p["minigame_scores"].get("space_runner", 0), score)
            self.sp(uid)
            return f"🏁 **Финиш!**\n\n📏 Дистанция: {game_data['distance']}\n⭐ Очки: {score}\n💫 +{score} искр", None
        
        if game_data["energy"] <= 0:
            score = game_data["score"]
            game_data["active"] = False
            p["sparks"] += score
            p.setdefault("minigame_scores", {})["space_runner"] = max(p["minigame_scores"].get("space_runner", 0), score)
            self.sp(uid)
            return f"⚡ **Энергия закончилась!**\n\n📏 Дистанция: {game_data['distance']}\n⭐ Очки: {score}\n💫 +{score} искр", None
        
        return f"🚀 **Космический бегун**\n\n🏃 Дистанция: {game_data['distance']}\n⚡ Энергия: {game_data['energy']}\n⭐ Очки: {game_data['score']}", [
            [InlineKeyboardButton("🏃 Бежать", callback_data="minigame_space_runner_run"),
             InlineKeyboardButton("⭐ Ускориться", callback_data="minigame_space_runner_boost")],
            [InlineKeyboardButton("🛑 Закончить", callback_data="minigame_space_runner_end")]
        ]
    
    def moon_quiz(self, uid):
        """Мини-викторина"""
        questions = [
            {"q": "Сколько длится лунный цикл?", "a": ["27 дней", "29.5 дней", "30 дней", "31 день"], "correct": 1},
            {"q": "Какая планета самая большая?", "a": ["Марс", "Земля", "Юпитер", "Сатурн"], "correct": 2},
            {"q": "Что такое Млечный Путь?", "a": ["Звезда", "Планета", "Галактика", "Комета"], "correct": 2},
            {"q": "Сколько планет в Солнечной системе?", "a": ["7", "8", "9", "10"], "correct": 1},
        ]
        q = random.choice(questions)
        self.minigames[uid] = {"quiz": q}
        kb = []
        for i, ans in enumerate(q["a"]):
            kb.append([InlineKeyboardButton(f"{['A','B','C','D'][i]}. {ans}", callback_data=f"quiz_answer_{i}")])
        return f"🌙 **Лунная викторина**\n\n❓ {q['q']}", kb
    
    def check_quiz(self, uid, answer_idx):
        if uid not in self.minigames or "quiz" not in self.minigames[uid]:
            return "❌ Викторина не найдена. Начни заново: /minigame"
        
        q = self.minigames[uid]["quiz"]
        p = self.gp(uid)
        
        if answer_idx == q["correct"]:
            reward = 30
            p["sparks"] += reward
            p["exp"] += 15
            self.sp(uid)
            return f"✅ **Правильно!**\n💫 +{reward} искр\n✨ +15 опыта"
        else:
            comfort = random.choice(SUPPORT_PHRASES[:5])
            return f"❌ Неправильно. Правильный ответ: **{q['a'][q['correct']]}**\n\n{comfort}"
    
    def help(self):
        return """
🌙 **Lunar Capsule v11.0** — твой космический помощник заботы о себе

**Основные команды:**
/start — Начать путешествие
/profile — Твой профиль
/daily — Ежедневные задания
/checkin — Ежедневная отметка (стрик!)

**Забота о себе:**
/affirmation — Аффирмация
/support — Слова поддержки
/meditate [мин] — Медитация
/mood — Записать настроение
/dream [текст] — Записать сон
/moodstats — Статистика настроения

**Друзья и чат:**
/addfriend [ID] — Добавить друга
/friends — Список друзей
/friendrequests — Заявки в друзья
/sendgift [ID] — Отправить подарок
/chat [ID] [текст] — Написать другу
/readchat [ID] — Прочитать чат

**Кланы:**
/createclan [название] — Создать клан
/joinclan [ID] — Вступить в клан
/myclan — Информация о клане
/leaveclan — Покинуть клан

**Магазин и игры:**
/shop — Магазин
/buy [ID] — Купить предмет
/inventory — Инвентарь
/minigame — Мини-игры
/fact — Случайный факт

**Особое:**
/tarot — Карта Таро
/music — Музыка
/moon — Фаза луны
/achievements — Достижения
"""

game = Game()

# === TELEGRAM BOT ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    name = update.effective_user.first_name or "Друг"
    p = game.gp(uid)
    if p.get("name") == DEFAULT_PLAYER["name"] and p.get("level") == 1:
        p["name"] = name
        game.sp(uid)
    
    m = get_moon()
    req_count = friend_system.check_requests(uid)
    
    kb = [
        [InlineKeyboardButton("🌟 Профиль", callback_data="profile"),
         InlineKeyboardButton("📋 Задания", callback_data="daily")],
        [InlineKeyboardButton("💫 Аффирмация", callback_data="affirmation"),
         InlineKeyboardButton("🤗 Поддержка", callback_data="support")],
        [InlineKeyboardButton("🧘 Медитация", callback_data="meditate"),
         InlineKeyboardButton("🎭 Настроение", callback_data="mood")],
        [InlineKeyboardButton("🛒 Магазин", callback_data="shop"),
         InlineKeyboardButton("🎮 Мини-игры", callback_data="minigame")],
        [InlineKeyboardButton("👥 Друзья", callback_data="friends"),
         InlineKeyboardButton("🏰 Клан", callback_data="myclan")],
        [InlineKeyboardButton("🔮 Таро", callback_data="tarot"),
         InlineKeyboardButton("💡 Факт", callback_data="fact")],
        [InlineKeyboardButton("🎵 Музыка", callback_data="music"),
         InlineKeyboardButton("🏆 Достижения", callback_data="achievements")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")],
    ]
    
    if req_count > 0:
        kb.insert(0, [InlineKeyboardButton(f"📬 Заявки в друзья ({req_count})", callback_data="friendrequests")])
    
    await update.message.reply_text(
        f"{m.value[0]} **Добро пожаловать в {GAME_NAME}!**\n\n"
        f"🌙 Сейчас **{m.value[1]}**: {m.value[2]}\n\n"
        "Я твой космический помощник. Выбери действие:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(game.profile(str(update.effective_user.id)), parse_mode=ParseMode.MARKDOWN)

async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    tasks = game.daily_tasks(uid, 5)
    if not tasks:
        await update.message.reply_text("❌ Нет доступных заданий")
        return
    msg = "📋 **Ежедневные задания:**\n\n"
    kb = []
    for i, t in enumerate(tasks):
        msg += f"**{i+1}. {t['name']}**\n📝 {t['short_desc']}\n⏱ {t['duration']} | 💫 {t['exp']} опыта | ⭐ {t['sparks']} искр\n\n"
        # ИСПРАВЛЕНО: Используем ID вместо имени для callback (короче и уникальнее)
        kb.append([InlineKeyboardButton(f"📋 {t['name'][:25]}", callback_data=f"task_{t['id']}")])
    kb.append([InlineKeyboardButton("🔄 Обновить задания", callback_data="daily")])
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def checkin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(game.checkin(str(update.effective_user.id)), parse_mode=ParseMode.MARKDOWN)

async def affirmation_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(game.affirm(str(update.effective_user.id)), parse_mode=ParseMode.MARKDOWN)

async def support_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(game.support(str(update.effective_user.id)))

async def meditate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    mins = 5
    if context.args:
        try: mins = max(1, min(120, int(context.args[0])))
        except: pass
    r = game.meditate(uid, mins)
    kb = [[InlineKeyboardButton("5 мин", callback_data="meditate_5"),
           InlineKeyboardButton("10 мин", callback_data="meditate_10"),
           InlineKeyboardButton("15 мин", callback_data="meditate_15"),
           InlineKeyboardButton("30 мин", callback_data="meditate_30")]]
    await update.message.reply_text(r + "\n\nХочешь ещё помедитировать?", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def mood_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    moods = [
        [InlineKeyboardButton("😊 Счастливый", callback_data="mood_😊 Счастливый"),
         InlineKeyboardButton("😌 Спокойный", callback_data="mood_😌 Спокойный")],
        [InlineKeyboardButton("⚡ Энергичный", callback_data="mood_⚡ Энергичный"),
         InlineKeyboardButton("🤔 Задумчивый", callback_data="mood_🤔 Задумчивый")],
        [InlineKeyboardButton("🙏 Благодарный", callback_data="mood_🙏 Благодарный"),
         InlineKeyboardButton("💡 Вдохновлённый", callback_data="mood_💡 Вдохновлённый")],
        [InlineKeyboardButton("😴 Уставший", callback_data="mood_😴 Уставший"),
         InlineKeyboardButton("😢 Грустный", callback_data="mood_😢 Грустный")],
    ]
    await update.message.reply_text("🎭 Какое у тебя сейчас настроение?", reply_markup=InlineKeyboardMarkup(moods))

async def dream_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🌌 Расскажи свой сон: /dream Я летал среди звёзд...")
        return
    text = " ".join(context.args)
    await update.message.reply_text(game.dream(str(update.effective_user.id), text), parse_mode=ParseMode.MARKDOWN)

async def moodstats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(game.moodstats(str(update.effective_user.id)), parse_mode=ParseMode.MARKDOWN)

async def addfriend_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    name = update.effective_user.first_name or "Друг"
    if not context.args:
        await update.message.reply_text(f"👥 Используй: /addfriend [ID друга]\n\nТвой ID: `{uid}`\n\nПоделись своим ID с другом!", parse_mode=ParseMode.MARKDOWN)
        return
    ok, msg = friend_system.send_request(uid, name, str(context.args[0]))
    await update.message.reply_text(msg)

async def friends_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    fr = friend_system.get_friends(uid)
    if not fr:
        await update.message.reply_text(f"👥 У вас пока нет друзей.\n\nТвой ID: `{uid}`\n/addfriend [ID друга]", parse_mode=ParseMode.MARKDOWN)
        return
    msg = "👥 **Ваши друзья:**\n\n"
    kb = []
    for f in fr:
        msg += f"{f.get('status','✅')} **{f.get('name','Друг')}** | 💫 {f.get('friendship_points',0)} очков дружбы\n"
        kb.append([InlineKeyboardButton(f"💬 Чат с {f['name']}", callback_data=f"chat_{f['friend_id']}")])
        kb.append([InlineKeyboardButton(f"🎁 Подарок для {f['name']}", callback_data=f"gift_{f['friend_id']}")])
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def friendrequests_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    reqs = friend_system.get_pending_requests(uid)
    if not reqs:
        await update.message.reply_text("📭 Нет входящих заявок в друзья.")
        return
    msg = "📬 **Входящие заявки:**\n\n"
    kb = []
    for r in reqs:
        msg += f"• **{r.get('from_name', 'Пользователь')}** (ID: `{r.get('from', '')}`)\n"
        kb.append([
            InlineKeyboardButton(f"✅ Принять", callback_data=f"accept_{r['from']}"),
            InlineKeyboardButton(f"❌ Отклонить", callback_data=f"decline_{r['from']}")
        ])
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def sendgift_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("🎁 Используй: /sendgift [ID друга]\nСписок друзей: /friends")
        return
    ok, msg = friend_system.send_gift(uid, str(context.args[0]))
    await update.message.reply_text(msg)

# === ЧАТ ===
async def chat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if len(context.args) < 2:
        await update.message.reply_text("💬 Используй: /chat [ID друга] [сообщение]\nПример: /chat 12345 Привет! Как дела?")
        return
    fid = str(context.args[0])
    text = " ".join(context.args[1:])
    ok, msg = chat_system.send_message(uid, fid, text)
    await update.message.reply_text(msg)

async def readchat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("💬 Используй: /readchat [ID друга]")
        return
    fid = str(context.args[0])
    messages = chat_system.get_messages(uid, fid, 20)
    if not messages:
        await update.message.reply_text("💬 Нет сообщений с этим другом.")
        return
    msg = f"💬 **Чат с другом:**\n\n"
    for m in messages[-10:]:
        sender = "Вы" if m["from"] == uid else "Друг"
        msg += f"**{sender}**: {m['text']}\n_{m['timestamp'][:16]}_\n\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

# === КЛАНЫ ===
async def createclan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    name = update.effective_user.first_name or "Друг"
    if not context.args:
        await update.message.reply_text("🏰 Используй: /createclan [название]")
        return
    clan_name = " ".join(context.args)
    ok, msg = clan_system.create_clan(uid, name, clan_name)
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def joinclan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("🏰 Используй: /joinclan [ID клана]")
        return
    ok, msg = clan_system.join_clan(uid, str(context.args[0]))
    await update.message.reply_text(msg)

async def myclan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    clan = clan_system.get_my_clan(uid)
    if not clan:
        await update.message.reply_text("🏰 Вы не состоите в клане.\n/createclan [название] — создать\n/joinclan [ID] — вступить")
        return
    members = "\n".join([f"• {name}" for name in clan["member_names"].values()])
    msg = f"🏰 **Клан: {clan['name']}**\n\n👑 Лидер: {clan['owner_name']}\n⭐ Уровень: {clan['level']}\n👥 Участники ({len(clan['members'])}):\n{members}\n\nID клана: `{clan['id']}`"
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def leaveclan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    ok, msg = clan_system.leave_clan(uid)
    await update.message.reply_text(msg)

# === МАГАЗИН ===
async def shop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🛒 **Магазин Lunar Capsule:**\n\n"
    kb = []
    for i in SHOP_ITEMS:
        msg += f"{i['emoji']} **{i['name']}** ({i['rarity_name']}) — {i['cost']}💫\n{i['description']}\n\n"
        kb.append([InlineKeyboardButton(f"Купить {i['name']} - {i['cost']}💫", callback_data=f"buy_{i['id']}")])
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def buy_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("🛒 Используй: /buy [ID предмета]\nСписок: /shop")
        return
    ok, msg = game.buy(uid, str(context.args[0]))
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def inventory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(game.inventory(str(update.effective_user.id)), parse_mode=ParseMode.MARKDOWN)

async def tarot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    msg = game.tarot(uid)
    kb = [[InlineKeyboardButton("🔮 Ещё карту", callback_data="tarot")]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def music_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🎵 **Музыка для души:**\n\n"
    kb = []
    for t in MUSIC_TRACKS:
        msg += f"• {t['name']} ({t['genre']}) [{t['mood']}]\n"
        kb.append([InlineKeyboardButton(f"▶ {t['name']}", url=t['url'])])
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def moon_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = get_moon()
    phases = list(MoonPhase)
    next_phase = phases[(m.value[3] + 1) % 8]
    await update.message.reply_text(
        f"{m.value[0]} **{m.value[1]}**\n\n{m.value[2]}\n\n"
        f"🌑 → 🌒 → 🌓 → 🌔 → 🌕 → 🌖 → 🌗 → 🌘\n\n"
        f"Следующая фаза: {next_phase.value[0]} {next_phase.value[1]}",
        parse_mode=ParseMode.MARKDOWN
    )

async def achievements_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = game.gp(str(update.effective_user.id))
    ach = p.get("achievements", [])
    all_ach = {
        "first_step": "🌱 Первый шаг", "ten_tasks": "⭐ 10 заданий", "hundred_tasks": "🌟 100 заданий",
        "streak_3": "🔥 Стрик 3 дня", "streak_7": "🌟 Стрик 7 дней", "streak_30": "🌙 Стрик 30 дней",
        "level_5": "📈 Уровень 5", "level_10": "🎯 Уровень 10", "level_25": "🏆 Уровень 25",
        "first_friend": "👋 Первый друг", "five_friends": "👥 5 друзей",
        "first_meditation": "🧘 Первая медитация", "ten_meditations": "🕉️ 10 медитаций",
        "first_affirmation": "💫 Первая аффирмация", "fifty_affirmations": "✨ 50 аффирмаций",
        "first_gift": "🎁 Первый подарок", "kindness_100": "💝 100 доброты",
        "kindness_1000": "🌟 1000 доброты", "dreamer": "🌌 Мечтатель",
    }
    msg = f"🏆 **Достижения** ({len(ach)}/{len(all_ach)})\n\n"
    for aid, aname in all_ach.items():
        if aid in ach:
            msg += f"{aname}\n"
        else:
            msg += f"🔒 ???\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(game.help(), parse_mode=ParseMode.MARKDOWN)

# === ФАКТЫ ===
async def fact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fact = random.choice(FUN_FACTS)
    kb = [[InlineKeyboardButton("💡 Ещё факт!", callback_data="fact")]]
    await update.message.reply_text(f"💡 **Случайный факт:**\n\n{fact}", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

# === МИНИ-ИГРЫ ===
async def minigame_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🚀 Космический бегун", callback_data="minigame_space_runner")],
        [InlineKeyboardButton("🌙 Лунная викторина", callback_data="minigame_moon_quiz")],
    ]
    await update.message.reply_text("🎮 **Мини-игры:**\n\nВыбери игру:", reply_markup=InlineKeyboardMarkup(kb))

# === CALLBACK HANDLER (ИСПРАВЛЕНО ДЛЯ ЗАДАНИЙ) ===
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    uid = str(q.from_user.id)
    await q.answer()
    
    if d == "profile":
        await q.edit_message_text(game.profile(uid), parse_mode=ParseMode.MARKDOWN)
    
    elif d == "daily":
        tasks = game.daily_tasks(uid, 5)
        if not tasks:
            await q.edit_message_text("❌ Нет заданий")
            return
        msg = "📋 **Ежедневные задания:**\n\n"
        kb = []
        for i, t in enumerate(tasks):
            msg += f"**{i+1}. {t['name']}**\n📝 {t['short_desc']}\n⏱ {t['duration']} | 💫 {t['exp']} опыта\n\n"
            kb.append([InlineKeyboardButton(f"📋 {t['name'][:25]}", callback_data=f"task_{t['id']}")])
        kb.append([InlineKeyboardButton("🔄 Обновить", callback_data="daily")])
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d.startswith("task_"):
        task_id = d[5:]
        t = next((x for x in TASKS if x["id"] == task_id), None)
        if not t:
            await q.edit_message_text("❌ Задание не найдено")
            return
        msg = f"📋 **{t['name']}**\n\n📝 **Инструкция:**\n{t['instruction']}\n\n"
        msg += f"⏱ Длительность: {t['duration']}\n"
        msg += f"💫 Награда: {t['exp']} опыта, {t['sparks']} искр, {t['kindness']} доброты\n\n"
        msg += "⚠️ **Выполни задание в реальной жизни, затем нажми кнопку!**"
        kb = [
            [InlineKeyboardButton("✅ Я выполнил(а)!", callback_data=f"confirm_{task_id}")],
            [InlineKeyboardButton("⬅ Назад", callback_data="daily")]
        ]
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d.startswith("confirm_"):
        task_id = d[8:]
        ok, msg = game.confirm_complete(uid, task_id)
        if ok:
            kb = [[InlineKeyboardButton("📋 К заданиям", callback_data="daily"),
                   InlineKeyboardButton("🌟 Профиль", callback_data="profile")]]
            await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        else:
            await q.edit_message_text(msg)
    
    elif d == "affirmation":
        await q.edit_message_text(game.affirm(uid), parse_mode=ParseMode.MARKDOWN)
    
    elif d == "support":
        await q.edit_message_text(game.support(uid))
    
    elif d == "meditate":
        r = game.meditate(uid, 5)
        kb = [[InlineKeyboardButton("5 мин", callback_data="meditate_5"),
               InlineKeyboardButton("10 мин", callback_data="meditate_10"),
               InlineKeyboardButton("15 мин", callback_data="meditate_15"),
               InlineKeyboardButton("30 мин", callback_data="meditate_30")]]
        await q.edit_message_text(r + "\n\nЕщё?", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d.startswith("meditate_"):
        mins = int(d.split("_")[1])
        r = game.meditate(uid, mins)
        kb = [[InlineKeyboardButton("Ещё 5 мин", callback_data="meditate_5"),
               InlineKeyboardButton("Ещё 10 мин", callback_data="meditate_10")]]
        await q.edit_message_text(r, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d == "mood":
        moods = [
            [InlineKeyboardButton("😊 Счастливый", callback_data="mood_😊"),
             InlineKeyboardButton("😌 Спокойный", callback_data="mood_😌")],
            [InlineKeyboardButton("⚡ Энергичный", callback_data="mood_⚡"),
             InlineKeyboardButton("🤔 Задумчивый", callback_data="mood_🤔")],
            [InlineKeyboardButton("😴 Уставший", callback_data="mood_😴"),
             InlineKeyboardButton("😢 Грустный", callback_data="mood_😢")],
        ]
        await q.edit_message_text("🎭 Какое настроение?", reply_markup=InlineKeyboardMarkup(moods))
    
    elif d.startswith("mood_"):
        mood_map = {"😊": "😊 Счастливый", "😌": "😌 Спокойный", "⚡": "⚡ Энергичный", 
                    "🤔": "🤔 Задумчивый", "😴": "😴 Уставший", "😢": "😢 Грустный"}
        mood = d[5:]
        full_mood = mood_map.get(mood, mood)
        await q.edit_message_text(game.mood(uid, full_mood), parse_mode=ParseMode.MARKDOWN)
    
    elif d == "shop":
        msg = "🛒 **Магазин:**\n\n"
        kb = []
        for i in SHOP_ITEMS:
            msg += f"{i['emoji']} **{i['name']}** ({i['rarity_name']}) — {i['cost']}💫\n"
            kb.append([InlineKeyboardButton(f"Купить {i['name']} - {i['cost']}💫", callback_data=f"buy_{i['id']}")])
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d.startswith("buy_"):
        item_id = d[4:]
        ok, msg = game.buy(uid, item_id)
        await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)
    
    elif d == "tarot":
        msg = game.tarot(uid)
        kb = [[InlineKeyboardButton("🔮 Ещё карту", callback_data="tarot")]]
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d == "music":
        msg = "🎵 **Музыка:**\n\n"
        kb = []
        for t in MUSIC_TRACKS:
            msg += f"• {t['name']}\n"
            kb.append([InlineKeyboardButton(f"▶ {t['name']}", url=t['url'])])
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d == "moon":
        m = get_moon()
        phases = list(MoonPhase)
        next_phase = phases[(m.value[3] + 1) % 8]
        await q.edit_message_text(
            f"{m.value[0]} **{m.value[1]}**\n\n{m.value[2]}\n\nСледующая: {next_phase.value[0]} {next_phase.value[1]}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif d == "friends":
        fr = friend_system.get_friends(uid)
        if not fr:
            await q.edit_message_text(f"👥 Нет друзей.\nТвой ID: `{uid}`\n/addfriend [ID]", parse_mode=ParseMode.MARKDOWN)
            return
        msg = "👥 **Друзья:**\n\n"
        kb = []
        for f in fr:
            msg += f"{f.get('status','✅')} **{f.get('name','Друг')}** | 💫 {f.get('friendship_points',0)}\n"
            kb.append([InlineKeyboardButton(f"💬 Чат с {f['name']}", callback_data=f"chat_{f['friend_id']}")])
            kb.append([InlineKeyboardButton(f"🎁 Подарок {f['name']}", callback_data=f"gift_{f['friend_id']}")])
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d == "friendrequests":
        reqs = friend_system.get_pending_requests(uid)
        if not reqs:
            await q.edit_message_text("📭 Нет заявок.")
            return
        msg = "📬 **Заявки:**\n\n"
        kb = []
        for r in reqs:
            msg += f"• **{r.get('from_name','?')}**\n"
            kb.append([
                InlineKeyboardButton(f"✅ Принять", callback_data=f"accept_{r['from']}"),
                InlineKeyboardButton(f"❌ Отклонить", callback_data=f"decline_{r['from']}")
            ])
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d.startswith("accept_"):
        fid = d[7:]
        my_name = q.from_user.first_name or "Друг"
        ok, msg = friend_system.accept_request(uid, my_name, fid)
        await q.edit_message_text(msg)
    
    elif d.startswith("decline_"):
        fid = d[8:]
        ok, msg = friend_system.decline_request(uid, fid)
        await q.edit_message_text(msg)
    
    elif d.startswith("gift_"):
        fid = d[5:]
        ok, msg = friend_system.send_gift(uid, fid)
        await q.edit_message_text(msg)
    
    # === ЧАТ CALLBACK ===
    elif d.startswith("chat_"):
        fid = d[5:]
        await q.edit_message_text(f"💬 Чтобы написать другу, используй команду:\n/chat {fid} [сообщение]\n\nПрочитать чат:\n/readchat {fid}")
    
    elif d == "achievements":
        p = game.gp(uid)
        ach = p.get("achievements", [])
        await q.edit_message_text(f"🏆 Достижения: {len(ach)}\n\nИспользуй /achievements для полного списка")
    
    elif d == "help":
        await q.edit_message_text(game.help(), parse_mode=ParseMode.MARKDOWN)
    
    # === ФАКТЫ CALLBACK ===
    elif d == "fact":
        fact = random.choice(FUN_FACTS)
        kb = [[InlineKeyboardButton("💡 Ещё факт!", callback_data="fact")]]
        await q.edit_message_text(f"💡 **Случайный факт:**\n\n{fact}", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    # === МИНИ-ИГРЫ CALLBACK ===
    elif d == "minigame":
        kb = [
            [InlineKeyboardButton("🚀 Космический бегун", callback_data="minigame_space_runner")],
            [InlineKeyboardButton("🌙 Лунная викторина", callback_data="minigame_moon_quiz")],
        ]
        await q.edit_message_text("🎮 **Мини-игры:**\n\nВыбери игру:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == "minigame_space_runner":
        msg, kb = game.space_runner(uid, "start")
        if kb:
            await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        else:
            await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)
    
    elif d == "minigame_space_runner_run":
        msg, kb = game.space_runner(uid, "run")
        if kb:
            await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        else:
            await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)
    
    elif d == "minigame_space_runner_boost":
        msg, kb = game.space_runner(uid, "boost")
        if kb:
            await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        else:
            await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)
    
    elif d == "minigame_space_runner_end":
        msg, kb = game.space_runner(uid, "end")
        await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)
    
    elif d == "minigame_moon_quiz":
        msg, kb = game.moon_quiz(uid)
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif d.startswith("quiz_answer_"):
        answer_idx = int(d.split("_")[2])
        msg = game.check_quiz(uid, answer_idx)
        await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)
    
    # === КЛАН CALLBACK ===
    elif d == "myclan":
        uid = str(q.from_user.id)
        clan = clan_system.get_my_clan(uid)
        if not clan:
            await q.edit_message_text("🏰 Вы не в клане.\n/createclan [название] — создать\n/joinclan [ID] — вступить")
            return
        members = "\n".join([f"• {name}" for name in list(clan["member_names"].values())[:10]])
        msg = f"🏰 **Клан: {clan['name']}**\n\n👑 Лидер: {clan['owner_name']}\n⭐ Уровень: {clan['level']}\n👥 Участники ({len(clan['members'])}):\n{members}\n\nID: `{clan['id']}`"
        await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)

# === MESSAGE HANDLER ===
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if any(g in text for g in ["привет", "хай", "здравствуй", "hi", "hello", "добрый"]):
        uid = str(update.effective_user.id) if update.effective_user else "0"
        p = game.gp(uid)
        m = get_moon()
        await update.message.reply_text(
            f"{m.value[0]} Привет, {p['name']}! {m.value[2]}\n\nИспользуй /help для списка команд!"
        )
    else:
        await update.message.reply_text("🌙 Я не совсем понял. Используй /help для списка команд!")

# === ЗАПУСК ===
def main():
    print(f"""
╔══════════════════════════════════════════╗
║     🌙 {GAME_NAME} v{VERSION}    ║
║   Космическая игра заботы о себе   ║
║  + Чат + Мини-игры + Кланы + Факты ║
╚══════════════════════════════════════════╝
    """)
    
    token = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f: token = f.read().strip()
    if not token:
        token = input("Введите токен бота: ").strip()
        if token and input("Сохранить токен? (y/n): ").lower() == "y":
            with open(TOKEN_FILE, "w") as f: f.write(token)
    if not token:
        print("❌ Токен не указан")
        sys.exit(1)
    
    print("🚀 Запуск бота...")
    app = Application.builder().token(token).build()
    
    # Все команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("daily", daily_cmd))
    app.add_handler(CommandHandler("checkin", checkin_cmd))
    app.add_handler(CommandHandler("affirmation", affirmation_cmd))
    app.add_handler(CommandHandler("support", support_cmd))
    app.add_handler(CommandHandler("meditate", meditate_cmd))
    app.add_handler(CommandHandler("mood", mood_cmd))
    app.add_handler(CommandHandler("dream", dream_cmd))
    app.add_handler(CommandHandler("moodstats", moodstats_cmd))
    app.add_handler(CommandHandler("addfriend", addfriend_cmd))
    app.add_handler(CommandHandler("friends", friends_cmd))
    app.add_handler(CommandHandler("friendrequests", friendrequests_cmd))
    app.add_handler(CommandHandler("sendgift", sendgift_cmd))
    app.add_handler(CommandHandler("chat", chat_cmd))
    app.add_handler(CommandHandler("readchat", readchat_cmd))
    app.add_handler(CommandHandler("createclan", createclan_cmd))
    app.add_handler(CommandHandler("joinclan", joinclan_cmd))
    app.add_handler(CommandHandler("myclan", myclan_cmd))
    app.add_handler(CommandHandler("leaveclan", leaveclan_cmd))
    app.add_handler(CommandHandler("shop", shop_cmd))
    app.add_handler(CommandHandler("buy", buy_cmd))
    app.add_handler(CommandHandler("inventory", inventory_cmd))
    app.add_handler(CommandHandler("tarot", tarot_cmd))
    app.add_handler(CommandHandler("music", music_cmd))
    app.add_handler(CommandHandler("moon", moon_cmd))
    app.add_handler(CommandHandler("achievements", achievements_cmd))
    app.add_handler(CommandHandler("fact", fact_cmd))
    app.add_handler(CommandHandler("minigame", minigame_cmd))
    
    # Callback и сообщения
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))
    
    print("✅ Бот запущен! Нажми Ctrl+C для остановки")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()