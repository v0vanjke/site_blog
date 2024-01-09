# Сайт-блог.



## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/v0vanjke/django_sprint4
```

```
cd django_sprint4
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

# Технологии

Python 3.9, Django 3.2, SQLite3, DjDT.
