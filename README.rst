Приложение для работы с базой данных ФИАС в Django

Основные возможности
====================

* Импорт базы ФИАС из скачанного архива XML или напрямую с сайта http://fias.nalog.ru
* Возможность хранить данные в отдельной БД.
* Поле модели AddressField, предоставляющее в админке Django ajax-поиск адреса.
* Несколько абстрактных моделей, немного упрощающих жизнь.

Установка
============

1. Установите `django_fias`::

        pip install django_fias

2. Добавьте `fias` в ваш список `INSTALLED_APPS`.
3. Добавьте `url(r'^django_fias/', include('fias.urls', namespace='fias')),` в ваш urlpatterns
4. Если вы желаете использовать отдельную БД под данные ФИАС, выполните следующее

* Создайте БД
* Добавьте в ваш `settings.py` параметр::

        FIAS_DATABASE_ALIAS = 'fias'

где `fias` - имя БД

* Добавьте в список `DATABASE_ROUTERS`::

        fias.routers.FIASRouter

* Выполните::

        python manage.py syncdb --database=fias

5. Выполните::

        python manage.py syncdb

6. Выполните::

        python manage.py collectstatic

Использование
==============

Вы можете самостоятельно ссылаться на таблицы БД фиас.

Вы так же можете добавить в свои модели поле `fias.fields.address.AddressField`, которое предоставит вам удобный
поиск адреса по базе и прявязку Один-ко-Многим вашей модели к таблице AddrObj базы ФИАС.

Либо вы можете унаследоваться от любой модели из `fias.models.address`, которые добавят несколько дополнительных
полей к вашим моделям и выполнят за вас кое-какую рутину.