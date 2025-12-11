Развёртывание
=============

Docker
------

Dockerfile
~~~~~~~~~~

.. code-block:: dockerfile

   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8000

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

docker-compose.yml
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   version: '3.8'

   services:
     web:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://user:pass@db/clinic_db
       depends_on:
         - db

     db:
       image: postgres:14
       environment:
         - POSTGRES_USER=user
         - POSTGRES_PASSWORD=pass
         - POSTGRES_DB=clinic_db
       volumes:
         - postgres_data:/var/lib/postgresql/data

   volumes:
     postgres_data:

Запуск:

.. code-block:: bash

   docker-compose up -d

Production
----------

Gunicorn + Nginx
~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install gunicorn

   gunicorn app.main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000