Архитектура системы
===================

Структура проекта
-----------------

.. code-block:: text

   clinic_rest_service/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py                 # Точка входа FastAPI
   │   ├── database.py             # Подключение к БД
   │   ├── logger.py               # Настройка логирования
   │   ├── problem_details.py      # RFC 7807 обработка ошибок
   │   ├── models/
   │   │   ├── entities.py         # Dataclass модели
   │   │   └── database.py         # SQLAlchemy модели
   │   ├── schemas/
   │   │   └── schemas.py          # Pydantic схемы
   │   ├── services/
   │   │   ├── patient_service.py
   │   │   ├── doctor_service.py
   │   │   └── appointment_service.py
   │   ├── controllers/
   │   │   ├── patient_controller.py
   │   │   ├── doctor_controller.py
   │   │   └── appointment_controller.py
   │   └── exceptions/
   │       └── custom_exceptions.py
   ├── logs/
   ├── .env
   ├── requirements.txt
   └── README.md

Архитектурные слои
------------------

Система построена по трёхслойной архитектуре:

1. **Presentation Layer (Controllers)**
   
   * Обработка HTTP запросов
   * Валидация входных данных
   * Формирование ответов

2. **Business Logic Layer (Services)**
   
   * Бизнес-логика и правила
   * Валидация данных
   * Управление транзакциями

3. **Data Access Layer (Models + Database)**
   
   * SQLAlchemy ORM
   * Работа с БД
   * Миграции схемы

Паттерны проектирования
-----------------------

Repository Pattern
~~~~~~~~~~~~~~~~~~

Сервисы инкапсулируют логику доступа к данным:

.. code-block:: python

   class PatientService:
       def __init__(self, db: Session):
           self.db = db
       
       def get_patient_by_id(self, patient_id: int) -> PatientDB:
           # Логика получения пациента

Dependency Injection
~~~~~~~~~~~~~~~~~~~~

FastAPI автоматически инжектирует зависимости:

.. code-block:: python

   @router.post("/")
   def create_patient(
       patient: PatientCreate,
       db: Session = Depends(get_db)
   ):
       service = PatientService(db)
       return service.create_patient(patient)

DTO Pattern
~~~~~~~~~~~

Pydantic схемы для передачи данных:

.. code-block:: python

   class PatientCreate(BaseModel):
       fio: str
       birth_date: date
       phone: str
       # ...

Обработка ошибок
----------------

Используется стандарт **RFC 7807 Problem Details**:

.. code-block:: json

   {
     "type": "ValidationException",
     "title": "Ошибка валидации данных",
     "status": 400,
     "detail": "ФИО должно содержать минимум 3 слова",
     "instance": "/api/patients"
   }

Типы исключений:

* ``NotFoundException`` (404)
* ``ValidationException`` (400)
* ``AlreadyExistsException`` (409)
* ``TimeConflictException`` (409)
* ``MaxAppointmentsExceededException`` (429)
* ``BusinessLogicException`` (422)
* ``DatabaseException`` (500)