from crapssim.bet import PassLine, Odds, Come
from crapssim.bet import DontPass, LayOdds
from crapssim.bet import Place, Place4, Place5, Place6, Place8, Place9, Place10
from crapssim.bet import PlaceWorking, Place6Working, Place8Working
from crapssim.bet import Hop32, Hop41, Hop61, Hop52, Hop43
from crapssim.bet import Lay4, Lay6, Lay8, Lay10
from crapssim.bet import Hard10, Hard8, Hard6, Hard4
from crapssim.bet import Field
from crapssim.bet import Bet
import math

"""
Various betting strategies that are based on conditions of the CrapsTable.
Each strategy must take a table and a player_object, and implicitly 
uses the methods from the player object.
"""

"""
Fundamental Strategies
"""

def passline(player, table, unit=5, strat_info=None):
    # Pass line bet
    if table.point == "Off" and not player.has_bet("PassLine"):
        player.bet(PassLine(unit))


def passline_odds(player, table, unit=5, strat_info=None, mult=1):
    unit = player.unit
    passline(player, table, unit)
    # Pass line odds
    if mult == "345":
        if table.point == "On":
            if table.point.number in [4, 10]:
                mult = 3
            elif table.point.number in [5, 9]:
                mult = 4
            elif table.point.number in [6, 8]:
                mult = 5
    else:
        mult = float(mult)

    if (
        table.point == "On"
        and player.has_bet("PassLine")
        and not player.has_bet("Odds")
    ):
        player.bet(Odds(mult * unit, player.get_bet("PassLine")))

def dontpass_odds100(player, table, unit=5, strat_info=None):
    dontpass_odds(player, table, unit, mult=100)

def dontpass_odds(player, table, unit=5, strat_info=None, mult=1):
    dontpass(player, table, unit)
    # Pass line odds
    if table.point == "On":
        if table.point.number in [4, 10]:
            mult = 5 if mult == '345' else mult
            divisible_by = 2 # Payout is 1:2, so the bet amount must be divisible by 2
        elif table.point.number in [5, 9]:
            mult = 4 if mult == '345' else mult
            divisible_by = 3 # Payout is 2:3, so the bet amount must be divisible by 3
        elif table.point.number in [6, 8]:
            mult = 3 if mult == '345' else mult
            divisible_by = 6 # Payout is 5:6, so the bet amount must be divisible by 6
        # Get the nearest bet amount that is divisible by the payout
        bet_amount = math.floor(mult*unit / divisible_by) * divisible_by    

    if (
        table.point == "On"
        and player.has_bet("DontPass")
        and not player.has_bet("LayOdds")
    ):
        player.bet(LayOdds(bet_amount, player.get_bet("DontPass")))
    if table.point == "Off":
        for bet in player.bets_on_table:
            if isinstance(bet, LayOdds):
                player.remove(bet)

def dontpass_odds2(player, table, unit=5, strat_info=None):
    dontpass_odds(player, table, unit, strat_info=None, mult=2)

def dontpass_odds345(player, table, unit=5, strat_info=None):
    dontpass_odds(player, table, unit, strat_info=None, mult='345')

def passline_odds2(player, table, unit=5, strat_info=None):
    passline_odds(player, table, unit, strat_info=None, mult=2)

def passline_odds345(player, table, unit=5, strat_info=None):
    passline_odds(player, table, unit, strat_info=None, mult="345")


def pass2come(player, table, unit=5, strat_info=None):
    passline(player, table, unit)

    # Come bet (2)
    if table.point == "On" and player.num_bet("Come") < 2:
        player.bet(Come(unit))

def dontpass_come_on_third_roll(player, table, unit=5, strat_info=None):
    unit = player.unit
    dontpass(player, table, unit)
    # Come bet (after 2 rolls)
    if table.point == "On" and table.point_rolls >= 2 and player.num_bet("Come") == 0:
        player.bet(Come(unit))
    # stop if we've hit our bank limit
    if player.bankroll + player.total_bet_amount > player.win_limit:
        for bet in player.bets_on_table:
            player.remove(bet)

def pass_and_dontpass_stack_dont_odds(player, table, unit=5, strat_info=None):
    unit = player.unit
    passline(player, table, unit*2)
    dontpass_odds(player, table, unit, strat_info=None, mult='345')
    if player.bankroll + player.total_bet_amount > player.win_limit:
        for bet in player.bets_on_table:
            player.remove(bet)

def pass_and_dontpass_stack_dont_odds_plus_cross(player, table, mult=3, unit=5, strat_info=None):
    field_unit = player.unit

    pass_unit_mapping = {
        5: 25,
        10: 25,
        15: 30,
        25: 50
    }

    pass_unit = pass_unit_mapping[player.unit]
    if player.bankroll + player.total_bet_amount > player.win_limit:
        for bet in player.bets_on_table:
            player.remove(bet)
        return None
    passline(player, table, pass_unit)
    dontpass_odds(player, table, pass_unit, strat_info=None, mult=mult)
    place(player, table, field_unit + 5, strat_info={"numbers": {5, 6, 8}})
    field(player, table, field_unit, strat_info=None)
    # Swap the place bets for odds because they pay more with less of a bet
    if table.point_rolls > 3:
        for bet in list(player.bets_on_table):
            if bet.name not in ["PassLine", "DontPass", "LayOdds"]:
                player.remove(bet)
    if table.point == "On" and table.point.number in [5, 6, 8]:
        if (not player.has_bet(f"Odds")) and (player.has_bet("PassLine")):
            player.bet(Odds(field_unit + 5, player.get_bet("PassLine")))
        player.remove_if_present(f"Place{table.point.number}")


def place(player, table, unit=5, strat_info={"numbers": {6, 8}}, skip_point=True):
    strat_info["numbers"] = set(strat_info["numbers"]).intersection({4, 5, 6, 8, 9, 10})
    if skip_point:
        strat_info["numbers"] -= {table.point.number}

    # Place the provided numbers when point is ON
    if table.point == "On":
        if not player.has_bet("Place4") and 4 in strat_info["numbers"]:
            player.bet(Place4(unit))
        if not player.has_bet("Place5") and 5 in strat_info["numbers"]:
            player.bet(Place5(unit))
        if not player.has_bet("Place6") and 6 in strat_info["numbers"]:
            player.bet(Place6(6 / 5 * unit))
        if not player.has_bet("Place8") and 8 in strat_info["numbers"]:
            player.bet(Place8(6 / 5 * unit))
        if not player.has_bet("Place9") and 9 in strat_info["numbers"]:
            player.bet(Place9(unit))
        if not player.has_bet("Place10") and 10 in strat_info["numbers"]:
            player.bet(Place10(unit))

    # Move the bets off the point number if it shows up later
    if skip_point and table.point == "On":
        if player.has_bet("Place4") and table.point.number == 4:
            player.remove(player.get_bet("Place4"))
        if player.has_bet("Place5") and table.point.number == 5:
            player.remove(player.get_bet("Place5"))
        if player.has_bet("Place6") and table.point.number == 6:
            player.remove(player.get_bet("Place6"))
        if player.has_bet("Place8") and table.point.number == 8:
            player.remove(player.get_bet("Place8"))
        if player.has_bet("Place9") and table.point.number == 9:
            player.remove(player.get_bet("Place9"))
        if player.has_bet("Place10") and table.point.number == 10:
            player.remove(player.get_bet("Place10"))


