[![Foodgram workflow](https://github.com/rodichevm/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/rodichevm/foodgram-project-react/actions/workflows/main.yml)

`Python` `Django` `Django Rest Framework` `Docker` `Gunicorn` `NGINX` `PostgreSQL` `Yandex Cloud` `Continuous Integration` `Continuous Deployment`

# Foodgram(«Продуктовый помощник».)

На этом сервисе пользователи публикуют свои рецепты, подписываются на публикации других пользователей, добавляют понравившиеся рецепты в список «Избранное», и могут скачивать список продуктов.

**Ссылка на проект http://foodgramers.ddns.net**

**Ссылка на админ-зону проекта http://foodgramers.ddns.net/admin**

**Ссылка на API документацию проекта http://foodgramers.ddns.net/api/docs/**



### Развернуть проект на удаленном сервере:

**Склонировать репозиторий**
```
git@github.com:rodichevm/foodgram-project-react.git
```
**Установить на сервере Docker, Docker Compose:**
```
sudo apt install curl                                   - установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      - скачать скрипт для установки
sh get-docker.sh                                        - запуск скрипта
sudo apt-get install docker-compose-plugin              - последняя версия docker compose
```
**Скопировать на сервер файлы docker-compose.production.yml, nginx.conf:**
```
scp docker-compose.production.yml username@IP:/home/username/
scp nginx.conf username@IP:/home/username/

# username - имя пользователя на сервере
# IP - публичный IP сервера
```

**Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:**
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

```
**Создать директорию "foodgram" на сервере и внутри директории, файл .env и наполнить переменными:**
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

**Создать и запустить контейнеры Docker, выполнить команду на сервере в директории с docker-compose.production**
```
sudo docker compose up -d
```
**Выполнить миграции:**
```
sudo docker compose exec backend_foodgram python manage.py migrate
```
**Собрать статику:**
```
sudo docker compose exec backend_foodgram python manage.py collectstatic
```
**Наполнить базу данных списком ингредиентов для рецептов**
```
sudo docker compose exec backend_foodgram python manage.py load_ingredients
```
**Наполнить базу данных списком тегов для рецептов**
```
sudo docker compose exec backend_foodgram python manage.py load_tags
```
**Создать суперпользователя:**
```
sudo docker compose exec backend_foodgram python manage.py createsuperuser
```
**Для остановки контейнеров Docker:**
```
sudo docker compose down -v      - с их удалением
sudo docker compose stop         - без удаления
```
### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend, backend и gateway на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram об успешном выполнении деплоя

### Локальный запуск проекта:

**Склонировать репозиторий**
```
git@github.com:rodichevm/foodgram-project-react.git
```

**В директории проекта c docker-compose создать файл .env и заполнить данными:**
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

**Создать и запустить контейнеры Docker (выполнять команду, находясь в директории с файлом docker-compose)**
```
docker compose up -d
```

**После локального запуска проект будет доступен по адресу: http://localhost/**


### Автор
**Михаил Родичев (https://github.com/rodichevm)**
