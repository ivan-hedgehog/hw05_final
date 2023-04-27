# hw05_final

Блог для авторов YaTube
YaTube – это полнофункциональный блог, реализованный на фреймворке Django. Он предоставляет пользователям возможность создавать, редактировать и публиковать свои посты с изображениями, просматривать и комментировать посты других авторов, а также ставить лайки. Помимо этого, в YaTube реализован механизм регистрации пользователей и авторизации, который позволяет им создавать свои профили. Реализван функционал подписки на любимых авторов. Написаны юнит-тесты.

Как развернуть проект:
Клонировать репозиторий и перейти в него в командной строке:

git clone git@github.com:ivan-hedgehog/hw05_final.git
cd hw05_final
Cоздать и активировать виртуальное окружение:

python3.7 -m venv venv
source venv/Scripts/activate (venv/bin/activate для МасOS, Linux)
python3 -m pip install --upgrade pip (python далее везде для Windows)
Установить зависимости из requirements.txt:

pip install -r requirements.txt
Выполнить миграции:

python3 manage.py migrate  
Создать администратора:

python3 manage.py createsuperuser
Запустить проект:

python3 manage.py runserver