def place68(player, table, unit=5, strat_info=None):
    passline(player, table, unit, strat_info=None)
    # Place 6 and 8 when point is ON
    p_has_place_bets = player.has_bet(
        "Place4", "Place5", "Place6", "Place8", "Place9", "Place10"
    )
    if table.point == "On" and not p_has_place_bets:
        if table.point.number == 6:
            player.bet(Place8(6 / 5 * unit))
        elif table.point.number == 8:
            player.bet(Place6(6 / 5 * unit))
        else:
            player.bet(Place8(6 / 5 * unit))
            player.bet(Place6(6 / 5 * unit))

def place68_after_7(player, table, unit=5, strat_info=None):
    if strat_info == None:
        strat_info = {"progression": 0, 'Place6Working': False, 'Place8Working': False, 'num_consecutive_sevens': 0}

    place68_unit = 6/5 * unit
    bet_progressions = [place68_unit, place68_unit*3, place68_unit*8]

    # We've hit our bank limit or are past our topmost progression, pull down bets and stop playing
    if player.bankroll + player.total_bet_amount > player.win_limit or strat_info['num_consecutive_sevens'] == 4:
        for bet_nm in ["Place6Working", "Place8Working"]:
            player.remove_if_present(bet_nm)
    # the last roll was a 7
    elif table.last_roll == 7:
        strat_info['num_consecutive_sevens'] += 1
        # If the player had bets and lost
        if strat_info['Place6Working'] or strat_info['Place8Working']:
            strat_info['progression'] += 1
            player.remove_if_present("Place6Working")
            player.remove_if_present("Place8Working")
            
        # otherwise, the progression will stay at what it currently is
        # set bet amount to the current progression index
        try:
            bet_amount = bet_progressions[strat_info['progression']]
            player.bet(Place6Working(bet_amount))
            player.bet(Place8Working(bet_amount))
            strat_info['Place6Working'] = True
            strat_info['Place8Working'] = True
        except:
            pass
    elif table.last_roll in [bet.winning_numbers for bet in player.bets_on_table]:
        for bet_nm in ["Place6Working", "Place8Working"]:
            player.remove_if_present(bet_nm)
        strat_info = None # we hit our number, reset the progression!
    return strat_info

def place6_after_7(player, table, unit=5, strat_info=None):
    if strat_info == None:
        strat_info = {"progression": 0, 'Place6Working': False, 'num_consecutive_sevens': 0}
    place68_unit = 6/5 * unit
    bet_progressions = [place68_unit, place68_unit*2, place68_unit*4, place68_unit*8, place68_unit*16]

    # We've hit our bank limit or are past our topmost progression, pull down bets and stop playing
    if player.bankroll + player.total_bet_amount > player.win_limit or strat_info['num_consecutive_sevens'] == 6:
        for bet_nm in ["Place6Working"]:
            player.remove_if_present(bet_nm)
    # the last roll was a 7
    elif table.last_roll == 7:
        strat_info['num_consecutive_sevens'] += 1
        # If the player had bets and lost
        if strat_info['Place6Working']:
            strat_info['progression'] += 1
            player.remove_if_present("Place6Working")
            
        # otherwise, the progression will stay at what it currently is
        # set bet amount to the current progression index
        try:
            bet_amount = bet_progressions[strat_info['progression']]
            player.bet(Place6Working(bet_amount))
            strat_info['Place6Working'] = True
        except:
            pass
    elif table.last_roll == 6:
        for bet_nm in ["Place6Working"]:
            player.remove_if_present(bet_nm)
        strat_info = None # we hit our number, reset the progression!
    return strat_info

def dontpass(player, table, unit=5, strat_info=None):
    # Don't pass bet
    if table.point == "Off" and not player.has_bet("DontPass"):
        player.bet(DontPass(unit))

def dontpass_progressive_banklimit(player, table, unit=5, strat_info=None):
    if strat_info == None:
        strat_info = {"progression": 0, 'num_consecutive_losses': 0}

    def progression_generator(unit, iterations):
        a = unit
        # Start with the original unit
        results = [unit]
        # iterations minus 1 because we start with orig unit
        for i in range(1, iterations):
            a = a * 2
            results.append(a)
        return results


    try:
        bet_progressions
    except:
        bet_progressions = progression_generator(unit, 5)
    if table.point == "Off" and not player.has_bet("DontPass"):
        # Need to see if the we won or lost the last DontPass
        # We might not have a bet at this point, which is why the try/except exists
        try:
            if table.bet_update_info[player]['DontPass']['status'] == 'lose':
                strat_info['progression'] += 1
                strat_info['num_consecutive_losses'] += 1
            else:
                strat_info['progression'] = 0
                strat_info['num_consecutive_losses'] = 0
        except:
            pass
        # we've reached the end of our progression limit or we've hit our bank limit
        if strat_info['progression'] >= len(bet_progressions) or player.bankroll + player.total_bet_amount >= player.win_limit:
            pass
        else:
            # Place the bet using the current progression step
            player.bet(DontPass(bet_progressions[strat_info['progression']]))
   
    return strat_info

def dontpass_progressive(player, table, unit=5, strat_info=None):
    if strat_info == None:
        strat_info = {"progression": 0, 'num_consecutive_losses': 0}

    def progression_generator(unit, iterations):
        a = unit
        # Start with the original unit
        results = [unit]
        # iterations minus 1 because we start with orig unit
        for i in range(1, iterations):
            a = a * 2
            results.append(a)
        return results


    try:
        bet_progressions
    except:
        bet_progressions = progression_generator(unit, 5)
    if table.point == "Off" and not player.has_bet("DontPass"):
        # Need to see if the we won or lost the last DontPass
        # We might not have a bet at this point, which is why the try/except exists
        try:
            if table.bet_update_info[player]['DontPass']['status'] == 'lose':
                strat_info['progression'] += 1
                strat_info['num_consecutive_losses'] += 1
            else:
                strat_info['progression'] = 0
                strat_info['num_consecutive_losses'] = 0
        except:
            pass
        # we've reached the end of our progression limit or we've hit our bank limit
        if strat_info['progression'] >= len(bet_progressions):
            pass
        else:
            # Place the bet using the current progression step
            player.bet(DontPass(bet_progressions[strat_info['progression']]))
   
    return strat_info


def layodds(player, table, unit=5, strat_info=None, win_mult=1):
    # Assume that someone tries to win the `win_mult` times the unit on each bet, which corresponds
    # well to the max_odds on a table.
    # For `win_mult` = "345", this assumes max of 3-4-5x odds
    unit = player.unit
    dontpass(player, table, unit)

    # Lay odds for don't pass
    if win_mult == "345":
        mult = 6.0
    else:
        win_mult = float(win_mult)
        if table.point == "On":
            if table.point.number in [4, 10]:
                mult = 2 * win_mult
            elif table.point.number in [5, 9]:
                mult = 3 / 2 * win_mult
            elif table.point.number in [6, 8]:
                mult = 6 / 5 * win_mult

    if (
        table.point == "On"
        and player.has_bet("DontPass")
        and not player.has_bet("LayOdds")
    ):
        player.bet(LayOdds(mult * unit, player.get_bet("DontPass")))


