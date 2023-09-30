from datetime import datetime

def numeral_noun_declension(number, nominative_singular, genetive_singular, nominative_plural):
    dig_last = number % 10
    return (
        (number in range(5, 20)) and nominative_plural or
        (1 in (number, dig_last)) and nominative_singular or
        ({number, dig_last} & {2, 3, 4}) and genetive_singular or nominative_plural
    )

def declensed_gratz(n: int) -> str:
    return numeral_noun_declension(n, 'грац', 'граца', 'грацей')

def declensed_farm(n: int) -> str:
    return numeral_noun_declension(n, 'ферма', 'фермы', 'ферм')

def items_to_html(items, users) -> str:
    _list = []
    item: dict
    for index, item in enumerate(items):
        place = index + 1
        name = users[item].get("name", "[ДАННЫЕ СКРЫТЫ]")
        amount = users[item].get("amount", 0)
        token = users[item].get("token", 0)
        _list.append(f"{place}. <b>{name}</b> - {amount} {declensed_gratz(amount)}, {token} GZ!")
    return "\n".join(_list)

def calculate_tokens(farms_amount, last_date:datetime, current_date:datetime):
    delta = current_date - last_date
    days = delta.days
    if days <= 0:
        return 0
    return days * farms_amount