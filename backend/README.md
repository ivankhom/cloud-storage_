# Облачное файловое хранилище — Backend

Django + DRF + PostgreSQL. Frontend — React (папка `frontend/`).
Инструкция ниже описывает развёртывание всего приложения (backend + frontend).

## Структура

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.py
│   ├── app_settings.py    # параметры окружения (БД, хранилище, ключи)
│   ├── urls.py             # маршрутизация + отдача собранного фронтенда
│   ├── exceptions.py       # единый формат ошибок API
│   └── wsgi.py / asgi.py
├── users/                  # пользователи и аутентификация
│   ├── models.py
│   ├── validators.py       # валидация логина/email/пароля
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/          # включая создание пользователя admin
├── storage/                 # файловое хранилище
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── deploy/                  # готовые файлы для production
│   ├── .env.production       # шаблон .env
│   ├── cloud-storage.service # systemd-юнит gunicorn
│   └── nginx.conf            # конфиг nginx
└── frontend_build/           # сюда копируется результат `npm run build`
```

## Модель данных

**User**: `username`, `full_name`, `email`, `password` (хэш), `is_admin`, `storage_path`.

**UserFile**: `owner`, `original_name`, `stored_name` (уникальное имя на диске), `comment`, `size`, `uploaded_at`, `last_downloaded_at`, `link_token`.

## API

Ошибки — в формате `{"error": "...", "details": {...}}` с HTTP-статусом.

### `/api/users/`
| Метод  | URL                        | Доступ         | Описание |
|--------|----------------------------|----------------|----------|
| GET    | `csrf/`                    | любой          | получить CSRF-cookie |
| POST   | `register/`                | любой          | регистрация |
| POST   | `login/`                   | любой          | вход |
| POST   | `logout/`                  | аутентиф.      | выход |
| GET    | `me/`                      | аутентиф.      | текущий пользователь |
| GET    | ``                         | администратор  | список пользователей |
| DELETE | `<id>/`                    | администратор  | удалить пользователя |
| PATCH  | `<id>/admin/`              | администратор  | изменить признак «администратор» |

### `/api/files/`
| Метод  | URL                  | Описание |
|--------|----------------------|----------|
| GET    | `?user=<id>`         | список файлов (`user` — только для администратора) |
| POST   | `upload/`            | загрузка (multipart: `file`, `comment`, опц. `user`) |
| DELETE | `<id>/`              | удалить файл |
| PATCH  | `<id>/rename/`       | `{"name": "..."}` |
| PATCH  | `<id>/comment/`      | `{"comment": "..."}` |
| POST   | `<id>/link/`         | перегенерировать специальную ссылку |
| GET    | `<id>/download/`     | скачать файл (требует аутентификации) |
| GET    | `/api/public/<token>/` | скачать по обезличенной ссылке (без аутентификации) |

Аутентификация — сессионная (`sessionid` + `csrftoken`). Для POST/PUT/PATCH/DELETE
фронтенд сначала запрашивает `GET /api/users/csrf/` и передаёт токен в заголовке `X-CSRFToken`.

## Локальное развёртывание

Python ≥ 3.10, Node.js ≥ 20.19, PostgreSQL ≥ 13.

### PostgreSQL

```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE cloud_storage;
CREATE USER cloud_storage_user WITH PASSWORD 'cloud_storage_password';
GRANT ALL PRIVILEGES ON DATABASE cloud_storage TO cloud_storage_user;
ALTER DATABASE cloud_storage OWNER TO cloud_storage_user;
\q
```

Значения совпадают с `.env` (см. ниже).

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# при необходимости поправьте параметры БД/секретный ключ

python manage.py migrate            # создаст таблицы + пользователя admin
python manage.py runserver 0.0.0.0:8000
```

Backend: `http://127.0.0.1:8000/`, API: `http://127.0.0.1:8000/api/...`.

По умолчанию создаётся администратор: логин `admin`, пароль `Admin123!`.
Смените пароль после первого входа, либо задайте свои
`APP_ADMIN_LOGIN`/`APP_ADMIN_PASSWORD` в `.env` до первого `migrate`.

Для проверки без PostgreSQL: `APP_USE_SQLITE=1` в `.env` (для сдачи
проекта нужен PostgreSQL).

### Frontend

Подробности — в `frontend/README.md`.

```bash
cd frontend
npm install
npm run build

rm -rf ../backend/frontend_build
cp -r dist ../backend/frontend_build
```

После этого Django отдаёт и API, и фронтенд с одного порта. Для разработки
с горячей перезагрузкой — `npm run dev` (Vite проксирует `/api` на Django).

