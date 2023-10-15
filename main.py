import os

os.environ['PATH'] = 'C:\\Program Files\\swipl\\bin' + os.pathsep + os.environ['PATH']
from pyswip import Prolog, Atom
import re

print(os.environ['PATH'])
prolog = Prolog()
prolog.consult("swish.pl")
# for soln in prolog.query("imperial(X)"):
#     print(soln["X"])
name = "путник"
race = "дружок"
fractions = []
for fraction in prolog.query("fraction(_, X)"):
    fractions.append(fraction["X"])
fractions = list(set(fractions))
races = ["argonian", "altmer", "nord", "imperial", "breton"]

def atoms_to_strings(answer):
    if isinstance(answer, dict):
        result = {}
        for k in answer.keys():
            result[k] = atoms_to_strings(answer[k])
    elif isinstance(answer, list):
        result = [atoms_to_strings(val) for val in answer]
    elif isinstance(answer, Atom):
        result = answer.value
    elif isinstance(answer, int) or isinstance(answer, str):
        result = answer
    else:
        print("Unsupported result from Prolog: " + str(type(answer)) + str(answer))
    return result


def greeting():
    print(
        "*Вы входите в славный город Солитьюд, столицу провинции Скайрим. К вам подходит стражник.* - Добро "
        "пожаловать, "
        "путник. В стране сейчас идёт гражданская война, поэтому я обязан опрашивать всех гостей города. Зачем ты "
        "пришёл в славный Солитьюд?")
    greet_ans = input()
    greet_match = re.search(r"новенький|первый|смотр|регис|сматр", greet_ans)
    if greet_match:
        registration()
    else:
        dialogue(greet_ans)


def dialogue(ans):
    trade_match = re.search(r"куп|достать|найти", ans)
    marriage_match = re.search(r"женить|замуж|венч", ans)
    frac_match = re.search(r"сменить|фрак|альянс|союз|присоед", ans)
    if trade_match:
        if name != "путник":
            trade(ans)
        else:
            print("- Извини, но незарегистрировавшимся путникам мы ничего не продаём.")
    elif marriage_match:
        if name != "путник":
            marriage()
        else:
            print("- Извини, но на незарегистрированном путнике никто не женится.")
    elif frac_match:
        if name != "путник":
            fraction(ans)
        else:
            print("- Как я могу тебе в этом помочь, если даже имени твоего не знаю?")
    else:
        print("- До встречи!")


def fraction(ans):
    print("- Это можно. Сейчас посмотрим, кто тебя может принять под своё крыло...")
    frac_list = []
    for frac in fractions:
        leader = list(prolog.query("leader(X, " + frac + ")"))
        q = list(prolog.query("are_hatred(" + leader[0]["X"] + ", " + name + ")"))
        if not q:
            gold = 0
            print(frac + " может принять тебя к себе. Список членов фракции: ")
            q2_list = list(prolog.query("fraction(X, " + frac + ")"))
            for q2 in q2_list:
                print(q2["X"])
                q3 = list(prolog.query("septims(" + q2["X"] + ", Y)"))[0]
                gold = gold + q3["Y"]
            print("Их общий бюджет: " + str(gold))
            frac_list.append([frac, gold])
    if len(frac_list) == 0:
        print("- Извини, " + name + ", сейчас в тебе фракции не заинтересованы. Еще вопросы?")
        dialogue(input())
    frac_list.sort(key=lambda x: x[1])
    frac_list.reverse()
    print("- Ну что, к кому из тех, кого я перечислил, будешь пробовать вступать? Я бы порекомендовал " + frac_list[0][0] + ". Они самые богатые в этом списке.")
    fract = ""
    ans = input()
    if re.search(r"импер|домин", ans):
        fract = "imperial"
    elif re.search(r"бард|певец|поэт", ans):
        fract = "bards"
    elif re.search(r"вор|банд", ans):
        fract = "thiefs"
    frac_q = list(prolog.query("new_allies(" + name + ", " + fract + ", Z)"))[0]
    if frac_q["Z"] == 0:
        print("- Ты извини, но они от тебя отказались. Нужно ещё что-нибудь?")
        dialogue(input())
    elif frac_q["Z"] == 1:
        print("- Что ж, ты покинул свою старую фракцию, и теперь являешься членом новой. Я могу чем-то ещё помочь?")
        dialogue(input())
    else:
        print("- Поздравляю, теперь ты член фракции! Остались вопросы?")
        dialogue(input())