def lay4(player, table, unit=5, strat_info=None, win_mult=1):
    unit = player.unit

    if not player.has_bet("Lay4"):
        player.bet(Lay4(unit))


def lay68_comeout(player, table, unit=5, strat_info=None, win_mult=1):
    unit = player.unit

    if table.point == "Off":
        if not player.has_bet('Lay6'):
            player.bet(Lay6(unit))
        if not player.has_bet('Lay8'):
            player.bet(Lay8(unit))
    else:
        if player.has_bet('Lay6'):
            player.remove(player.get_bet('Lay6'))
        if player.has_bet('Lay8'):
            player.remove(player.get_bet('Lay8'))

def lay410_comeout(player, table, unit=5, strat_info=None, win_mult=1):
    unit = player.unit

    if table.point == "Off":
        if not player.has_bet('Lay4'):
            player.bet(Lay4(unit))
        if not player.has_bet('Lay10'):
            player.bet(Lay10(unit))
    else:
        if player.has_bet('Lay4'):
            player.remove(player.get_bet('Lay4'))
        if player.has_bet('Lay10'):
            player.remove(player.get_bet('Lay10'))

"""
Detailed Strategies
"""


def place68_2come(player, table, unit=5, strat_info=None):
    """
    Once point is established, place 6 and 8, with 2 additional come bets.
    The goal is to be on four distinct numbers, moving place bets if necessary
    """
    current_numbers = []
    for bet in player.bets_on_table:
        current_numbers += bet.winning_numbers
    current_numbers = list(set(current_numbers))

    if table.point == "On" and len(player.bets_on_table) < 4:
        # always place 6 and 8 when they aren't come bets or place bets already
        if 6 not in current_numbers:
            player.bet(Place6(6 / 5 * unit))
        if 8 not in current_numbers:
            player.bet(Place8(6 / 5 * unit))

    # add come of passline bets to get on 4 numbers
    if player.num_bet("Come", "PassLine") < 2 and len(player.bets_on_table) < 4:
        if table.point == "On":
            player.bet(Come(unit))
        if table.point == "Off" and (
            player.has_bet("Place6") or player.has_bet("Place8")
        ):
            player.bet(PassLine(unit))

    # if come bet or passline goes to 6 or 8, move place bets to 5 or 9
    pass_come_winning_numbers = []
    if player.has_bet("PassLine"):
        pass_come_winning_numbers += player.get_bet("PassLine").winning_numbers
    if player.has_bet("Come"):
        pass_come_winning_numbers += player.get_bet("Come", "Any").winning_numbers

    if 6 in pass_come_winning_numbers:
        if player.has_bet("Place6"):
            player.remove(player.get_bet("Place6"))
        if 5 not in current_numbers:
            player.bet(Place5(unit))
        elif 9 not in current_numbers:
            player.bet(Place9(unit))
    elif 8 in pass_come_winning_numbers:
        if player.has_bet("Place8"):
            player.remove(player.get_bet("Place8"))
        if 5 not in current_numbers:
            player.bet(Place5(unit))
        elif 9 not in current_numbers:
            player.bet(Place9(unit))

def field(player, table, unit=5, strat_info=None):
    if table.point == "On" and not player.has_bet("Field"):
        player.bet(
            Field(
                unit,
                double=table.payouts["fielddouble"],
                triple=table.payouts["fieldtriple"],
            )
        )


def ironcross(player, table, unit=5, strat_info=None):
    passline(player, table, unit)
    passline_odds(player, table, unit, strat_info=None, mult=2)
    place(player, table, 2 * unit, strat_info={"numbers": {5, 6, 8}})

    if table.point == "On":
        if not player.has_bet("Field"):
            player.bet(
                Field(
                    unit,
                    double=table.payouts["fielddouble"],
                    triple=table.payouts["fieldtriple"],
                )
            )


def ironcross_banklimit(player, table, unit=5, strat_info=None):
    bet_nms = ['PassLine', 'Odds', 'Place5', 'Place6', 'Place8', 'Field']
    if table.point == 'Off' and player.bankroll + player.total_bet_amount > player.win_limit:
        for bet_nm in bet_nms:
            player.remove_if_present(bet_nm)
        pass
    elif table.point == 'On' and player.bankroll + player.total_bet_amount > player.win_limit:
        bet_nms_place_field = ['Place5', 'Place6', 'Place8', 'Field']
        for bet_nm in bet_nms_place_field:
            player.remove_if_present(bet_nm)
        pass
    else:
        passline(player, table, unit)
        passline_odds(player, table, unit, strat_info=None, mult=2)
        place(player, table, 2 * unit, strat_info={"numbers": {5, 6, 8}})

        if table.point == "On":
            if not player.has_bet("Field"):
                player.bet(
                    Field(
                        unit,
                        double=table.payouts["fielddouble"],
                        triple=table.payouts["fieldtriple"],
                    )
                )


def hammerlock(player, table, unit=5, strat_info=None):
    passline(player, table, unit)
    layodds(player, table, unit, win_mult="345")

    place_nums = set()
    for bet in player.bets_on_table:
        if isinstance(bet, Place):
            place_nums.add(bet.winning_numbers[0])
    place_point_nums = place_nums.copy()
    place_point_nums.add(table.point.number)

    has_place68 = (6 in place_nums) or (8 in place_nums)
    has_place5689 = (
        (5 in place_nums) or (6 in place_nums) or (8 in place_nums) or (9 in place_nums)
    )

    # 3 phases, place68, place_inside, takedown
    if strat_info is None or table.point == "Off":
        strat_info = {"mode": "place68"}
        for bet_nm in ["Place5", "Place6", "Place8", "Place9"]:
            player.remove_if_present(bet_nm)

    if strat_info["mode"] == "place68":
        if table.point == "On" and has_place68 and place_nums != {6, 8}:
            # assume that a place 6/8 has won
            if player.has_bet("Place6"):
                player.remove(player.get_bet("Place6"))
            if player.has_bet("Place8"):
                player.remove(player.get_bet("Place8"))
            strat_info["mode"] = "place_inside"
            place(
                player,
                table,
                unit,
                strat_info={"numbers": {5, 6, 8, 9}},
                skip_point=False,
            )
        else:
            place(
                player,
                table,
                2 * unit,
                strat_info={"numbers": {6, 8}},
                skip_point=False,
            )
    elif strat_info["mode"] == "place_inside":
        if table.point == "On" and has_place5689 and place_nums != {5, 6, 8, 9}:
            # assume that a place 5/6/8/9 has won
            for bet_nm in ["Place5", "Place6", "Place8", "Place9"]:
                player.remove_if_present(bet_nm)
            strat_info["mode"] = "takedown"
        else:
            place(
                player,
                table,
                unit,
                strat_info={"numbers": {5, 6, 8, 9}},
                skip_point=False,
            )
    elif strat_info["mode"] == "takedown" and table.point == "Off":
        strat_info = None

    return strat_info