## Развёртывание на reg.ru

Инструкция проверена для облачного сервера (VPS) reg.ru с **Ubuntu 24.04 LTS**
(подходит и 22.04). Все пути и имена файлов фиксированы — команды можно
выполнять подряд, ничего не меняя, кроме трёх значений:

| Обозначение       | Что подставить |
|-------------------|----------------|
| `<IP_СЕРВЕРА>`    | IP-адрес сервера из панели reg.ru |
| `<ПАРОЛЬ_БД>`     | придуманный вами пароль PostgreSQL (латиница и цифры, без кавычек и пробелов) |
| `<URL_РЕПОЗИТОРИЯ>` | ссылка на этот репозиторий на GitHub |

Итоговая схема: `браузер → nginx (:80) → gunicorn (127.0.0.1:8000) → Django → PostgreSQL`.
Django отдаёт и API, и собранный фронтенд. Проект лежит в `/opt/cloud-storage`
и работает от имени системного пользователя `cloud`.

### Шаг 0. Создайте сервер

В панели reg.ru: «Облачные серверы» → «Создать сервер» → образ **Ubuntu 24.04**,
минимальный тариф (1 ядро / 1 ГБ RAM / 10 ГБ диска достаточно). После создания
IP-адрес и пароль пользователя `root` показаны в карточке сервера и приходят на почту.

### Шаг 1. Войдите на сервер

```bash
ssh root@<IP_СЕРВЕРА>
```

### Шаг 2. Установите системные пакеты

```bash
apt update
apt install -y python3-venv python3-pip postgresql nginx git curl
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs
```

Node.js ставится из NodeSource, потому что сборщику фронтенда (Vite 8) нужен
Node.js ≥ 20.19, а в репозитории Ubuntu версия старее. Проверка:
`node -v` (должно быть `v22.x`), `python3 --version` (≥ 3.10).

### Шаг 3. Создайте базу данных

```bash
sudo -u postgres psql -c "CREATE USER cloud_storage_user WITH PASSWORD '<ПАРОЛЬ_БД>';"
sudo -u postgres psql -c "CREATE DATABASE cloud_storage OWNER cloud_storage_user;"
```

### Шаг 4. Создайте пользователя ОС и клонируйте репозиторий

```bash
adduser --system --group --home /opt/cloud-storage --shell /bin/bash cloud
sudo -u cloud git clone <URL_РЕПОЗИТОРИЯ> /opt/cloud-storage/repo
shopt -s dotglob && mv /opt/cloud-storage/repo/* /opt/cloud-storage/ && shopt -u dotglob
rmdir /opt/cloud-storage/repo
chmod 755 /opt/cloud-storage
ls /opt/cloud-storage        # должны быть видны каталоги backend и frontend
```

### Шаг 5. Создайте файл `.env`

Готовый production-шаблон лежит в `backend/deploy/.env.production`.
Команды ниже копируют его и подставляют значения:

```bash
cd /opt/cloud-storage/backend
sudo -u cloud cp deploy/.env.production .env
sudo -u cloud sed -i "s|<СЛУЧАЙНАЯ_СТРОКА>|$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')|" .env
sudo -u cloud sed -i "s|<IP_СЕРВЕРА>|$(curl -4 -s ifconfig.me)|" .env
sudo -u cloud nano .env      # впишите APP_DB_PASSWORD=<ПАРОЛЬ_БД>, Ctrl+O, Enter, Ctrl+X
chmod 600 .env
```

В файле не должно остаться ни одного значения в угловых скобках:
`grep '<' .env` должен выводить только строки-комментарии (начинаются с `#`).
Если используется домен — допишите его в `APP_ALLOWED_HOSTS` через запятую.
Там же при желании смените пароль администратора `APP_ADMIN_PASSWORD`
(до выполнения шага 6).

### Шаг 6. Установите зависимости backend и примените миграции

```bash
cd /opt/cloud-storage/backend
sudo -u cloud python3 -m venv venv
sudo -u cloud venv/bin/pip install -r requirements.txt
sudo -u cloud venv/bin/python manage.py migrate
```

`migrate` создаёт таблицы и администратора (`admin` / `Admin123!`, если не меняли в `.env`).

### Шаг 7. Соберите фронтенд

```bash
cd /opt/cloud-storage/frontend
sudo -u cloud npm ci
sudo -u cloud npm run build
sudo -u cloud rm -rf ../backend/frontend_build
sudo -u cloud cp -r dist ../backend/frontend_build
```