def marriage():
    print("- Ого! Это интересно! Я знаю несколько свободных кандидатов... Но все в этом городе очень требовательны. "
          "Что тебя больше всего интересует в человеке?")
    choice = input()
    race_flag = False
    gold_flag = True
    if re.search(r"внеш|крас|лицо", choice):
        race_flag = True
        gold_flag = False
    else:
        gold_flag = True
    print("- Я понял и не осуждаю. Итак, наши кандидаты:")
    marriage_list = []
    candidates_atom = list(prolog.query("marriage(" + name + ", Y)"))[0]
    if candidates_atom["Y"] == 0:
        print("- Ой. Кажется свободные жители города или слишком богаты, или слишком бедны для тебя. Что нибудь ещё нужно?")
        dialogue(input())
    candidates = atoms_to_strings(candidates_atom["Y"])
    for candidate in candidates:
        can_race = ""
        can_frac = "в объединениях не состоит"
        can_gold = 0
        for temp in races:
            q = list(prolog.query(temp + "(" + candidate + ")"))
            if q:
                can_race = temp
                break
        can_frac_pl = list(prolog.query("fraction(" + candidate + ", X)"))
        if len(can_frac_pl) != 0:
            can_frac_pl = list(prolog.query("fraction(" + candidate + ", X)"))[0]
        if can_frac_pl:
            can_frac = can_frac_pl["X"]
        can_gold_pl = list(prolog.query("septims(" + candidate + ", X)"))[0]
        can_gold = can_gold_pl["X"]
        print(candidate + " - " + can_race + ", " + can_frac + ", " + "обладает приданым в " + str(can_gold) + " септимов.")
        can_race_id = 0
        for id in races:
            can_race_id = can_race_id + 1
            if can_race == id:
                break
        marriage_list.append([candidate, can_race, can_frac, can_gold, can_race_id])
    if gold_flag:
        marriage_list.sort(key=lambda x: x[3], reverse=True)
        print("- Я бы пригляделся к этой личности - " + marriage_list[0][0] + ". Это твой лучший вариант.")
    elif race_flag:
        marriage_list.sort(key=lambda x: x[4], reverse=True)
        desc = [[1, "Аргонианцы... м-м-м... не считаются особенно красивыми... но привыкнуть можно."],
                [2, "Высшие эльфы выглядят довольно странно. Но некоторым нравятся."],
                [3, "Норды не сильно ценят красоту, поэтому редко за собой ухаживают."],
                [4, "Гламурные имперцы с их тонной макияжа, да... Многим это нравится."],
                [5, "Бретонцы, на мой взгляд, самые приглядные обитатели этих земель."]]
        print("- Вот что я думаю, твой выбор -- это " + marriage_list[0][0] + ". " + desc[marriage_list[0][4]-1][1] + " Так или иначе, это твой лучший выбор.")
    print("- Итак, есть ко мне ещё вопросы?")
    dialogue(input())

def trade(ans):
    herbs_match = re.search(r"трав|ингридиент", ans)
    potions_match = re.search(r"зел|яд|отрав|напит|эссенц", ans)
    song_match = re.search(r"тамада|песн|стих|бард", ans)
    house_match = re.search(r"дом|поместье|селить|недвиж", ans)
    info_match = re.search(r"слух|говор|инфо|расска", ans)
    stolen_match = re.search(r"крад|вор|вещ", ans)
    if not herbs_match and not potions_match and not song_match and not house_match and not info_match and not stolen_match:
        print("- Что ты хочешь купить, я не расслышал?")
        trade(input())
    else:
        if herbs_match:
            print("- А, нужны ингридиенты для готовки или зельеварения? Посмотрим, к кому тебе лучше обратится...")
            trade_helper("herbs")
        elif potions_match:
            print("- Хочешь купить уже готовые зелья? Я тоже не люблю сам их варить. Хм, посмотрим...")
            trade_helper("potions")
        elif song_match:
            print("- О, я знаю! Это тебе к бардам! Как начнут, невозможно оторваться! Давай посмотрим...")
            trade_helper("song")
        elif house_match:
            print("- Ну, это большое дело. У нас тут дома не из дешёвых так-то. Но я подскажу...")
            trade_helper("house")
        elif info_match:
            print("- Есть тут личности, распространяющие всякие там слухи и прочее. Я бы не доверял им на твоём "
                  "месте, но подсказать смогу...")
            trade_helper("information")
        elif stolen_match:
            print("- *шёпотом* Есть тут кое-кто, кто сможет тебе помочь...")
            trade_helper("stolen")


