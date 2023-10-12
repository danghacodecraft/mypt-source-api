import datetime

def birthday_is_today(birthday):
    try:
        today = datetime.datetime.now().date()
        return str(today) == birthday
    except Exception as e:
        print(e)
        return False