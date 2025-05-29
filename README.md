Для корректной работы нужно сделать директорию на латинице и от туда запускать
# for bot
pip install python-telegram-bot openai slither-analyzer solc-select
# for site
pip install django
pip install slither-analyzer
pip install openai
pip install web3
pip install PyJWT
# site map
audit/
├── audit/                  # Главная Django-конфигурация
│   ├── __init__.py
│   ├── settings.py         # Настройки проекта
│   ├── urls.py             # Глобальные маршруты
│   ├── wsgi.py
│   └── asgi.py
│
├── contracts/              # Приложение для анализа контрактов
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # (можно оставить пустым)
│   ├── tests.py
│   ├── forms.py            # Форма для загрузки кода/файла
│   ├── urls.py             # URL-ы приложения
│   ├── views.py            # Основная логика веб-интерфейса
│   └── logic/              # Вспомогательная логика для аудита
│       ├── __init__.py
│       └── analyzer.py     # Класс ERC20AuditTool с Slither и OpenAI
│
├── users/                  # Новое приложение для пользователей
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # Модель пользователя (можно расширить стандартную)
│   ├── tests.py
│   ├── forms.py            # Формы регистрации, входа и пр.
│   ├── urls.py              # URL-ы приложения (profile)
│   ├── middleware.py             # Элемент авторизации через Metamask
│   ├── context_processors.py             # Элемент авторизации через Metamask
│   └── views.py            # Логика работы с пользователями
│   └── utils/               # Вспомогательная логика для авторизации
│       ├── __init__.py
│       └── jwt_handler.py     # Элемент авторизации через Metamask
│       └── web3_auth.py     # Элемент авторизации через Metamask
│
├── media/                  # Загружаемые пользователем файлы
│   └── *.sol               # Контракты (автоматически)
│
├── templates/
│   ├── contracts/
│   │   └── upload.html     # HTML-шаблон загрузки и вывода результата
│   └── users/              # Шаблоны для пользователей
│       └── profile.html
│
├── static/                 # (если будут стили, js и т.п.)
│
├── manage.py
└── requirements.txt        # Список зависимостей
