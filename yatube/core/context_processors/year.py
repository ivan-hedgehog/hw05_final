import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    dt = datetime.datetime.today()
    return {
        'year': dt.year
    }
