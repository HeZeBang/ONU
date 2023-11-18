from ONU_source.template import * # Your ONU File
__version__ = "v1.0.2-beta"

# ---------------------------- Game Settings From UNO source file ----------------------------------

COLORS = [col for col in Color]
'''
Available Color
'''

EFFECTS = [Effect.BAN, Effect.CHANGE_COLOR, Effect.PLUS_TWO]
'''
Available Effect
'''

game = None

# ------------------------- Default Settings ----------------------------------
# Those settings will be applied if arguments didn't give

def get_argparser():
    confparser = argparse.ArgumentParser(description='Initializing ONU game server.')
    argconf = confparser.add_argument_group("Argument config")
    argconf.add_argument("-p", "--player-num", type = int, default = 7, help = "Player numbers (if forced started, "
                         "the remaining slots will be filled with bot)")
    argconf.add_argument("-hd", "--hand-card-num", type = int, default = 14, help = "Initial hand card numbers")
    argconf.add_argument("-s", "--special-card-sets", type = int, default = 2, help = "Number of sets of Special Cards")
    argconf.add_argument("-n", "--numeric-card-sets", type = int, default = 3, help = "Number of sets of Numeric Cards")
    argconf.add_argument("--port", type = int, default = 8082, help = "Recommend port : 8081 ~ 8088")
    argconf.add_argument("-r", "--run-on-server", default = False, action="store_true", help = "If this is set True, the server will "
                                                                                       "not stop running after all players exit.")
    argconf.add_argument("--password", type = str, default = "123456", help = "Server shutting down password")
    return confparser

# ---------------------------- Main Program -----------------------------------
import random
import types
import itertools
import argparse

def allKindofCards() -> List[Card]:
    '''
    Return a card list
    '''
    cardList = ([SpecialCard(attr[0], attr[1]) 
            for attr in list(itertools.product(COLORS,EFFECTS))] * SPECIAL
            + [NumericCard(attr[0], attr[1]) 
        for attr in list(itertools.product(COLORS, list(range(1, 10))))] * NUMERIC)
    random.shuffle(cardList)
    return cardList

chat_msgs = []  # The chat message history. The item is (name, message content)
cur = 0

def card_buttons(valid_cards: List[Card], all_cards: List[Card]):
    '''
    Return a List[Dict] to `put_buttons`
    '''
    lstBtn = [{
                    "label":"PASS",
                    "value":-1,
                    "color":"danger",
                    }]
    for i in all_cards:
        if i in valid_cards:
            if isinstance(i, NumericCard):
                lstBtn.append({
                    "label":repr(i),
                    "value":all_cards.index(i),
                    "color":"primary",
                    })
            else:
                lstBtn.append({
                    "label":repr(i),
                    "value":all_cards.index(i),
                    "color":"warning",
                    })
        else:
            lstBtn.append({
                    "label":repr(i),
                    "value":all_cards.index(i),
                    "color":'secondary',
                    "disabled":True
                    })
    return lstBtn

async def action_re(cards: List[Card], last_card: Card, is_last_player_drop: bool) -> Tuple[ActionType, Card | None]: 
    '''
    This `action` is rewrited.
    '''
    def match(toMatch: Card, other: Card) -> bool:
        if other is None:
            return True
        if isinstance(toMatch, NumericCard):
            return (toMatch.get_color() == other.get_color()
                    or (isinstance(other, NumericCard) and toMatch.get_number() == other.get_number()))
        if isinstance(toMatch, SpecialCard):
            if toMatch.get_effect() == Effect.CHANGE_COLOR:
                return True
            if toMatch.get_effect() == Effect.BAN:
                return (toMatch.get_color() == other.get_color() 
                        or type(other) == SpecialCard and other.get_effect() == toMatch.get_effect())
            if toMatch.get_effect() == Effect.PLUS_TWO:
                return (toMatch.get_color() == other.get_color()
                        or type(other) == SpecialCard and other.get_effect() == toMatch.get_effect())
    valid_cards = [i for i in cards if match(i, last_card)]
    if(is_last_player_drop):
        if(isinstance(last_card, SpecialCard)):
            if last_card.get_effect() == Effect.BAN:
                toast("🚫You were BANNED", color='error')
                await asyncio.sleep(1)
                return ActionType.PASS, None
            if last_card.get_effect() == Effect.PLUS_TWO:
                p2_cards = [i for i in cards if isinstance(i, SpecialCard) and i.get_effect() == Effect.PLUS_TWO]
                if len(p2_cards) == 0:
                    toast("😭Oops, you have NO PLUS_TWO cards!", color='warning')
                    await asyncio.sleep(1)
                    return ActionType.PASS, None
                valid_cards = p2_cards

    if valid_cards:
        toast("Your Turn!", color="success")
        idx = await actions("Your Turn!",card_buttons(valid_cards, cards))
        if idx == -1:
            return ActionType.PASS, None
        return ActionType.DROP, cards[idx]
    
    toast("😭Oops, you have NO valid cards!", color='warning')
    await asyncio.sleep(1)
    return ActionType.DRAW, None