def risk12(player, table, unit=5, strat_info=None):
    passline(player, table, unit)

    if table.pass_rolls == 0:
        strat_info = {"winnings": 0}
    elif table.point == "Off":
        if table.last_roll in table.payouts["fielddouble"]:
            # win double from the field, lose pass line, for a net of 1 unit win
            strat_info["winnings"] += unit
        elif table.last_roll in table.payouts["fieldtriple"]:
            # win triple from the field, lose pass line, for a net of 2 unit win
            strat_info["winnings"] += 2 * unit
        elif table.last_roll == 11:
            # win the field and pass line, for a net of 2 units win
            strat_info["winnings"] += 2 * unit

    if table.point == "Off":
        player.bet(
            Field(
                unit,
                double=table.payouts["fielddouble"],
                triple=table.payouts["fieldtriple"],
            )
        )
        if table.last_roll == 7:
            for bet_nm in ["Place6", "Place8"]:
                player.remove_if_present(bet_nm)
    elif table.point.number in [4, 9, 10]:
        place(player, table, unit, strat_info={"numbers": {6, 8}})
    elif table.point.number in [5, 6, 8]:
        # lost field bet, so can't automatically cover the 6/8 bets.  Need to rely on potential early winnings
        if strat_info["winnings"] >= 2 * unit:
            place(player, table, unit, strat_info={"numbers": {6, 8}})
        elif strat_info["winnings"] >= 1 * unit:
            if table.point.number != 6:
                place(player, table, unit, strat_info={"numbers": {6}})
            else:
                place(player, table, unit, strat_info={"numbers": {8}})

    return strat_info


def knockout(player, table, unit=5, strat_info=None):
    passline_odds345(player, table, unit)
    dontpass(player, table, unit)


def dicedoctor(player, table, unit=5, strat_info=None):
    if strat_info is None or table.last_roll in Field(0).losing_numbers:
        strat_info = {"progression": 0}
    else:
        strat_info["progression"] += 1

    bet_progression = [10, 20, 15, 30, 25, 50, 35, 70, 50, 100, 75, 150]
    prog = strat_info["progression"]
    if prog < len(bet_progression):
        amount = bet_progression[prog] * unit / 5
    elif prog % 2 == 0:
        # alternate between second to last and last
        amount = bet_progression[len(bet_progression) - 2] * unit / 5
    else:
        amount = bet_progression[len(bet_progression) - 1] * unit / 5

    player.bet(
        Field(
            amount,
            double=table.payouts["fielddouble"],
            triple=table.payouts["fieldtriple"],
        )
    )

    return strat_info


def place68_cpr(player, table, unit=5, strat_info=None):
    """ place 6 & 8 after point is establish.  Then collect, press, and regress (in that order) on each win """
    ## NOTE: NOT WORKING
    if strat_info is None:
        strat_info = {"mode6": "collect", "mode8": "collect"}

    if table.point == "On":
        # always place 6 and 8 when they aren't place bets already
        if not player.has_bet("Place6"):
            player.bet(Place6(6 / 5 * unit))
        if not player.has_bet("Place8"):
            player.bet(Place8(6 / 5 * unit))

    if table.bet_update_info is not None:
        # place6
        if player.has_bet("Place6"):
            bet = player.get_bet("Place6")
            if (
                table.bet_update_info[player].get(bet.name) is not None
            ):  # bet has not yet been updated; skip
                # print("level3")
                # print(table.bet_update_info[player][bet.name])
                if table.bet_update_info[player][bet.name]["status"] == "win":
                    # print("place6 mode: {}".format(strat_info["mode6"]))
                    if strat_info["mode6"] == "press":
                        player.remove(bet)
                        player.bet(Place6(2 * bet.bet_amount))
                        strat_info["mode6"] = "regress"
                    elif strat_info["mode6"] == "regress":
                        player.remove(bet)
                        player.bet(Place6(6 / 5 * unit))
                        strat_info["mode6"] = "collect"
                    elif strat_info["mode6"] == "collect":
                        strat_info["mode6"] = "press"
                    # print("updated place6 mode: {}".format(strat_info["mode6"]))
        # place8
        if player.has_bet("Place8"):
            bet = player.get_bet("Place8")
            if (
                table.bet_update_info[player].get(bet.name) is not None
            ):  # bet has not yet been updated; skip
                # print("level3")
                # print(table.bet_update_info[player][bet.name])
                if table.bet_update_info[player][bet.name]["status"] == "win":
                    # print("place8 mode: {}".format(strat_info["mode8"]))
                    if strat_info["mode8"] == "press":
                        player.remove(bet)
                        player.bet(Place8(2 * bet.bet_amount))
                        strat_info["mode8"] = "regress"
                    elif strat_info["mode8"] == "regress":
                        player.remove(bet)
                        player.bet(Place8(6 / 5 * unit))
                        strat_info["mode8"] = "collect"
                    elif strat_info["mode8"] == "collect":
                        strat_info["mode8"] = "press"
    print(strat_info)
    return strat_info

def quarter_pounder_w_ez_phase_1(player, table, unit=5, strat_info=None):
    rolls_before_taking_down_bets = 3

    if strat_info is None:
        strat_info = {'num_rolls': 1, 'places_set_flag': 0}

    place_bet_unit = (unit + 6 % unit) * 2
    field_bet_unit = round(unit)
    hop_bet_unit = round(1) 
    bet_dict = {
        'Place8Working': Place8Working(place_bet_unit),
        'Place6Working': Place6Working(place_bet_unit),
        'Field': Field(field_bet_unit),
        'Hop32': Hop32(hop_bet_unit),
        'Hop41': Hop41(hop_bet_unit)
    }

    if table.last_roll == 7:
        strat_info['num_rolls'] = 1

    for bet_name in bet_dict.keys():
        # Keep the bets on unless we roll our limit
        player.remove_if_present(bet_name)
        # check if we've hit our win limit, only put bets back on if we haven't hit the win limit
        if player.bankroll + player.total_bet_amount < player.win_limit and strat_info['num_rolls'] < rolls_before_taking_down_bets:
            player.bet(bet_dict[bet_name])

    strat_info['num_rolls'] += 1

    return strat_info

