import datetime

def numeral_noun_declension(number, nominative_singular, genetive_singular, nominative_plural):
    dig_last = number % 10
    return (
            (number in range(5, 20)) and nominative_plural or
            (1 in (number, dig_last)) and nominative_singular or
            ({number, dig_last} & {2, 3, 4}) and genetive_singular or nominative_plural
    )


def declensed_gratz(n: int) -> str:
    return numeral_noun_declension(n, 'грац', 'граца', 'грацей')


def items_to_html(items, users) -> str:
    _list = []
    item: dict
    for index, item in enumerate(items):
        place = index + 1
        name = users[item].get("name", "[ДАННЫЕ СКРЫТЫ]")
        gratz = users[item].get("gratz", 0)
        _list.append(f"{place}. <b>{name}</b> - {gratz} {declensed_gratz(gratz)}.")
    return "\n".join(_list)


def get_today():
    return (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).days
