# 🤖 Aether Multi-Agent Bot

## 🎯 **Обзор**

Multi-agent Telegram бот с AI моделями (Claude, Mistral, Groq, Gemini), системой мониторинга и enterprise-level security.

## 🏗️ **Архитектура**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot   │────│  AI Agent Hub    │────│  Model Router   │
│   (aiogram)      │    │  (FastAPI)       │    │  (Multi-model)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Session Mgmt   │────│   Redis Cache    │────│  Audit Logger   │
│   (Memory)      │    │   (Sessions)     │    │   (Security)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Prometheus     │────│   Grafana        │────│  AlertManager   │
│  (Metrics)      │    │   (Dashboards)   │    │   (Alerts)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔥 **Фичи**

### 🤖 **Multi-Agent System**
- **AI Agent Hub** - Центральный менеджер агентов
- **Model Router** - Умный роутинг между AI моделями
- **Session Management** - Контекст и история сессий
- **Agent Orchestration** - Координация между агентами

### 🧠 **AI Модели**
- **Claude (Anthropic)** - Для сложных рассуждений
- **Mistral** - Для быстрых ответов
- **Groq** - Для real-time обработки
- **Gemini (Google)** - Для мультимодальных задач

### 📊 **Monitoring & Observability**
- **Prometheus** - Сбор метрик
- **Grafana** - Дашборды и визуализация
- **AlertManager** - Алерты и уведомления
- **Health Checks** - Мониторинг здоровья системы

### 🔒 **Security & Compliance**
- **User Authentication** - Доступ только по Telegram ID
- **Audit Logging** - Полный лог всех действий
- **Rate Limiting** - Защита от abuse
- **Secret Management** - Безопасное хранение ключей

## 🚀 **Ключевые команды**

```
/start          - Приветствие и информация
/agents         - Список активных AI агентов
/status         - Статус системы и метрики
/history        - История сессий
/restore <id>   - Восстановление сессии
/reset          - Сброс и архивация
/monitor        - Мониторинг системы
```

## 🏗️ **Технологический стек**

### Backend
- **FastAPI** - API для AI Agent Hub
- **aiogram** - Telegram Bot Framework
- **Redis** - Сессии и кэширование
- **asyncio** - Асинхронная обработка

### AI & ML
- **Anthropic Claude** - LLM для рассуждений
- **Mistral AI** - Быстрые ответы
- **Groq** - Real-time обработка
- **Google Gemini** - Мультимодальность

### Infrastructure
- **Docker** - Контейнеризация
- **Docker Compose** - Оркестрация
- **Prometheus** - Метрики
- **Grafana** - Визуализация

### Security
- **Telegram ID Auth** - Аутентификация
- **Audit Logging** - Логирование
- **Rate Limiting** - Лимиты запросов
- **Secret Management** - Управление секретами

## 📁 **Структура проекта**

```
aether-multi-agent-bot/
├── bot/                    # Telegram бот
│   ├── main.py            # Основной файл бота
│   ├── handlers/          # Обработчики команд
│   ├── middleware/        # Middleware для безопасности
│   └── utils/             # Утилиты бота
├── agents/                # AI агенты
│   ├── hub.py            # AI Agent Hub (FastAPI)
│   ├── models/           # Интеграции с AI моделями
│   ├── router.py         # Роутер запросов
│   └── orchestrator.py   # Оркестратор агентов
├── core/                  # Ядро системы
│   ├── security.py       # Безопасность
│   ├── session.py        # Управление сессиями
│   ├── audit.py          # Аудит логирование
│   └── config.py         # Конфигурация
├── monitoring/            # Мониторинг
│   ├── prometheus.yml    # Конфиг Prometheus
│   ├── grafana/          # Дашборды Grafana
│   └── alerts.yml        # Правила алертов
├── docker/               # Docker конфиги
│   ├── Dockerfile        # Основной образ
│   ├── docker-compose.yml # Все сервисы
│   └── nginx.conf        # Nginx конфиг
├── scripts/              # Скрипты деплоя
│   ├── deploy.sh         # Деплой на сервер
│   ├── setup.sh          # Первичная настройка
│   └── health.sh         # Health checks
└── docs/                 # Документация
    ├── API.md            # API документация
    ├── DEPLOYMENT.md     # Инструкция деплоя
    └── SECURITY.md       # Политика безопасности
```

## 🔐 **Безопасность**

### 🚨 **Критически важные правила**
- **НИКОГДА не коммитить `.env` файл**
- **Все ключи только в GitHub Secrets**
- **Доступ только по Telegram ID**
- **Полный аудит всех действий**

### 🛡️ **Меры безопасности**
- **User Authentication** - Проверка Telegram ID
- **Rate Limiting** - 10 запросов в минуту
- **Audit Logging** - Запись всех действий
- **Secret Rotation** - Регулярная смена ключей

## 📊 **Мониторинг**

### 📈 **Метрики**
- **Request Rate** - Частота запросов
- **Response Time** - Время ответа
- **Error Rate** - Частота ошибок
- **Active Sessions** - Активные сессии
- **Model Usage** - Использование AI моделей

### 🚨 **Алерты**
- **High Error Rate** - Много ошибок
- **Slow Response** - Медленные ответы
- **Service Down** - Сервис недоступен
- **Security Events** - Подозрительные действия

## 🚀 **Быстрый старт**

### 1️⃣ **Клонирование**
```bash
git clone https://github.com/твой-username/aether-multi-agent-bot.git
cd aether-multi-agent-bot
```

### 2️⃣ **Настройка секретов**
```bash
cp .env.example .env
# Заполнить все переменные в .env
```

### 3️⃣ **Запуск**
```bash
docker compose up -d --build
```

### 4️⃣ **Проверка**
```bash
# Health check
curl http://localhost:8080/health

# Telegram бот
# Напиши /start боту
```

## 📞 **Поддержка**

### 🆘 **Траблшутинг**
- **Логи:** `docker compose logs -f`
- **Статус:** `docker compose ps`
- **Перезапуск:** `docker compose restart`

### 📧 **Контакты**
- **GitHub Issues:** Для баг-репортов
- **Telegram:** Для оперативной связи

---

**🎯 Status: In Development**
**🔒 Security: Enterprise Level**
**🚀 Ready for Production**

---

**Создан с ❤️ для Aether OS Ecosystem**