def action_new(self, cards: List[Card], last_card: Card, is_last_player_drop: bool) -> Tuple[ActionType, Card | None]: 
    return local.action

SpecialCard.__json__ = types.MethodType(lambda self: {'value': repr(self)}, SpecialCard)
NumericCard.__json__ = types.MethodType(lambda self: {'value': repr(self)}, NumericCard)

# -----------------------------------------------------------------------------

import asyncio
import sys
import os
try:
    from pywebio import start_server
    from pywebio.input import *
    from pywebio.output import *
    from pywebio.session import defer_call, info as session_info, run_async, local, set_env, run_js
    from pywebio.platform import config
    from pywebio.pin import *
    from pywebio_battery import *
except:
    if(input("检测到没有安装依赖 pywebio / pywebio_battery 输入 y 并按下【回车 / Enter / Return】开始安装") == 'y'):
        os.system(f"{sys.executable} -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pywebio pywebio_battery")
        print('安装完成，请重新运行')
    sys.exit() 

MAX_MESSAGES_CNT = 10 ** 4

online_users = []

def htmlize(who: str, action: Tuple) -> str:
    return f"<code>{who}</code>&emsp;<b>{action[0].name}</b>&emsp;" + (f"{colorful_cards([action[1]])[0]}" if action[1] is not None else "")

async def refresh_msg(my_name):
    """
    send new message to current session
    """
    global chat_msgs
    last_idx = len(chat_msgs)
    while True:
        await asyncio.sleep(0.5)
        global cur, game

        for m in chat_msgs[last_idx:]:
            if m[0] == "🎴":
                put_html('<code>%s</code>: %s' % m, sanitize=True, scope='msg-box')
            elif m[0] == False:
                popup('GAME OVER',
                      [put_markdown(m[1]),
                      put_table([game.get_scores()],
                                [_ if _ != "" else "ROBOT" for _ in online_users] + ["ROBOT" for _ in range(max_player_num - len(online_users))])])
            elif m[0] != my_name:  # only refresh message that not sent by current user
                put_markdown('`%s`: %s' % m, sanitize=True, scope='msg-box')
        
        # update_status(my_name)
        # remove expired message
        if len(chat_msgs) > MAX_MESSAGES_CNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)
    
        notend = True
        cur_id, last_card, is_last_player_drop, plus_two_cnt, hands = game.get_info()

        if(game.is_not_end()):
            update_status(my_name)
            if (cur == online_users.index(my_name) and cur == (cur_id + 1) % max_player_num): # Human
                Player.action_old = Player.action
                Player.action = types.MethodType(action_new, Player)
                local.action = await action_re(hands[cur].get_cards(), last_card, is_last_player_drop)
                action, info, notend = game.turn()
                chat_msgs.append(("🎴", htmlize(f"{my_name}", action)))
                cur = (info[0] + 1) % max_player_num
                Player.action = Player.action_old
                
            elif (len(online_users) > cur and online_users[cur] == "") or (cur >= len(online_users)):
                # Robot played by Player.action() from your ONU_source
                action, info, notend = game.turn()
                chat_msgs.append(("🎴", htmlize(f"🤖{cur + 1}", action)))
                cur = (info[0] + 1) % max_player_num
                await asyncio.sleep(0.5)
            
        update_status(my_name)
        if not notend: # Ended
            userLst = online_users + ["ROBOT" for _ in range(max_player_num - len(online_users))]
            update_status(my_name)
            msg = (f"GAME OVER", f"\n# 🏆Player `{userLst[game.get_winner()]}` WIN!\nThe next game will begin in 10s")
            put_markdown('%s\n%s' % msg, sanitize=True, scope='msg-box')
            chat_msgs.append(msg)
            
            reset_game()
            
            await asyncio.sleep(10)
            
            update_status(my_name)
            

