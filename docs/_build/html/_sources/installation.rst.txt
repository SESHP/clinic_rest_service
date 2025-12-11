Установка и настройка
=====================

Системные требования
--------------------

* Python 3.11+
* PostgreSQL 14+ или SQLite 3
* pip 23+

Установка
---------

1. Клонирование репозитория
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/username/clinic_rest_service.git
   cd clinic_rest_service

2. Создание виртуального окружения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate  # Windows

3. Установка зависимостей
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements.txt

4. Настройка переменных окружения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Создайте файл ``.env`` в корне проекта:

.. code-block:: bash

   DATABASE_URL=sqlite:///./clinic.db
   LOG_FILE=logs/app.log
   LOG_LEVEL=INFO

Для PostgreSQL:

.. code-block:: bash

   DATABASE_URL=postgresql://user:password@localhost/clinic_db
   LOG_FILE=logs/app.log
   LOG_LEVEL=INFO

5. Инициализация базы данных
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

База данных создаётся автоматически при первом запуске:

.. code-block:: bash

   uvicorn app.main:app --reload

Запуск
------

Локальный сервер
~~~~~~~~~~~~~~~~

.. code-block:: bash

   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Проверка работы
~~~~~~~~~~~~~~~

Откройте в браузере:

* http://localhost:8000 - корневой endpoint
* http://localhost:8000/docs - Swagger UI
* http://localhost:8000/redoc - ReDoc

Тестирование
------------

.. code-block:: bash

   pytest tests/