def quarter_pounder_w_ez(player, table, unit=5, strat_info=None):
    if strat_info is None:
        strat_info = {'phase': '1', 'num_rolls': 0, 'places_set_flag': 0, 'last_roll_point_status': 'Off'}

    # reset rolls if we crapped out on the point
    if table.last_roll == 7 and strat_info['last_roll_point_status'] == 'On':
        strat_info['num_rolls'] = 0

    place_bet_phase_1_unit = unit * 6
    place68_bet_phase_2_unit = 6/5 * unit
    place59_bet_phase_2_unit = unit
    field_bet_unit = round(unit * 3.5)
    hop_bet_unit = round(unit * 0.5) 
    bet_dict = {
        'Place8': Place8(place_bet_phase_1_unit),
        'Place6': Place6(place_bet_phase_1_unit),
        'Field': Field(field_bet_unit),
        'Hop32': Hop32(hop_bet_unit),
        'Hop41': Hop41(hop_bet_unit)
    }
    if player.bankroll + player.total_bet_amount < unit * 16.5:
        # We hit our limit, remove all bets
        for bet in player.bets_on_table:
            player.remove(bet)

    elif table.point == 'On':
        if strat_info['phase'] == '1':
            # Every roll, we're going to want all the bets to be on. We can remove and add them all each roll to get that
            for bet_name in bet_dict.keys():
                player.remove_if_present(bet_name)
                player.bet(bet_dict[bet_name])
            strat_info['num_rolls'] += 1
        # Clear all existing bets and place 1 unit inside to start phase 2
        elif strat_info['phase'] == '2' and not strat_info['places_set_flag']:
            for bet_name in bet_dict.keys():
                player.remove_if_present(bet_name)
            player.bet(Place8(place68_bet_phase_2_unit))
            player.bet(Place6(place68_bet_phase_2_unit))
            player.bet(Place5(place59_bet_phase_2_unit))
            player.bet(Place9(place59_bet_phase_2_unit))
            strat_info['places_set_flag'] = 1 # places are now set
        elif strat_info['phase'] == '2' and strat_info['places_set_flag']:
            bet_to_make = None
            for bet in player.bets_on_table:
                bet_object = player.get_bet(bet.name)
                if table.bet_update_info[player][bet_object.name]['status'] == 'win':
                    player.remove(bet_object)
                    if bet_object.name == 'Place8':
                        bet_to_make = Place8(bet_object.bet_amount + place68_bet_phase_2_unit)
                    elif bet_object.name == 'Place6':
                        bet_to_make = Place6(bet_object.bet_amount + place68_bet_phase_2_unit)
                    elif bet_object.name == 'Place5':
                        bet_to_make = Place5(bet_object.bet_amount + place59_bet_phase_2_unit)
                    elif bet_object.name == 'Place9':
                        bet_to_make = Place9(bet_object.bet_amount + place59_bet_phase_2_unit)    
            try:
                player.bet(bet_to_make)
            except:
                pass

        strat_info['last_roll_point_status'] = 'On'

    elif table.point == 'Off':
        if strat_info['phase'] == '1':
            for bet_name in bet_dict.keys():
                player.remove_if_present(bet_name)
        # Crapped out after phase 2, go back to phase 1 and reset everything
        elif strat_info['phase'] == '2':
            if table.last_roll == 7 and strat_info['last_roll_point_status'] == 'On':
                strat_info['phase'] = '1'
                strat_info['places_set_flag'] = 0
                strat_info['num_rolls'] = 0
            # We hit a place bet previously and need to up our bet, this seems overly complicated, 
            # but the table doesn't perceive a bet there because it is off on the come out
            elif table.last_roll in (5,6,8,9) and strat_info['places_set_flag']:
                if table.last_roll == 5:
                    place5_bet = player.get_bet('Place5')
                    player.remove(place5_bet)
                    player.bet(Place5(place5_bet.bet_amount + place59_bet_phase_2_unit))
                if table.last_roll == 6:
                    place6_bet = player.get_bet('Place6')
                    player.remove(place6_bet)
                    player.bet(Place6(place6_bet.bet_amount + place68_bet_phase_2_unit))
                if table.last_roll == 8:
                    place8_bet = player.get_bet('Place8')
                    player.remove(place8_bet)
                    player.bet(Place8(place8_bet.bet_amount + place68_bet_phase_2_unit))
                if table.last_roll == 9:
                    place9_bet = player.get_bet('Place9')
                    player.remove(place9_bet)
                    player.bet(Place9(place9_bet.bet_amount + place59_bet_phase_2_unit))
        strat_info['last_roll_point_status'] = 'Off'

    if strat_info['num_rolls'] == 2:
        strat_info['phase'] = '2'
        
    return strat_info

# Need to find a way to update bet amounts when a point is hit on a 5,6,8,9
def quarter_pounder_w_ez_banklimit(player, table, unit=5, strat_info=None):
    if strat_info is None:
        strat_info = {'phase': '1', 'num_rolls': 0, 'places_set_flag': 0, 'last_roll_point_status': 'Off'}

    # reset rolls if we crapped out on the point
    if table.last_roll == 7 and strat_info['last_roll_point_status'] == 'On':
        strat_info['num_rolls'] = 0

    place_bet_phase_1_unit = unit * 6
    place68_bet_phase_2_unit = 6/5 * unit
    place59_bet_phase_2_unit = unit
    field_bet_unit = round(unit * 3.5)
    hop_bet_unit = round(unit * 0.5) 
    bet_dict = {
        'Place8': Place8(place_bet_phase_1_unit),
        'Place6': Place6(place_bet_phase_1_unit),
        'Field': Field(field_bet_unit),
        'Hop32': Hop32(hop_bet_unit),
        'Hop41': Hop41(hop_bet_unit)
    }

    if player.bankroll + player.total_bet_amount >= player.win_limit or player.bankroll + player.total_bet_amount < unit * 16.5:
        # We hit our limit, remove all bets
        for bet in player.bets_on_table:
            player.remove(bet)

    elif table.point == 'On':
        if strat_info['phase'] == '1':
            # Every roll, we're going to want all the bets to be on. We can remove and add them all each roll to get that
            for bet_name in bet_dict.keys():
                player.remove_if_present(bet_name)
                player.bet(bet_dict[bet_name])
            strat_info['num_rolls'] += 1
        # Clear all existing bets and place 1 unit inside to start phase 2
        elif strat_info['phase'] == '2' and not strat_info['places_set_flag']:
            for bet_name in bet_dict.keys():
                player.remove_if_present(bet_name)
            player.bet(Place8(place68_bet_phase_2_unit))
            player.bet(Place6(place68_bet_phase_2_unit))
            player.bet(Place5(place59_bet_phase_2_unit))
            player.bet(Place9(place59_bet_phase_2_unit))
            strat_info['places_set_flag'] = 1 # places are now set
        elif strat_info['phase'] == '2' and strat_info['places_set_flag']:
            bet_to_make = None
            for bet in player.bets_on_table:
                bet_object = player.get_bet(bet.name)
                if table.bet_update_info[player][bet_object.name]['status'] == 'win':
                    player.remove(bet_object)
                    if bet_object.name == 'Place8':
                        bet_to_make = Place8(bet_object.bet_amount + place68_bet_phase_2_unit)
                    elif bet_object.name == 'Place6':
                        bet_to_make = Place6(bet_object.bet_amount + place68_bet_phase_2_unit)
                    elif bet_object.name == 'Place5':
                        bet_to_make = Place5(bet_object.bet_amount + place59_bet_phase_2_unit)
                    elif bet_object.name == 'Place9':
                        bet_to_make = Place9(bet_object.bet_amount + place59_bet_phase_2_unit)    
            try:
                player.bet(bet_to_make)
            except:
                pass

        strat_info['last_roll_point_status'] = 'On'

    elif table.point == 'Off':
        if strat_info['phase'] == '1':
            for bet_name in bet_dict.keys():
                player.remove_if_present(bet_name)
        # Crapped out after phase 2, go back to phase 1 and reset everything
        elif strat_info['phase'] == '2':
            if table.last_roll == 7 and strat_info['last_roll_point_status'] == 'On':
                strat_info['phase'] = '1'
                strat_info['places_set_flag'] = 0
                strat_info['num_rolls'] = 0
            # We hit a place bet previously and need to up our bet, this seems overly complicated, 
            # but the table doesn't perceive a bet there because it is off on the come out
            elif table.last_roll in (5,6,8,9) and strat_info['places_set_flag']:
                if table.last_roll == 5:
                    place5_bet = player.get_bet('Place5')
                    player.remove(place5_bet)
                    player.bet(Place5(place5_bet.bet_amount + place59_bet_phase_2_unit))
                if table.last_roll == 6:
                    place6_bet = player.get_bet('Place6')
                    player.remove(place6_bet)
                    player.bet(Place6(place6_bet.bet_amount + place68_bet_phase_2_unit))
                if table.last_roll == 8:
                    place8_bet = player.get_bet('Place8')
                    player.remove(place8_bet)
                    player.bet(Place8(place8_bet.bet_amount + place68_bet_phase_2_unit))
                if table.last_roll == 9:
                    place9_bet = player.get_bet('Place9')
                    player.remove(place9_bet)
                    player.bet(Place9(place9_bet.bet_amount + place59_bet_phase_2_unit))
        strat_info['last_roll_point_status'] = 'Off'

    if strat_info['num_rolls'] == 2:
        strat_info['phase'] = '2'
        
    return strat_info

