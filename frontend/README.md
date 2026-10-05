# Облачное файловое хранилище — Frontend

React SPA-фронтенд для дипломного проекта «Облачное файловое
хранилище». Общие инструкции по развёртыванию **всего** приложения
(backend + frontend) находятся в `../backend/README.md`. Этот файл
описывает только сборку и подготовку артефактов фронтенда.

## Технологии

- React + React Router (SPA, состояние аутентификации реализовано
  через React Context, запросы к API — через обёртку `src/api.js`)
- Сборка — Vite

## Структура

```
frontend/
├── index.html
├── vite.config.js       # dev-прокси /api -> Django (127.0.0.1:8000)
├── src/
│   ├── api.js             # обёртка над fetch + CSRF
│   ├── AuthContext.jsx    # состояние аутентификации (React Context)
│   ├── validators.js      # клиентская валидация формы регистрации
│   ├── styles.css
│   ├── components/
│   │   ├── NavBar.jsx        # навигация (Вход/Выход/Регистрация)
│   │   └── ProtectedRoute.jsx
│   └── pages/
│       ├── Home.jsx
│       ├── Register.jsx
│       ├── Login.jsx
│       ├── Admin.jsx          # список пользователей (только admin)
│       └── Storage.jsx        # управление файлами
└── package.json
```

## Локальная разработка

Требуется Node.js ≥ 20.19 (требование Vite 8).

```bash
npm install
npm run dev
```

Приложение откроется на `http://localhost:5173/`. Запросы к `/api/...`
автоматически проксируются на Django-сервер, который должен быть
запущен на `http://127.0.0.1:8000/` (см. `../backend/README.md`,
раздел «Локальное развёртывание»).

## Сборка для production

```bash
npm run build
```

Результат появится в папке `dist/`. Backend (Django) настроен на
раздачу файлов из папки `backend/frontend_build/`, поэтому после
сборки нужно скопировать туда содержимое `dist/`:

```bash
rm -rf ../backend/frontend_build
cp -r dist ../backend/frontend_build
```

После этого Django-сервер (`python manage.py runserver` или gunicorn
в production) будет отдавать фронтенд с того же порта, что и API —
отдельный веб-сервер для фронтенда не требуется.

> Если backend и frontend опубликованы в раздельных репозиториях —
> именно эти два шага (`npm run build` + копирование `dist/` в
> `frontend_build/` соседнего backend-репозитория) и есть то, что
> нужно проверяющему выполнить перед запуском backend по инструкции
> из `backend/README.md`.

## Переменные окружения

`VITE_API_BASE` — базовый URL API, если фронтенд собирается для
раздачи с отдельного домена/порта от backend (по умолчанию пустой —
запросы идут на тот же origin, что и сам фронтенд, что подходит для
схемы «единый сервер отдаёт всё», описанной в задании).