### Шаг 8. Соберите статику Django (нужна для `/admin/`)

```bash
cd /opt/cloud-storage/backend
sudo -u cloud venv/bin/python manage.py collectstatic --noinput
sudo -u cloud venv/bin/python manage.py check --deploy 2>&1 | tail -n 3
```

### Шаг 9. Запустите Gunicorn через systemd

Готовый unit-файл: `backend/deploy/cloud-storage.service`.

```bash
cp /opt/cloud-storage/backend/deploy/cloud-storage.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now cloud-storage
systemctl status cloud-storage --no-pager      # должно быть: active (running)
curl -s -o /dev/null -w "%{http_code}\n" -H "Host: localhost" http://127.0.0.1:8000/   # 200
```

### Шаг 10. Настройте Nginx

Готовый конфиг: `backend/deploy/nginx.conf`.

```bash
cp /opt/cloud-storage/backend/deploy/nginx.conf /etc/nginx/sites-available/cloud-storage
ln -sf /etc/nginx/sites-available/cloud-storage /etc/nginx/sites-enabled/cloud-storage
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
ufw allow 80/tcp 2>/dev/null; ufw allow 443/tcp 2>/dev/null; true
```

Приложение доступно по адресу **`http://<IP_СЕРВЕРА>/`**.

### Шаг 11 (необязательно). Домен и HTTPS

Нужен домен, A-запись которого указывает на `<IP_СЕРВЕРА>`.

```bash
sed -i 's/server_name _;/server_name example.ru;/' /etc/nginx/sites-available/cloud-storage
apt install -y certbot python3-certbot-nginx
certbot --nginx -d example.ru
```

Затем в `/opt/cloud-storage/backend/.env` допишите `example.ru` в
`APP_ALLOWED_HOSTS`, раскомментируйте `APP_CSRF_TRUSTED_ORIGINS=https://example.ru`
и `APP_SECURE_COOKIES=1`, после чего `systemctl restart cloud-storage`.

### Проверка после развёртывания

1. `http://<IP_СЕРВЕРА>/` — открывается главная страница.
2. «Регистрация» — создать пользователя, войти.
3. «Хранилище» — загрузить файл, переименовать (Enter), изменить комментарий, скачать.
4. «Спец. ссылка» — открыть скопированную ссылку в режиме инкогнито: файл скачивается без входа.
5. Войти как `admin` — в разделе администратора виден список пользователей, доступны их хранилища.

### Обновление приложения

```bash
cd /opt/cloud-storage && sudo -u cloud git pull
cd backend && sudo -u cloud venv/bin/pip install -r requirements.txt
sudo -u cloud venv/bin/python manage.py migrate
cd ../frontend && sudo -u cloud npm ci && sudo -u cloud npm run build
sudo -u cloud rm -rf ../backend/frontend_build && sudo -u cloud cp -r dist ../backend/frontend_build
cd ../backend && sudo -u cloud venv/bin/python manage.py collectstatic --noinput
systemctl restart cloud-storage
```

### Если что-то не работает

| Симптом | Что проверить |
|---------|---------------|
| 502 Bad Gateway | `systemctl status cloud-storage`, `journalctl -u cloud-storage -n 50` — gunicorn не запущен |
| 400 Bad Request | в `APP_ALLOWED_HOSTS` нет IP/домена, по которому открыт сайт |
| `password authentication failed` в логах | `APP_DB_PASSWORD` в `.env` не совпадает с паролем из шага 3 |
| Открывается «Welcome to nginx» | не удалён `/etc/nginx/sites-enabled/default` (шаг 10) |
| Главная отдаёт 404 | не выполнен шаг 7 (нет `backend/frontend_build/index.html`); после сборки — `systemctl restart cloud-storage` |
| 413 при загрузке файла | `client_max_body_size` в конфиге nginx |
| Сайт не открывается совсем | `ufw status`; файрвол в панели reg.ru — открыт ли порт 80 |

## Логирование

События (регистрация, вход/выход, ошибки, операции с файлами) пишутся
в консоль с уровнями debug/info/warning/error (`config/settings.py -> LOGGING`).
Через systemd/gunicorn — `journalctl -u <имя_сервиса> -f`.

## Команды

```bash
python manage.py createsuperuser
python manage.py migrate
python manage.py collectstatic
python manage.py check
```

## Упрощения

Хранилище одноуровневое, без вложенных папок. Специальная ссылка не
имеет срока действия — отозвать можно только перегенерацией
(`POST /api/files/<id>/link/`).