def triplelux68_banklimit(player, table, unit=5, strat_info=None):
    unit = player.unit
    win_limit = player.win_limit

    def update_power_press_bets(number_to_update):
        number_to_update_str = str(number_to_update)

        # If the round was lost, reset the progression
        if table.last_roll_point_status == 'On' and table.dice.total == 7:
            strat_info[f"progression{number_to_update_str}"] = 0
            strat_info[f"mode{number_to_update_str}"] = "power_press"

        if table.point == "On":
            if not player.has_bet(f"Place{number_to_update_str}") and player.bankroll + player.total_bet_amount < win_limit:
                current_prog_bet = bet_progressions[number_to_update][strat_info[f'progression{number_to_update_str}']]

                # set the bets
                if number_to_update == 6:
                    bet = Place6(current_prog_bet)
                elif number_to_update == 8:
                    bet = Place8(current_prog_bet)
                    
                player.bet(bet)
            elif player.has_bet(f"Place{number_to_update_str}") and player.bankroll + player.total_bet_amount >= win_limit:
                # Remove these bets immediately and stop playing.
                for bet_nm in ["Place6", "Place8"]:
                    player.remove_if_present(bet_nm)
                
        
        if table.bet_update_info is not None:
            # print(f'Progression number: {strat_info[f"progression{number_to_update_str}"]}')
            # place6 and place8
            if player.has_bet(f"Place{number_to_update_str}"):
                bet = player.get_bet(f"Place{number_to_update_str}")
                if (
                    table.bet_update_info[player].get(bet.name) is not None
                ):  # bet has not yet been updated; skip
                    # Take wins as soon as you hit the win_limit
                    # if player.bankroll > win_limit:
                    #     player.remove(bet)
                    #     return strat_info
                    # print("level3")
                    if table.bet_update_info[player][bet.name]["status"] == "win":
                        # print(f"place{number_to_update_str} mode: {}".format(strat_info[f"mode{number_to_update_str}"]))
                        # if we're power pressing in the first 2 progression levels or we're collecting on any level above the 3rd progression level
                        if  (strat_info[f"mode{number_to_update_str}"] == "power_press" and strat_info[f"progression{number_to_update_str}"] < 2) or\
                            (strat_info[f"progression{number_to_update_str}"] >= 2 and strat_info[f"mode{number_to_update_str}"] == 'collect'):
                            # move to the next progression, but check if it's at the max
                            if strat_info[f"progression{number_to_update_str}"]+1 != len(bet_progressions[number_to_update]):
                                strat_info[f"progression{number_to_update_str}"] += 1
                            else:
                                pass # The progression has gotten to the max
                            
                            current_prog_bet = bet_progressions[number_to_update][strat_info[f'progression{number_to_update_str}']]
                            player.remove(bet)
                            if number_to_update == 6:
                                player.bet(Place6(current_prog_bet))
                            elif number_to_update == 8:
                                player.bet(Place8(current_prog_bet))
                            # Need to reset this in cases where we're in the 'collect' mode
                            strat_info[f"mode{number_to_update_str}"] = "power_press" # Need to reset this in cases where we're in the 'collect' mode
                        # If we hit on the 3rd or higher, we want to collect one win prior to power_pressing again
                        elif strat_info[f"progression{number_to_update_str}"] >= 2 and strat_info[f"mode{number_to_update_str}"] == 'power_press':
                            strat_info[f"mode{number_to_update_str}"] = "collect"


    if strat_info == None:
        strat_info = {"progression6": 0, "progression8": 0, "mode6": "power_press", "mode8": "power_press"}

    # Unit may be 5 or more, need to account for all values
    value_to_get_unit_to_be_divisible_by_6 = math.ceil(unit / 6) if unit != 6 else 0
    if value_to_get_unit_to_be_divisible_by_6:
        unit_for_68 = unit + (value_to_get_unit_to_be_divisible_by_6)
    else:
        unit_for_68 = unit

    bet_progressions = {
        4:  [unit, unit*3, unit*8, unit*20, unit*60],
        5:  [unit, unit*3, unit*7.2, unit*17.2, unit*40, unit*60, unit*100],
        6:  [unit_for_68, unit_for_68*3, unit_for_68*7, unit_for_68*15, unit_for_68*30, unit_for_68*65, unit_for_68*75],
        8:  [unit_for_68, unit_for_68*3, unit_for_68*7, unit_for_68*15, unit_for_68*30, unit_for_68*65, unit_for_68*75],
        9:  [unit, unit*3, unit*7.2, unit*17.2, unit*40, unit*60, unit*100],
        10: [unit, unit*3, unit*8, unit*20, unit*60]
    }

    update_power_press_bets(6)
    update_power_press_bets(8)
                        
    # print("updated place6 mode: {}".format(strat_info["mode6"]))
    return strat_info


