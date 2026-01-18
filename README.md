# REST-сервис "Поликлиника"

Курсовой проект по дисциплине "Технология программирования"

## Описание проекта

REST API для управления поликлиникой с полной реализацией CRUD операций, валидацией данных, обработкой исключений и логированием.

### Предметная область

- **Пациенты** - регистрация и управление данными пациентов
- **Врачи** - учет врачей с привязкой к специализациям и кабинетам
- **Специализации** - справочник медицинских специализаций (врач может иметь несколько)
- **Кабинеты** - справочник кабинетов поликлиники
- **Приемы** - записи пациентов на прием к врачам

## Реализованные требования

- База данных SQLite с 5 связанными таблицами
- CRUD операции для всех сущностей
- Связь многие-ко-многим между врачами и специализациями
- Валидация данных через Pydantic схемы
- Обработка пользовательских исключений
- Problem Details (RFC 7807) для форматирования ошибок
- Логирование всех операций и исключительных событий
- Unit-тестирование с демонстрацией работы
- Автоматическая документация API (Swagger/OpenAPI)

## Структура проекта

```
clinic_rest_service/
├── app/
│   ├── controllers/          # REST API endpoints
│   │   ├── patient_controller.py
│   │   ├── doctor_controller.py
│   │   ├── appointment_controller.py
│   │   ├── specialization_controller.py
│   │   └── cabinet_controller.py
│   ├── services/             # Бизнес-логика
│   │   ├── patient_service.py
│   │   ├── doctor_service.py
│   │   ├── appointment_service.py
│   │   ├── specialization_service.py
│   │   └── cabinet_service.py
│   ├── models/               # Модели данных
│   │   ├── entities.py       # Dataclass модели
│   │   └── database.py       # SQLAlchemy модели
│   ├── schemas.py            # Pydantic схемы
│   ├── exceptions.py         # Пользовательские исключения
│   ├── init_data.py          # Инициализация данных
│   ├── logger.py             # Настройка логирования
│   ├── problem_details.py    # RFC 7807 Problem Details
│   └── main.py               # Главный файл приложения
├── tests/
│   └── test_services.py      # Unit-тесты
├── requirements.txt          # Зависимости
└── README.md
```

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/SESHP/clinic_rest_service.git
cd clinic_rest_service
```

### 2. Создание виртуального окружения

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Запуск сервера

```bash
python -m app.main
```

Или через uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: http://localhost:8000

При первом запуске автоматически создается база данных SQLite и заполняется начальными данными (специализации, кабинеты, тестовые врачи и пациенты).

## API Документация

После запуска сервера документация доступна по адресам:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Запуск тестов

```bash
python -m pytest tests/ -v
```

Или напрямую:

```bash
python tests/test_services.py
```

## API Endpoints

### Специализации

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/specializations` | Создать специализацию |
| GET | `/api/specializations` | Получить все специализации |
| GET | `/api/specializations/{id}` | Получить специализацию по ID |
| DELETE | `/api/specializations/{id}` | Удалить специализацию |

### Кабинеты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/cabinets` | Создать кабинет |
| GET | `/api/cabinets` | Получить все кабинеты |
| GET | `/api/cabinets/{id}` | Получить кабинет по ID |
| PUT | `/api/cabinets/{id}` | Обновить кабинет |
| DELETE | `/api/cabinets/{id}` | Удалить кабинет |

### Пациенты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/patients` | Создать пациента |
| GET | `/api/patients` | Получить всех пациентов |
| GET | `/api/patients/{id}` | Получить пациента по ID |
| PUT | `/api/patients/{id}` | Обновить пациента |
| DELETE | `/api/patients/{id}` | Удалить пациента |

### Врачи

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/doctors` | Создать врача |
| GET | `/api/doctors` | Получить всех врачей |
| GET | `/api/doctors?specialization=Терапевт` | Фильтр по специализации |
| GET | `/api/doctors/{id}` | Получить врача по ID |
| PUT | `/api/doctors/{id}` | Обновить врача |
| DELETE | `/api/doctors/{id}` | Удалить врача |

### Приемы

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/appointments` | Создать запись на прием |
| GET | `/api/appointments` | Получить все приемы |
| GET | `/api/appointments/{id}` | Получить прием по ID |
| GET | `/api/appointments/patient/{id}` | История приемов пациента |
| GET | `/api/appointments/doctor/{id}` | Приемы врача |
| PUT | `/api/appointments/{id}` | Обновить прием |
| PATCH | `/api/appointments/{id}/cancel` | Отменить прием |
| PATCH | `/api/appointments/{id}/complete` | Завершить прием |
| DELETE | `/api/appointments/{id}` | Удалить прием |

## Бизнес-правила

### Пациенты

- ФИО должно содержать минимум 3 слова
- Дата рождения не может быть в будущем и не раньше 1900 года
- Номер телефона в формате `+7XXXXXXXXXX`
- Номер полиса ОМС уникален и содержит ровно 16 цифр
- При удалении пациента каскадно удаляются все его приемы

### Врачи

- ФИО должно содержать минимум 3 слова
- Врач может иметь несколько специализаций
- Врач привязывается к кабинету (опционально)
- Стаж работы от 0 до 60 лет
- Нельзя удалить врача с запланированными приемами

### Приемы

- Проверка существования пациента и врача
- У врача не может быть двух приемов в одно время
- Врач не может иметь более 20 приемов в день
- Между приемами минимум 20 минут
- Время приема: 8:00 - 20:00
- Нельзя отменить завершенный прием
- Нельзя установить диагноз для отмененного приема

## Примеры запросов

### Создание пациента

```bash
curl -X POST "http://localhost:8000/api/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "fio": "Иванов Иван Иванович",
    "birth_date": "1985-05-15",
    "phone": "+79161234567",
    "address": "г. Москва, ул. Ленина, д. 10",
    "insurance_number": "1234567890123456"
  }'
```

### Создание врача

```bash
curl -X POST "http://localhost:8000/api/doctors" \
  -H "Content-Type: application/json" \
  -d '{
    "fio": "Смирнов Алексей Викторович",
    "specialization_ids": [1, 2],
    "cabinet_id": 1,
    "phone": "+79161112233",
    "experience_years": 15
  }'
```

### Запись на прием

```bash
curl -X POST "http://localhost:8000/api/appointments" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "appointment_date": "2026-01-20",
    "appointment_time": "10:00",
    "status": "scheduled"
  }'
```

## Обработка ошибок

Все ошибки форматируются согласно RFC 7807 Problem Details:

```json
{
  "type": "https://api.clinic.ru/problems/409",
  "title": "Time Conflict Error",
  "status": 409,
  "detail": "У врача уже есть прием на 2026-01-20 в 10:00",
  "instance": "/api/appointments"
}
```

## Логирование

Все операции и исключения логируются в файл `logs/app.log`:

```
[2026-01-18 14:30:25] INFO - Попытка создания нового пациента: Иванов Иван Иванович
[2026-01-18 14:30:25] INFO - Пациент успешно создан с ID=1
[2026-01-18 14:35:10] WARNING - Пациент с полисом 1234567890123456 уже существует
[2026-01-18 14:40:00] ERROR - Конфликт времени у врача ID=1 на 2026-01-20 10:00
```

## Автор

SESHP  
Группа: ДИТ-31  
Астраханский государственный университет им. В. Н. Татищева

## Лицензия

Курсовой проект для образовательных целей.