# Pinterest Analytics

Инструмент для получения аналитики вашего Pinterest аккаунта.

## Быстрый старт

### 1. Установка

```bash
cd c:\project\pin

# Активация виртуального окружения
.venv\Scripts\activate

# Зависимости уже установлены!
```

### 2. Получение Access Token

1. Откройте: https://developers.pinterest.com/tools/access_token/
2. Войдите в ваш Pinterest аккаунт
3. Выберите разрешения:
   - `boards:read` — чтение досок
   - `pins:read` — чтение пинов  
   - `user_accounts:read` — информация об аккаунте
4. Нажмите "Generate token"
5. Скопируйте токен

### 3. Настройка

```bash
copy .env.example .env
```

Откройте `.env` и вставьте ваш токен:
```
PINTEREST_ACCESS_TOKEN=pina_ваш_токен_здесь
```

### 4. Проверка

```bash
python main.py test
```

## Команды

```bash
# Тест подключения
python main.py test

# Информация об аккаунте
python main.py account

# Список досок
python main.py boards

# Список пинов
python main.py pins
python main.py pins -n 50              # 50 пинов
python main.py pins -b BOARD_ID        # Пины из конкретной доски

# Сводка по аккаунту
python main.py summary

# Аналитика (только Business аккаунт)
python main.py analytics

# Экспорт данных
python main.py export -t all -f json   # Всё в JSON
python main.py export -t boards -f excel  # Доски в Excel
python main.py export -t pins -f csv   # Пины в CSV
```

## Типы экспорта

| Тип | Описание |
|-----|----------|
| `summary` | Сводка по аккаунту |
| `boards` | Все доски |
| `pins` | Все пины |
| `all` | Полный отчёт |

## Структура

```
pin/
├── main.py           # CLI
├── .env              # Ваш токен (создать!)
├── .env.example      # Шаблон
├── requirements.txt
├── src/
│   ├── auth.py       # Авторизация
│   ├── analytics.py  # Получение данных
│   └── report.py     # Генерация отчётов
└── reports/          # Сохранённые отчёты
```

## Решение проблем

### "Access Token not configured"
Создайте файл `.env` с вашим токеном.

### "401 Unauthorized" 
Токен истёк. Сгенерируйте новый на developers.pinterest.com/tools/access_token/

### Не получается получить аналитику
Расширенная аналитика (impressions, clicks) доступна только для **Business аккаунтов**.
Конвертировать можно на: pinterest.com/business/hub/