def triplelux68(player, table, strat_info=None):

    unit = player.unit

    def update_power_press_bets(number_to_update):
        number_to_update_str = str(number_to_update)

        # If the round was lost, reset the progression
        if table.last_roll_point_status == 'On' and table.dice.total == 7:
            strat_info[f"progression{number_to_update_str}"] = 0
            strat_info[f"mode{number_to_update_str}"] = "power_press"

        if table.point == "On":
            if not player.has_bet(f"Place{number_to_update_str}"):
                current_prog_bet = bet_progressions[number_to_update][strat_info[f'progression{number_to_update_str}']]

                # set the bets
                if number_to_update == 6:
                    bet = Place6(current_prog_bet)
                elif number_to_update == 8:
                    bet = Place8(current_prog_bet)
                    
                player.bet(bet)
        
        if table.bet_update_info is not None:
            # print(f'Progression number: {strat_info[f"progression{number_to_update_str}"]}')
            # place6 and place8
            if player.has_bet(f"Place{number_to_update_str}"):
                bet = player.get_bet(f"Place{number_to_update_str}")
                if (
                    table.bet_update_info[player].get(bet.name) is not None
                ):  # bet has not yet been updated; skip
                    # print("level3")
                    if table.bet_update_info[player][bet.name]["status"] == "win":
                        # print(f"place{number_to_update_str} mode: {}".format(strat_info[f"mode{number_to_update_str}"]))
                        # if we're power pressing in the first 2 progression levels or we're collecting on any level above the 3rd progression level
                        if  (strat_info[f"mode{number_to_update_str}"] == "power_press" and strat_info[f"progression{number_to_update_str}"] < 2) or\
                            (strat_info[f"progression{number_to_update_str}"] >= 2 and strat_info[f"mode{number_to_update_str}"] == 'collect'):
                            # move to the next progression, but check if it's at the max
                            if strat_info[f"progression{number_to_update_str}"]+1 != len(bet_progressions[number_to_update]):
                                strat_info[f"progression{number_to_update_str}"] += 1
                            else:
                                pass # The progression has gotten to the max
                            
                            current_prog_bet = bet_progressions[number_to_update][strat_info[f'progression{number_to_update_str}']]
                            player.remove(bet)
                            if number_to_update == 6:
                                player.bet(Place6(current_prog_bet))
                            elif number_to_update == 8:
                                player.bet(Place8(current_prog_bet))
                            # Need to reset this in cases where we're in the 'collect' mode
                            strat_info[f"mode{number_to_update_str}"] = "power_press" # Need to reset this in cases where we're in the 'collect' mode
                        # If we hit on the 3rd or higher, we want to collect one win prior to power_pressing again
                        elif strat_info[f"progression{number_to_update_str}"] >= 2 and strat_info[f"mode{number_to_update_str}"] == 'power_press':
                            strat_info[f"mode{number_to_update_str}"] = "collect"


    if strat_info == None:
        strat_info = {"progression6": 0, "progression8": 0, "mode6": "power_press", "mode8": "power_press"}

    # Unit may be 5 or more, need to account for all values
    value_to_get_unit_to_be_divisible_by_6 = math.ceil(unit / 6) if unit != 6 else 0
    if value_to_get_unit_to_be_divisible_by_6:
        unit_for_68 = unit + (value_to_get_unit_to_be_divisible_by_6)
    else:
        unit_for_68 = unit

    bet_progressions = {
        4:  [unit, unit*3, unit*8, unit*20, unit*60],
        5:  [unit, unit*3, unit*7.2, unit*17.2, unit*40, unit*60, unit*100],
        6:  [unit_for_68, unit_for_68*3, unit_for_68*7, unit_for_68*15, unit_for_68*30, unit_for_68*65, unit_for_68*75],
        8:  [unit_for_68, unit_for_68*3, unit_for_68*7, unit_for_68*15, unit_for_68*30, unit_for_68*65, unit_for_68*75],
        9:  [unit, unit*3, unit*7.2, unit*17.2, unit*40, unit*60, unit*100],
        10: [unit, unit*3, unit*8, unit*20, unit*60]
    }

    update_power_press_bets(6)
    update_power_press_bets(8)
                        
    # print("updated place6 mode: {}".format(strat_info["mode6"]))
    return strat_info


def triplelux5689(player, table, unit=5, strat_info=None):
    unit = player.unit
 
    def update_power_press_bets(number_to_update):
        number_to_update_str = str(number_to_update)

        # If the round was lost, reset the progression
        if table.last_roll_point_status == 'On' and table.dice.total == 7:
            strat_info[f"progression{number_to_update_str}"] = 0
            strat_info[f"mode{number_to_update_str}"] = "power_press"

        if table.point == "On":
            if not player.has_bet(f"Place{number_to_update_str}"):
                current_prog_bet = bet_progressions[number_to_update][strat_info[f'progression{number_to_update_str}']]

                # set the bets
                if number_to_update == 5:
                    bet = Place5(current_prog_bet)
                elif number_to_update == 6:
                    bet = Place6(current_prog_bet)
                elif number_to_update == 8:
                    bet = Place8(current_prog_bet)
                elif number_to_update == 9:
                    bet = Place8(current_prog_bet)
                    
                player.bet(bet)
        
        if table.bet_update_info is not None:
            # print(f'Progression number: {strat_info[f"progression{number_to_update_str}"]}')
            # place6 and place8
            if player.has_bet(f"Place{number_to_update_str}"):
                bet = player.get_bet(f"Place{number_to_update_str}")
                if (
                    table.bet_update_info[player].get(bet.name) is not None
                ):  # bet has not yet been updated; skip
                    # print("level3")
                    if table.bet_update_info[player][bet.name]["status"] == "win":
                        # print(f"place{number_to_update_str} mode: {}".format(strat_info[f"mode{number_to_update_str}"]))
                        # if we're power pressing in the first 2 progression levels or we're collecting on any level above the 3rd progression level
                        if  (strat_info[f"mode{number_to_update_str}"] == "power_press" and strat_info[f"progression{number_to_update_str}"] < 2) or\
                            (strat_info[f"progression{number_to_update_str}"] >= 2 and strat_info[f"mode{number_to_update_str}"] == 'collect'):
                            # move to the next progression, but check if it's at the max
                            if strat_info[f"progression{number_to_update_str}"]+1 != len(bet_progressions[number_to_update]):
                                strat_info[f"progression{number_to_update_str}"] += 1
                            else:
                                pass # The progression has gotten to the max
                            
                            current_prog_bet = bet_progressions[number_to_update][strat_info[f'progression{number_to_update_str}']]
                            player.remove(bet)

                            if number_to_update == 5:
                                player.bet(Place5(current_prog_bet))
                            elif number_to_update == 6:
                                player.bet(Place6(current_prog_bet))
                            elif number_to_update == 8:
                                player.bet(Place8(current_prog_bet))
                            elif number_to_update == 9:
                                player.bet(Place9(current_prog_bet))

                            # Need to reset this in cases where we're in the 'collect' mode
                            strat_info[f"mode{number_to_update_str}"] = "power_press" # Need to reset this in cases where we're in the 'collect' mode
                        # If we hit on the 3rd or higher, we want to collect one win prior to power_pressing again
                        elif strat_info[f"progression{number_to_update_str}"] >= 2 and strat_info[f"mode{number_to_update_str}"] == 'power_press':
                            strat_info[f"mode{number_to_update_str}"] = "collect"


    if strat_info == None:
        strat_info = {
            "progression5": 0, 
            "progression6": 0, 
            "progression8": 0, 
            "progression9": 0, 
            "mode5": "power_press", 
            "mode6": "power_press", 
            "mode8": "power_press",
            "mode9": "power_press"
        }

    # Unit may be 5 or more, need to account for all values
    value_to_get_unit_to_be_divisible_by_6 = math.ceil(unit / 6) if unit != 6 else 0
    if value_to_get_unit_to_be_divisible_by_6:
        unit_for_68 = unit + (value_to_get_unit_to_be_divisible_by_6)
    else:
        unit_for_68 = unit

    bet_progressions = {
        4:  [unit, unit*3, unit*8, unit*20, unit*60],
        5:  [unit, unit*3, unit*7.2, unit*17.2, unit*40, unit*60, unit*100],
        6:  [unit_for_68, unit_for_68*3, unit_for_68*7, unit_for_68*15, unit_for_68*30, unit_for_68*65, unit_for_68*75],
        8:  [unit_for_68, unit_for_68*3, unit_for_68*7, unit_for_68*15, unit_for_68*30, unit_for_68*65, unit_for_68*75],
        9:  [unit, unit*3, unit*7.2, unit*17.2, unit*40, unit*60, unit*100],
        10: [unit, unit*3, unit*8, unit*20, unit*60]
    }

    update_power_press_bets(5)
    update_power_press_bets(6)
    update_power_press_bets(8)
    update_power_press_bets(9)
                        
    # print("updated place6 mode: {}".format(strat_info["mode6"]))
    return strat_info

