<div align="center">

# 📊 Pinterest Аналитика

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Pinterest API](https://img.shields.io/badge/Pinterest-API%20v5-red.svg?logo=pinterest)](https://developers.pinterest.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)

**Мощный инструмент аналитики для вашего Pinterest аккаунта**

[English](../README.md) • [Русский](#возможности)

</div>

---

## ✨ Возможности

| Функция | Описание |
|---------|----------|
| 📈 **Аналитика аккаунта** | Просмотр подписчиков, пинов, досок |
| 📋 **Статистика досок** | Детальные метрики каждой доски |
| 📌 **Эффективность пинов** | Отслеживание вовлечённости |
| 📊 **Экспорт отчётов** | Экспорт в JSON, CSV, Excel |
| 🔒 **Приватность** | Все данные хранятся локально |
| 🚀 **Быстрый и лёгкий** | CLI-интерфейс, минимум зависимостей |

## 🚀 Быстрый старт

### Требования

- Python 3.8 или выше
- Pinterest Business аккаунт (рекомендуется)
- Учётные данные Pinterest Developer

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/xodapi/pin.git
cd pin

# Создание виртуального окружения
python -m venv .venv

# Активация (Windows)
.venv\Scripts\activate

# Активация (Linux/Mac)
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### Настройка

1. Создайте приложение Pinterest на [developers.pinterest.com](https://developers.pinterest.com/apps/)
2. Скопируйте пример конфигурации:
   ```bash
   copy .env.example .env
   ```
3. Добавьте свои учётные данные в `.env`:
   ```env
   PINTEREST_APP_ID=ваш_app_id
   PINTEREST_APP_SECRET=ваш_app_secret
   ```
4. Получите токен доступа:
   ```bash
   python get_token.py
   ```

### Использование

```bash
# Проверка подключения
python main.py test

# Информация об аккаунте
python main.py account

# Список досок
python main.py boards

# Список пинов
python main.py pins

# Сводка
python main.py summary

# Экспорт всех данных
python main.py export -t all -f json
```

## 📖 Документация

| Документ | Описание |
|----------|----------|
| [Руководство по установке](INSTALL.ru.md) | Подробная инструкция по установке |
| [Политика конфиденциальности](../PRIVACY.md) | Как мы обрабатываем ваши данные |

## 🛠️ Доступные команды

```
main.py <команда> [опции]

Команды:
  test        Проверка подключения к Pinterest API
  account     Информация об аккаунте
  boards      Список всех досок со статистикой
  pins        Список пинов (-n лимит, -b доска)
  summary     Сводка с топ-досками
  analytics   Детальная аналитика (Business аккаунты)
  export      Экспорт в файл (-t тип, -f формат)

Опции:
  -n, --limit    Количество элементов
  -b, --board    ID доски для фильтрации
  -t, --type     Тип экспорта: summary, boards, pins, all
  -f, --format   Формат: json, csv, excel
```

## 🔐 Безопасность и приватность

- ✅ **Без сбора данных** — Все данные остаются на вашем устройстве
- ✅ **Без передачи третьим лицам** — Мы никогда не передаём ваши данные
- ✅ **Открытый исходный код** — Проверяйте код в любое время
- ✅ **GDPR соответствие** — Полный контроль над вашими данными

Читать полную [Политику конфиденциальности](../PRIVACY.md).

## 📄 Лицензия

Этот проект лицензирован под MIT License — см. файл [LICENSE](../LICENSE).

---

<div align="center">

**⭐ Поставьте звезду, если проект полезен!**

Сделано с ❤️

</div>