COLORMAPPING = {
    # background, foreground
    Color.RED   : ("#F44336", "#FFFFFF"),
    Color.YELLOW: ("#FFEB3B", "#212121"),
    Color.GREEN : ("#4CAF50", "#FFFFFF"),
    Color.BLUE  : ("#2196F3", "#FFFFFF"),
    Color.CYAN  : ("#00BCD4", "#FFFFFF"),
    Color.ORANGE: ("#FF9800", "#FFFFFF"),
    Color.PURPLE: ("#9C27B0", "#FFFFFF"),
    Color.WHITE : ("#F9F9F9", "#212121"),
    Color.BLACK : ("#1F1F1F", "#FFFFFF"),
    Color.VIOLET: ("#4F2F4F", "#FFFFFF")
}

EFFECTMAPPING = {
    Effect.BAN  : "🚫",
    Effect.CHANGE_COLOR: "🎨",
    Effect.PLUS_TWO: "➕2️⃣"
}

def colorful_cards(cards: List[Card], size: str = "80%"):
    """
    Give the colorfuled card output to a table
    """
    result = []
    for card in cards:
        if isinstance(card, NumericCard):
            result.append(
                (f'<code style="white-space: nowrap; font-size: {size}; background: {COLORMAPPING[card.get_color()][0]}; color: {COLORMAPPING[card.get_color()][1]};">{card.get_color().name} {card.get_number()}</code>'))
            
        elif isinstance(card, SpecialCard):
            result.append(
                (f'<code style="white-space: nowrap; font-size: {size}; background: {COLORMAPPING[card.get_color()][0]}; color: {COLORMAPPING[card.get_color()][1]};">{card.get_color().name} {EFFECTMAPPING[card.get_effect()]}</code>'))
        else:
            pass

    return result

def update_status(my_name):
    """
    Update Player's info and Game's info
    """
    statusNew = (online_users.index(my_name) + 1, sum([i != "" for i in online_users]),
                cur + 1, max_player_num)
    userLst = [_ if _ != "" else "ROBOT" for _ in online_users] + ["ROBOT" for _ in range(max_player_num - len(online_users))]
    scoreNew = [f"{len(game.get_info()[4][i].get_cards())}🎴" for i in range(max_player_num)]
    cardsNew = game.get_info()[4][online_users.index(my_name)].get_cards()
    if(local.status != statusNew):
        for i in range(len(online_users)):
            if online_users[i] == "" and online_users.index(my_name) >= max_player_num:
                online_users.remove(my_name)
                online_users[i] = my_name
                toast(f"⚠You've taken over Player {i + 1}'s cards", color='warning')
                break
        clear("status")
        put_markdown(f"Your name: `{my_name}` - `(#{online_users.index(my_name) + 1})`\n"
                        + "Online: `%d/%d` Player: `%d/%d`" % statusNew, scope="status")
    if(local.score != scoreNew):
        clear("score")
        put_table(list(zip(userLst,
            scoreNew,
            strict=False)),
            ["Player", "Left"],
            scope = "score")
    if(local.cards != cardsNew):
        clear("cards")
        put_html(f'<div style="line-height: 220%">{" ".join(colorful_cards(cardsNew, "120%"))}</div>', scope = "cards")

        
    local.status = statusNew
    local.score = scoreNew
    local.cards = cardsNew

