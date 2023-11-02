import random


def numeral_noun_declension(number, nominative_singular, genitive_singular, nominative_plural):
    dig_last = number % 10
    return (
            (number in range(5, 20)) and nominative_plural or
            (1 in (number, dig_last)) and nominative_singular or
            ({number, dig_last} & {2, 3, 4}) and genitive_singular or nominative_plural
    )


def declensed_gratz(n: int) -> str:
    return numeral_noun_declension(n, 'грац', 'граца', 'грацей')


def declensed_farm(n: int) -> str:
    return numeral_noun_declension(n, 'ферма', 'фермы', 'ферм')


def declensed_gold(n: int) -> str:
    return numeral_noun_declension(n, 'золото', 'золота', 'золотых')


def items_to_html(items, users) -> str:
    _list = []
    item: dict
    for index, item in enumerate(items):
        place = index + 1
        name = users[item].get("name", "[ДАННЫЕ СКРЫТЫ]")
        gold = users[item].get("gold", 0)
        farm = users[item].get("farm", 1)
        _list.append(f"{place}. <b>{name}</b> - {gold} {declensed_gold(gold)}, {farm} {declensed_farm(farm)}.")
    return "\n".join(_list)


def roll_for_success(success_rate):
    roll_result = random.randint(1, 100)

    if roll_result <= success_rate:
        return True  # Success
    else:
        return False  # Failure
