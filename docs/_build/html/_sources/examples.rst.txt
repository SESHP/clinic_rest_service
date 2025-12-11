Примеры использования
=====================

Python примеры
--------------

Создание пациента
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import requests

   BASE_URL = "http://localhost:8000"

   patient_data = {
       "fio": "Иванов Иван Иванович",
       "birth_date": "1990-01-15",
       "phone": "+79161234567",
       "address": "г. Москва, ул. Ленина, д. 10",
       "insurance_number": "1234567890123456"
   }

   response = requests.post(f"{BASE_URL}/api/patients", json=patient_data)
   patient = response.json()
   print(f"Создан пациент ID: {patient['id']}")

Запись на приём
~~~~~~~~~~~~~~~

.. code-block:: python

   appointment_data = {
       "patient_id": 1,
       "doctor_id": 1,
       "appointment_date": "2025-12-15",
       "appointment_time": "10:00"
   }

   response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
   appointment = response.json()
   print(f"Создана запись ID: {appointment['id']}")

Получение расписания врача
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   doctor_id = 1
   date = "2025-12-15"

   response = requests.get(
       f"{BASE_URL}/api/doctors/{doctor_id}/schedule",
       params={"date": date}
   )
   schedule = response.json()
   print(f"Расписание врача: {len(schedule)} записей")

curl примеры
------------

Создание врача
~~~~~~~~~~~~~~

.. code-block:: bash

   curl -X POST http://localhost:8000/api/doctors \
     -H "Content-Type: application/json" \
     -d '{
       "fio": "Петров Петр Петрович",
       "specialization": "Терапевт",
       "cabinet_number": "101",
       "phone": "+79161111111",
       "experience_years": 10
     }'

Получение списка пациентов
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/api/patients

История приёмов пациента
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/api/patients/1/appointments