# @config(theme='dark')
async def main():
    """
    🃏ONU! Server Edition
    """
    with redirect_stdout():
        print("Hello.")
    
    run_js(f'document.getElementsByClassName("footer")[0].innerHTML="<b>ONU!</b> is powered by PyWebIO / Special Thanks for <img src="https://contrib.rocks/image?repo=HeZeBang/ONU" style="max-height: 50%;">"')
    
    global chat_msgs, online_users

    put_markdown(f"## WELCOME TO 🃏ONU! <sup>{__version__}</sup>")
    put_collapse("README (Click to hide)", put_markdown(
f"""
[![Static Badge](https://img.shields.io/badge/Github-ONU-black?logo=github&link=https%3A%2F%2Fgithub.com%2FHeZeBang%2FONU)](https://github.com/HeZeBang/ONU) [![Latest](https://img.shields.io/github/v/tag/HeZeBang/ONU?label=Latest%20Version)](https://github.com/HeZeBang/ONU/releases) [![Last Update](https://img.shields.io/github/release-date-pre/HeZeBang/ONU?label=Last%20Update)](https://github.com/HeZeBang/ONU/commits/main)

🎉 Welcome to `ONU!`, a game designed for everyone in the **SI100B** course.

**The core logic of this game stems from your very own `ONU` class!** 
We've taken the initiative to adapt certain modules to ensure seamless gameplay on your web browser. 
We hope that as you dive into the intricacies of debugging, 
you can also experience a profound sense of accomplishment.

Interested in inviting your ShanghaiTech friends to play along?
Simply have them connect to the **WIFI:** 🌐 `ShanghaiTech` and open the following URL:

[http://{session_info.user_ip}:{PORT}](http://{session_info.user_ip}:{PORT})

***References:***
[Chat_Room - PyWebIO Demo](https://github.com/wang0618/PyWebIO/blob/dev/demos/chat_room.py)
"""), open = True)

    put_row([
                put_scrollable(put_scope('msg-box'), height=250, keep_bottom=True), 
                None,
                put_column(
                    [
                        put_scope("status"), 
                        put_scrollable(put_scope("score"), height=192)
                    ], size='20% 1px 80%')
            ],
            size='72% 5px 28%')
    try:
        nickname = await get_cookie('name')
        if(nickname is None or nickname in online_users):
            nickname = await input("What's your name...", required=True,
                validate=lambda n: 'Nickname already exists!' 
                    if n in online_users or n == '📢' else None)
        else:
            toast(f"🎉Welcome back, {nickname}")
        set_cookie("name", nickname, 7)
    except:
        return
    
    for i in range(len(online_users)):
        if(online_users[i] == ""):
            online_users[i] = nickname
    if(nickname not in online_users):
        online_users.append(nickname)
    chat_msgs.append(('📢', '`%s` joins the room. users currently online : `%s`' % (nickname, (", ".join(online_users)))))
    put_markdown('`📢`: `%s` join the room. users currently online : `%s`' % (nickname, (", ".join(online_users))), sanitize=True, scope='msg-box')

    @defer_call
    def on_close():
        index = online_users.index(nickname)
        if(index <  max_player_num):
            online_users[index] = ""
        else:
            online_users.remove(nickname)
        chat_msgs.append(('📢', '`%s` leaves the room. %s users currently online' % (nickname, sum([i != "" for i in online_users]))))
        
        if(all([user == "" for user in online_users])):
            if RUN_ON_SERVER :
                reset_game()
            else :
                sys.exit()

    put_markdown("## 💬 Chat with friends")
    put_input('chatbox')
    put_actions(name = "actbar", label = "", buttons = ['Send', 'Exit Game',{'label': '🛑Shutdown Server','type' : 'submit',
                                                                             'value': 'Shutdown Server', 'color': 'danger'}])
    update_status(nickname)
    put_markdown("## 🎴 Your Cards")
    put_scope("cards")
    local.cards=[]
    update_status(nickname)
    scroll_to("cards")

    refresh_task = run_async(refresh_msg(nickname))

    while True:
        data = await pin_wait_change('actbar')
        if data['value'] == 'Exit Game' :
                break
        elif data['value'] == 'Send':
                msg = await pin['chatbox']
                put_markdown('**`%s`**: %s' % (nickname, msg), sanitize=True, scope='msg-box')
                chat_msgs.append((nickname, msg))
        else :
            passwd = await input("Admin Password Required :")
            global PASSWORD
            if passwd == PASSWORD:
                sys.exit()
            else:
                toast('Invalid Password')

    refresh_task.close()
    toast("ヾ(•ω•`)o See you next time!")
    
def reset_game() :
    global cur, game
    game = Game(allKindofCards(), max_player_num, hand_card_num, 0)
    cur = 0
    
if __name__ == '__main__':
    args = get_argparser().parse_args()
    global max_player_num, hand_card_num, SPECIAL, NUMERIC, PORT, RUN_ON_SERVER
    max_player_num, hand_card_num = args.player_num, args.hand_card_num
    SPECIAL, NUMERIC, PORT, RUN_ON_SERVER = args.special_card_sets, args.numeric_card_sets, args.port, args.run_on_server
    PASSWORD = args.password
    game = Game(allKindofCards(), max_player_num, hand_card_num, 0)
    start_server(main, debug = True, port = PORT)