def trade_helper(prod):
    b_traders = []
    offers = []
    costs = []
    poor_flag = False
    race_flag = False
    for b_trader in prolog.query("trade_offer(X, " + prod + ", _)"):
        b_traders.append(b_trader["X"])
    for trader in b_traders:
        offer = list(prolog.query("can_purchase(" + name + ", " + trader + ", Z)"))[0]
        temp = []
        if re.search(r"discont", offer["Z"]):
            offers.append(trader)
            temp.append(trader)
            t_ans = list(prolog.query("trade_offer(" + temp[0] + ", " + prod + ", X)"))[0]
            temp.append(str(t_ans["X"] / 2))
            costs.append(temp)
        elif re.search(r"race", offer["Z"]):
            race_flag = True
        elif re.search(r"cannot", offer["Z"]):
            poor_flag = True
        else:
            temp.append(trader)
            t_ans = list(prolog.query("trade_offer(" + temp[0] + ", " + prod + ", X)"))[0]
            temp.append(str(t_ans["X"]))
            costs.append(temp)
    if len(offers) == 0 and race_flag is True:
        print("- Боюсь, " + race + ", твоей расе ничего в нашем прекрасном городе не продадут. Можешь "
                                   "проклинать за это своего бога. Что-то ещё нужно?")
        dialogue(input())
    elif len(offers) == 0 and poor_flag is True:
        print("- " + name + ", брат, у тебя денег не хватит на это добро. У нас тут в тридорога дерут. "
                            "Что-то ещё нужно?")
        dialogue(input())
    else:
        costs.sort(key=lambda x: x[1])
        print("- Я бы порекомендовал обратится к " + costs[0][0] + ". Там купишь всего за " + costs[0][1])
        print("- Ещё какие нибудь вопросы?")
        dialogue(input())


def registration():
    global name
    global race
    global fractions
    print("- Вот как? Я должен тебя зарегистрировать. Держи входную грамоту. Впиши сюда своё имя, расу и пол. Если "
          "состоишь в каком-либо союзе, тоже пиши. И было бы здорово, если укажешь честно сколько у тебя золота в "
          "кармане.")
    print("*Введите через запятую имя, расу, пол, фракцию и бюджет*")
    reg_input = input()
    # prolog.query("add_human(" + reg_input + ")")
    # prolog.assertz("nord(" + name + ")")
    reg_input = reg_input.split(", ")
    print(reg_input)
    name = reg_input[0]

    if reg_input[1] == "imperial":
        prolog.assertz("imperial(" + name + ")")
        race = "имперец"
    elif reg_input[1] == "nord":
        prolog.assertz("nord(" + name + ")")
        race = "норд"
    elif reg_input[1] == "breton":
        prolog.assertz("breton(" + name + ")")
        race = "бретонец"
    elif reg_input[1] == "altmer":
        prolog.assertz("altmer(" + name + ")")
        race = "высший эльф"
    else:
        prolog.assertz("argonian(" + name + ")")
        race = "аргонианин"

    if reg_input[2] == "man":
        prolog.assertz("man(" + name + ")")
    else:
        prolog.assertz("woman(" + name + ")")

    for fraction in fractions:
        if fraction == reg_input[3]:
            prolog.assertz("fraction(" + name + ", " + reg_input[3] + ")")

    prolog.assertz("septims(" + name + ", " + reg_input[4] + ")")

    print("Так, " + name + "-" + race + ", верно? Теперь ты гость города Солитьюда. Если что-то нужно, спрашивай.")
    ans = input()
    dialogue(ans)





greeting()

