# 📊 Services Status API

REST API для отслеживания и управления статусами различных сервисов. Предоставляет возможности обновления статусов, получения актуальных данных и расчёта уровня доступности (SLA) сервисов за заданный период времени.

---

## 🚀 Возможности

- ✅ Обновление статуса сервиса с сохранением истории изменений
- 📋 Получение актуального статуса всех сервисов
- 📈 Расчёт уровня доступности (SLA) за указанный период времени
- 🐳 Развёртывание с использованием Docker Compose
- 🧪 Миграции базы данных с использованием Alembic

---

## 🧰 Технологии

- Python 3.10+
- FastAPI
- PostgreSQL
- Alembic
- Docker & Docker Compose

---

## ⚙️ Установка и запуск

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/artem-sitd/ServicesStatusFastapi.git
   cd ServicesStatusFastapi
   ```

2. **Настройте переменные окружения:**

   Переименуйте файл `.env.docker.template` в `.env.docker`:

   ```bash
   cp .env.docker.template .env.docker
   ```

   Отредактируйте файл `.env.docker`, указав необходимые значения:

   - `POSTGRES_USER` — имя пользователя PostgreSQL
   - `POSTGRES_PASSWORD` — пароль пользователя PostgreSQL
   - `POSTGRES_DB` — имя базы данных

3. **Запустите приложение с помощью Docker Compose:**

   ```bash
   docker-compose up --build
   ```

   Приложение будет доступно по адресу `http://localhost:8000`.

---

## 📁 Структура проекта

```
├── alembic/               # Миграции базы данных
├── app/                   # Основная логика приложения
├── .env.docker.template   # Шаблон переменных окружения
├── docker-compose.yaml    # Конфигурация Docker Compose
├── main.py                # Точка входа в приложение
├── pyproject.toml         # Зависимости проекта
├── settings.py            # Настройки приложения
└── README.md              # Документация проекта
```

---

## 📄 Лицензия

Проект распространяется под лицензией MIT. Подробнее см. файл `LICENSE`.