def oops_all_sevens(player, table, unit=5, strat_info=None):
    if strat_info == None:
        strat_info = {
            'num_consecutive_losses': 0, 
            'num_rolls_not_seven': 0,
            'bet_amount': unit
        }

    # if strat_info['num_consecutive_losses'] == 0:
    #     bet_amount = 1
    # elif strat_info['num_consecutive_losses'] % 5 == 0:
    #     bet_amount = unit * (1 + strat_info['num_consecutive_losses'] / 5)
    # else:
    #     bet_amount = strat_info['bet_amount']
    bet_amount = strat_info['bet_amount']
    strat_info['bet_amount'] = bet_amount # Update bet amount for strat_info

    bets_to_make = [
        Hop52(bet_amount),
        Hop61(bet_amount),
        Hop43(bet_amount)
    ]

    for bet_nm in ['Hop61', 'Hop52', 'Hop43']:
        player.remove_if_present(bet_nm)

    if strat_info['num_rolls_not_seven'] > 10: # 1/6 rolls should be a 7, only do this if there are no bets on the table
        if not (player.has_bet(f"Hop61") or player.has_bet(f"Hop52") or player.has_bet(f"Hop43")) and player.has_not_reached_bank_limit():
            for bet in bets_to_make:
                player.bet(bet)

    # instantiate empty list to fill with bets
    bet_result_list = []
    for bet in player.bets_on_table:
        bet_object = player.get_bet(bet.name)
        try:
            current_bet_status = table.bet_update_info[player][bet_object.name]['status']
        except (KeyError, TypeError):
            current_bet_status = None
        bet_result_list.append(current_bet_status)

    # Update the num rolls and consecutive losses
    if table.last_roll == 7:
        strat_info['num_rolls_not_seven'] = 0
    else:
        strat_info['num_rolls_not_seven'] += 1
    
    if 'win' in bet_result_list:
        strat_info['num_consecutive_losses'] = 0
        for bet in player.bets_on_table:
            player.remove_if_present(bet.name)
    elif 'lose' in bet_result_list:
        strat_info['num_consecutive_losses'] += 1
    else:
        pass

    return strat_info

if __name__ == "__main__":
    # Test a betting strategy

    from player import Player
    from dice import Dice
    from table import Table

    # table = CrapsTable()
    # table._add_player(Player(500, place68_2come))

    d = Dice()
    p = Player(500, place68_2come)
    p.bet(PassLine(5))
    p.bet(Place6(6))
    print(p.bets_on_table)
    print(p.bankroll)
    print(p.total_bet_amount)


# Hardways

def hardways_winlimit(player, table, unit=5, strat_info=None):
    if strat_info is None:
        strat_info = {'hardways': 0}

    if table.point == 'On' and player.bankroll + player.total_bet_amount < player.win_limit:
        if strat_info['hardways'] == 0:
            player.bet(Hard4(unit))
            player.bet(Hard6(unit))
            player.bet(Hard8(unit))
            player.bet(Hard10(unit))
            strat_info['hardways'] = 1
        elif strat_info['hardways'] == 1:
            all_bets = ['Hard4', 'Hard6', 'Hard8', 'Hard10']
            # Ensure that all the hardways are replenished if they lost
            curr_bets = list(map(lambda x: x.name, player.bets_on_table))
            for bet in curr_bets:
                all_bets.remove(bet)
            for bet in all_bets:
                player.bet(eval(bet)(unit))

    else:
        if strat_info['hardways'] == 1:
            for bet in player.bets_on_table.copy():
                player.remove(bet)
            strat_info['hardways'] = 0

    return strat_info

def hardways_triple_up(player, table, unit=5, strat_info=None):
    if strat_info is None:
        strat_info = {'hardways': 0, 'times_tripled_up': 0, 'last_roll_point_status': 'Off'}

    try:
        dice_total = table.dice.total
    except:
        dice_total = 0

    if dice_total == 7 and strat_info['last_roll_point_status'] == 'On':
        strat_info['times_tripled_up'] = 0

    if table.point == 'On' and player.bankroll + player.total_bet_amount < player.win_limit and strat_info['times_tripled_up'] < 3:
        strat_info['last_roll_point_status'] = 'On'
        if strat_info['times_tripled_up'] > 0:
            unit = unit * (3 ** strat_info['times_tripled_up'])
        if strat_info['hardways'] == 0:
            player.bet(Hard4(unit))
            player.bet(Hard6(unit))
            player.bet(Hard8(unit))
            player.bet(Hard10(unit))
            strat_info['hardways'] = 1
        elif strat_info['hardways'] == 1:
            if any([table.bet_update_info[player][bet]['status'] == 'win' for bet in table.bet_update_info[player].keys()]):
                for bet in table.bet_update_info[player].keys():
                    try:
                        bet_object = player.get_bet(bet)
                        player.remove(bet_object)
                    except ValueError:
                        bet_object = Bet(bet_amount=unit) # Doesn't matter, this isn't going to be used
                        bet_object.name = bet
                    player.bet(eval(bet_object.name)(unit * 3))
                strat_info['times_tripled_up'] += 1
            all_bets = ['Hard4', 'Hard6', 'Hard8', 'Hard10']

            # Ensure that all the hardways are replenished if they lost
            curr_bets = list(map(lambda x: x.name, player.bets_on_table))
            # Remove the curr bets from all possible bets
            for bet in curr_bets:
                all_bets.remove(bet)
            # The remainder is either no bets (because they're all there) or one bet that would need to be added
            for bet in all_bets:
                player.bet(eval(bet)(unit))

    else:
        strat_info['last_roll_point_status'] = 'Off'
        if strat_info['hardways'] == 1:
            for bet in player.bets_on_table.copy():
                player.remove(bet)
            strat_info['hardways'] = 0

    return strat_info
