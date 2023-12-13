[![Foodgram workflow](https://github.com/rodichevm/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/rodichevm/foodgram-project-react/actions/workflows/main.yml)

`Python` `Django` `Django Rest Framework` `Docker` `Gunicorn` `NGINX` `PostgreSQL` `Yandex Cloud` `Continuous Integration` `Continuous Deployment`

# Foodgram(«Продуктовый помощник».)

На этом сервисе пользователи публикуют свои рецепты, подписываются на публикации других пользователей, добавляют понравившиеся рецепты в список «Избранное», и могут скачивать список продуктов.

**Ссылка на проект http://foodgramers.ddns.net**

**Ссылка на проект http://foodgramers.ddns.net/admin**

### _Развернуть проект на удаленном сервере:_

**_Склонировать репозиторий_**
```
git@github.com:rodichevm/foodgram-project-react.git
```
**_Установить на сервере Docker, Docker Compose:_**
```
sudo apt install curl                                   - установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      - скачать скрипт для установки
sh get-docker.sh                                        - запуск скрипта
sudo apt-get install docker-compose-plugin              - последняя версия docker compose
```
**_Скопировать на сервер файлы docker-compose.production.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):_**
```
scp docker-compose.production.yml username@IP:/home/username/
scp nginx.conf username@IP:/home/username/

# username - имя пользователя на сервере
# IP - публичный IP сервера
```

**_Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:_**
```

TOKEN                   - секретный ключ Django проекта
DOCKER_PASSWORD         - пароль от Docker Hub
DOCKER_USERNAME         - логин Docker Hub
HOST                    - публичный IP сервера
USER                    - имя пользователя на сервере
SSH_PASSPHRASE          - если ssh-ключ защищен паролем
SSH_KEY                 - приватный ssh-ключ
TELEGRAM_TO             - ID телеграм-аккаунта для отправки сообщения об успешном деплое
TELEGRAM_TOKEN          - токен бота, отправляющего сообщение


DB_ENGINE               - django.db.backends.postgresql
DB_NAME                 - postgres
POSTGRES_USER           - postgres
POSTGRES_PASSWORD       - postgres
DB_HOST                 - db
DB_PORT                 - 5432 (порт по умолчанию)
```

**_Создать и запустить контейнеры Docker, выполнить команду на сервере (версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):**_
```
sudo docker compose up -d
```
**_Выполнить миграции:_**
```
sudo docker compose exec backend python manage.py migrate
```
**_Собрать статику:_**
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```
**_Наполнить базу данных ингредиентами для рецептов**
```
sudo docker compose exec backend python manage.py dataload
```
**_Создать суперпользователя:_**
```
sudo docker compose exec backend python manage.py createsuperuser
```
**_Для остановки контейнеров Docker:_**
```
sudo docker compose down -v      - с их удалением
sudo docker compose stop         - без удаления
```
### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend, backend и gateway на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

### Локальный запуск проекта:

**_Склонировать репозиторий_**
```
git@github.com:rodichevm/foodgram-project-react.git
```

**_В директории infra создать файл .env и заполнить данными:_**
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

**_Создать и запустить контейнеры Docker_**

**_После запуска проект будут доступен по адресу: http://localhost/_**

**_Документация будет доступна по адресу: http://localhost/api/docs/_**


### Автор
**Михаил Родичев (https://github.com/rodichevm)**