#       Loogisen lausekkeen ratkaisuohjelma
#
#       Tekijä: Jussi Laitala
#
#       Ohjelma ratkaisee loogisia lausekkeita symbolien avulla, tulostaa
#       lausekkeesta totuustaulukon ja kertoo onko lauseke mahdollisesti
#       tautologia tai kontradiktio.
#
#       Ohjelma vaatii toimiakseen colorama-moduulin jotta värikomennot
#       toimisivat myös windowsin komentokehotteessa. Värit voi myös ottaa
#       pois päältä asettamalla COLORS-vakion arvoksi 0 ja poistamalla
#       coloraman alun paketeista. Coloraman voi asentaa terminaalissa
#       komennolla "pip install colorama".
#
#       Ohjelman käynnistysparametreilla voi myös vaikuttaa vakioihin:
#       -c = värit päälle
#       -b = ei värejä
#       -n = numerot lausekkeen osissa
#       -a = kirjaimet lausekkeen osissa

import msvcrt               # kirjastoa tarvitsee msvrt.getch() komennolle joka lukee yhden näppäimen
import colorama             # kirjasto värikoodeille windows-ympäristöön
import sys                  # kirjastoa käytetään käynnistysparametreille

class key_code:             # koodit näppäinkomennoille
    KEY_1           = b'1'
    KEY_2           = b'2'
    KEY_3           = b'3'
    KEY_4           = b'4'
    KEY_5           = b'5'
    KEY_6           = b'6'
    KEY_7           = b'7'
    KEY_8           = b'8'
    KEY_9           = b'9'
    KEY_0           = b'0'
    KEY_ENTER       = b'\r'
    KEY_BACKSPACE   = b'\x08'

class color:                # värikoodit print()-funktiolle
    BLUE    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\u001b[31m"
    END     = "\033[0m"

MAX_SIZE    = 25        # symbolien maksimimäärä
MAX_COUNT   = 20        # lausekkeiden osien maksimimäärä
COLORS      = 1         # vakio väreille (1=päällä 0=pois)
NUM_OR_ALPH = 0         # vakio lausekkeen osien nimeämiselle (1=kirjaimet 0=numerot)

L_p         = 1         # vakiot loogisille symboleille ja sulkumerkeille sekä pyyhkimiskomennolle
L_q         = 2
L_r         = 3
L_not       = 4
L_and       = 5
L_or        = 6
L_if        = 7
L_orif      = 8
L_brack_r   = 9
L_brack_l   = 10
L_backspace = 11

logic_statement = [0] * MAX_SIZE    # symbolien maksimimäärä
statement_curs = 0       # symbolien kirjoittamisen kursorin sijainti
bracket_count = [0,0]    # sulkumerkkien vakio
table_size = [0,0]       # totuustaulukon koko [pituus, korkeus]
logic_count_order = [[0] * 4 for i in range(MAX_SIZE)]      # loogisten laskujen laskujärjestys
logic_count_result = [[-1] * 8 for i in range(MAX_COUNT)]   # loogisten laskujen tulokset listattuna ykkösinä ja nollina
logic_calculation = [[0] * 5 for i in range(MAX_COUNT)]     # loogisten laskujen tiedot: mitä verrataan mihinkin lausekkeen osaan
logic_count_string = ["" for i in range(MAX_COUNT)]         # loogisten laskujen tulostettavat symbolit

string_size = [0,1,1,1,1,3,3,4,5]   # tulostettavien symbolien merkkijonojen pituus. Alkuun tulostettavaa värikoodia ei oteta huomioon

truth_table = [[1,1,0,1,1,1,1],   # totuustaulukko mitä käytetään loogisten osien laskemiseen
               [1,0,0,1,0,0,0],
               [0,1,1,1,0,1,0],
               [0,0,1,0,0,1,1]]

# Funktio palauttaa pyydetyn loogisen symbolin tai numeron värjättynä tai normaalina merkkijonona
# Kun log_char > 20 palauttaa funktio numeron (log_char - 19 eli 1-..) tai kirjaimen A-Z
def return_log_string(log_char):
    log_char -= 1
    logic_character = ["p","q","r","~"," v "," ^ "," => "," <=> ","(",")"]
    logic_colors = [color.YELLOW, color.YELLOW, color.YELLOW, color.RED, color.RED,
                    color.RED, color.RED, color.RED, color.BLUE, color.BLUE]

    if log_char > 19:
        if (COLORS):
            if NUM_OR_ALPH: # valitaan palautetaanko värillinen numero vai kirjain
                return str(color.GREEN + chr(64 + (log_char-19)))
            else:
                return str(color.GREEN + str(log_char-19))
        else:
            if NUM_OR_ALPH: #valitaan palautetaanko normaali numero vai kirjain
                return chr(64 + (log_char-19))
            else:
                return str(log_char-19)
    else:
        if (COLORS):    # jos log_char on välillä 1-11 palautetaan sitä vastaava symboli
            return str(logic_colors[log_char] + logic_character[log_char])
        else:
            return str(logic_character[log_char])

#   Funktiolle syötetään painettu näppäin ja se tarkistaa voiko pyydetyn symbolin tulostaa.
#   Jos tulostus onnistuu, palauttaa funktio symbolin koodin, muuten palautetaan arvo 0.
#   Jos käyttäjä painaa backspacea ja kursori ei ole rivin alussa, palautetaan -1.
def press_key(key):
    global bracket_count

    if L_p <= key <= L_r:
        if statement_curs > 0:
            if ((logic_statement[statement_curs-1] >= L_p) and (logic_statement[statement_curs-1] <= L_r)) or (logic_statement[statement_curs-1] == L_brack_l): return 0
    elif key == L_not:
        if statement_curs > 0:
            if ((logic_statement[statement_curs-1] >= L_p) and (logic_statement[statement_curs-1] <= L_not)) or (logic_statement[statement_curs-1] == L_brack_l): return 0
    elif L_and <= key <= L_orif:
        if statement_curs == 0: return 0
        if (logic_statement[statement_curs-1] > L_r) and (logic_statement[statement_curs-1] < L_brack_l): return 0
    elif key == L_brack_r:
        if statement_curs > 0:
            if ((logic_statement[statement_curs-1] >= L_p) and (logic_statement[statement_curs-1] <= L_r)) or (logic_statement[statement_curs-1] == L_brack_l): return 0
        bracket_count[0] += 1
    elif key == L_brack_l:
        if bracket_count[0] == bracket_count[1]: return 0
        if statement_curs == 0: return 0
        if (logic_statement[statement_curs-1] > L_r) and (logic_statement[statement_curs-1] < L_brack_l): return 0
        bracket_count[1] += 1
    elif key == L_backspace:
        if statement_curs == 0: return 0
        if logic_statement[statement_curs-1] == L_brack_r:
            bracket_count[0] -= 1
        elif logic_statement[statement_curs-1] == L_brack_l:
            bracket_count[1] -= 1
        print("\033[2K\033[1G", end = '\r')     # pyyhitään rivi tyhjäksi ja siirretään kursori rivin alkuun
        return -1

    print(return_log_string(key), end = '', flush = True)   # Tulostetaan pyydetty symboli, flush = True lisätään loppuun jotta tuloste näkyy heti näytöllä.
    return key

#   Funktio järjestää loogisen lausekkeen konnektiivit oikeaan suoritusjärjestykseen ja purkaa sulut pois.
#   Funktio myös laskee konnektiivit ja tallentaa arvot totuustaulukkoon.
def set_count_order():
    global logic_statement          # globaalit muuttujat mitä funktiossa muokataan
    global logic_count_order
    global logic_count_result
    global logic_string
    global table_size
    global logic_calculation
    brack_order = 0                 # muuttuja lasekttavalle sulkupaketille
    highest_brack = 0               # korkein sulkupaketti lausekkeessa
    count_max = 0                   # viimeinen laskettava symboli
    count = 0
    count_pqr = 1                   # lausekkeen eri lauseiden määrä (p, q ,r)
    logic_pqr = [-1, -1, -1]        # lauseiden järjestys totuustaulukossa
    pqr_count = 0                   # lauseiden laskuri

    for i in range(0,statement_curs):           # Sulkujen poistaminen ja korkeimman sulkupaketin tallennus mistä
        if logic_statement[i] == L_brack_r:     # konnektiivien laskeminen aloitetaan.
            brack_order += 1
            highest_brack += 1
        elif logic_statement[i] == L_brack_l:
             brack_order -= 1
        else:
            if L_p <= logic_statement[i] <= L_r:                    # Jos tarkistettava symboli on p, q tai r, niin tallennetaan
                logic_pqr[logic_statement[i]-L_p] = L_p             # sen symboli ja laskujärjestys taulukkoon järjestyksessä.
            logic_count_order[count_max][0] = brack_order           # Tämä tehdään heti aluksi, jotta saadaan symbolit kirjattua
            logic_count_order[count_max][1] = logic_statement[i]    # totuustaulukon alkuun.
            count_max += 1

    for i in range(0,3):
        if logic_pqr[i] > -1:
            logic_calculation[pqr_count][0] = 1                         # Järjestetään lausekkeen osat totuustaulukkoon p:n, q:n ja r:n osalta
            logic_calculation[pqr_count][1] = i + 1                     # johon tallennetaan myös tulostettava merkkijono ja merkkijonon
            logic_calculation[pqr_count][2] = i + 1                     # pituus ilman mahdollisia värikoodeja.
            logic_calculation[pqr_count][3] = string_size[i + 1]
            logic_count_string[pqr_count] += return_log_string(i + 1)
            logic_pqr[i] = pqr_count
            pqr_count += 1
            table_size[0] += 1

    for i in range(0, count_max):                                                   # Tallennetaan laskujärjestystaulukkoon viittaus totuustaulukon
        if L_p <= logic_count_order[i][1] <= L_r:                                   # alkioihin p:n, q:n ja r:n osalta laittamalla näiden tilalle arvon
            logic_count_order[i][1] = logic_pqr[logic_count_order[i][1]-1] + 20     # 20 + (p, q tai r). Arvot 1 - 11 on varattu symboleille ja konnektiiveille.

    table_size[1] = 2 ** pqr_count      # Määritellään totuustaulukon koko pystysuunnassa joka on riippuvainen monta eri vaihtoehtoa
                                        # loogisessa lausekkeessa on (p, q, r).
    for i in range(0,table_size[0]):    # Määritellään lausekkeen vaihtoehtojen arvot totuustaulukon alkuun.
        count = 0
        for i2 in range(0,count_pqr):
            for i3 in range(0,int(2 ** (pqr_count-1))):
                logic_count_result[i][count] = 1
                count += 1
            for i3 in range(0,int(2 ** (pqr_count-1))):
                logic_count_result[i][count] = 0
                count += 1
        pqr_count -= 1
        count_pqr *= 2

    current_brack = highest_brack       # laskuvuorossa oleva sulkupaketti määritellään lausekkeen korkeimman sulkupaketin mukaan
    count_cur_max = 0                   # laskuvuorossa olevan sulkupaketin viimeinen symboli
    count_start = table_size[0]         # ensimmäinen vapaa alkio totuustaulukossa p:n, q:n ja r:n jälkeen
    count_current = count_start         # muuttujalla määritellään missä alkiossa mennään totuustaulukossa
    calculated_count = 1                # muuttuja määrittelee laskettavan konnektiivin tuloksen järjestyksen
    check_old = 0                       # muuttujalla etsitään totuustaulukosta samanlaista laskua
    calc_logic = 0                      # laskuvuorossa oleva konnektiivi
    calc_order = 0                      # muuttuja konnektiivien laskujärjestykselle
    calc_table = [0,1,1,2,2]            # loogisten konnektiivien laskujärjestys [not, and, or, if, orif]
    i = 0                               # muuttujalla käydään läpi lauseketta kun suoritetaan konnektiivit oikeassa järjestyksessä

    while current_brack > -1:           # silmukkaa suoritetaan kunnes kaikki sulkeet on poistettu ja laskettu
        while i < count_max:            # silmukkaa suoritetaan kunnes ollaan viimeisessä laskettavassa symbolissa
            if logic_count_order[i][0] == current_brack:
                count_cur_max = i                                               # Kun saavutetaan laskujärjestykseesä oleva sulkupaketti, määritetään sen sisällä olevat symbolit jotka lasketaan.
                for count_cur_max in range(i, count_max):
                    if logic_count_order[count_cur_max][0] < current_brack:
                        break
                for calc_order in range(0,3):                                   # Suoritetaan sulkupaketin laskut oikeassa laskujärjestyksessä (1 = negaatiot, 2 = konjuktiot ja disjunktiot, 3 = implikaatiot ja ekvivalenssit)
                    i2 = i
                    while i2 < count_cur_max:       # silmukka suoritetaan kyseisen sulkupaketin loppuun
                        calc_logic = logic_count_order[i2][1]   # tallennetaan laskuvuorossa oleva konnektiivi muuttujaan
                        if L_not <= calc_logic <= L_orif and calc_table[calc_logic - L_not] == calc_order:  # jos symboli on konnektiivi ja oikeassa laskuvuorossa, suoritetaan lasku
                            logic_calculation[count_current][0] = 2 + (calc_logic - L_not)                  # tallennetaan kyseinen konnektiivi
                            logic_calculation[count_current][1] = logic_count_order[i2+1][1]                # mikä lauseke verrataan
                            if calc_logic == L_not:
                                logic_calculation[count_current][2] = logic_count_order[i2+1][1]            # negaatio suoritetaan vain seuraavaan lausekkeen osaan
                                logic_calculation[count_current][3] = string_size[calc_logic] + 1
                            else:
                                logic_calculation[count_current][2] = logic_count_order[i2-1][1]            # Mihin lauseke verrataan. Muut kuin negaatiot verrataan kahteen lausekkeen osaan
                                logic_calculation[count_current][3] = string_size[calc_logic] + 2
                            logic_calculation[count_current][4] = calculated_count                          # tallennetaan lausekkeen osan järjestysnumero

                            if calc_logic > L_not:                                                          # tallennetaan konnektiivin tulostettava merkkijono
                                if L_p <= logic_calculation[logic_count_order[i2 - 1][1] - 20][1] <= L_r:
                                    logic_count_string[count_current] += return_log_string(logic_calculation[logic_count_order[i2-1][1]-20][1])     # jos suoritettava lauseke on q, p tai r, tallenetaan sen merkki
                                else:
                                    logic_count_string[count_current] += return_log_string(logic_calculation[logic_count_order[i2-1][1]-20][4] + 20)    # muutoin tallennetaan suoritettavan lausekkeen järjestysnumero

                            if L_p <= logic_calculation[logic_count_order[i2 + 1][1] - 20][1] <= L_r:
                                logic_count_string[count_current] += return_log_string(calc_logic) + return_log_string(logic_calculation[logic_count_order[i2+1][1]-20][1])
                            else:
                                logic_count_string[count_current] += return_log_string(calc_logic) + return_log_string(logic_calculation[logic_count_order[i2+1][1]-20][4] + 20)

                            check_old = -1
                            for i3 in range(count_start, count_current):        # etsitään totuustaulukosta samanlaista lauseketta
                                if (logic_calculation[count_current][0] == logic_calculation[i3][0]) and (logic_calculation[count_current][1] == logic_calculation[i3][1]) and (logic_calculation[count_current][2] == logic_calculation[i3][2]):
                                    check_old = i3

                            if check_old == -1:                                 # jos samanlaista lauseketta ei löydy, suoritetaan lausekkeen osan lasku ja tallennetaan se totuustaulukkoon
                                for i4 in range(0, table_size[1]):
                                    for i3 in range(0, 4):
                                        if truth_table[i3][0] == logic_count_result[logic_calculation[count_current][1]-20][i4] and truth_table[i3][1] == logic_count_result[logic_calculation[count_current][2]-20][i4]:
                                            logic_count_result[count_current][i4] = truth_table[i3][calc_logic-2]
                                logic_count_order[i2][1] = 20 + count_current
                                table_size[0] += 1
                                count_current += 1
                                calculated_count += 1
                            else:                                               # muutoin tallennetaan vanhan lausekkeen osan järjestysnumero laskutaulukkoon
                                logic_count_order[i2][1] = 20 + check_old
                                logic_count_string[count_current] = ""

                            del logic_count_order[i2+1]                         # poistetaan jo laskettu symboli laskutaulukosta
                            if calc_logic > L_not:                              # negaatiossa poistetaan vain seuraava symboli, muissa konnektiiveissa myös edellinen symboli
                                del logic_count_order[i2-1]
                                count_cur_max -=2                               # kun lasketut symbolit on poistettu laskutaulukosta, niin sulkupaketin symbolimäärää pienennetään
                                count_max -= 2
                                i2 -=1
                            else:
                                count_cur_max -=1
                                count_max -= 1
                        i2 += 1
                i = count_cur_max
            i += 1
        for i4 in range(0, count_max):                                          # Kun ylimmät sulkupaketit on laskettu, tarkistetaan laskutaulukko ja asetetaan kyseisten symbolien sulkuarvo
            if logic_count_order[i4][0] == current_brack:                       # yksi alaspäin jotta ne otetaan huomioon kun aletaan laskemaan alempia sulkupaketteja.
                logic_count_order[i4][0] -= 1
        current_brack -= 1
        i = 0

    return

# Funktio tulostaa totuustaulukon ja kertoo jos looginen lauseke on mahdollisesti
# tautologia tai kontradiktio.
def draw_logic_table():

    row_count = 1
    empty_space = ""        # tyhjä merkkijono mikä tulostetaan taulukon osien väliin tarvittaessa
    col_print = ["","",""]  # jos värit eivät ole käytössä, tulostetaan tyhjä merkkijono niiden tilalle
    if COLORS:
        col_print = [color.END, color.GREEN, color.BLUE]

    print("Totuustaulukko lausekkeelle:\n")

    print(" " + col_print[1], end = '')
    for i in range(0,table_size[0]-1):
        empty_space = " " * (logic_calculation[i][3])       # lasketaan tyhjän merkkijonon pituus lausekkeen pituuden mukaan
        if logic_calculation[i][4] > 0:     # jos lausekkeen osaa käytetään muissa taulukon osissa, niin tulostetaan sen järjestysnumero taulukon alkuun
            print(return_log_string(logic_calculation[i][4] + 20) + empty_space, end = '')
        else :
            print(empty_space + " ", end = '')      # tulostetaan tyhjä merkkijono, jotta taulukon rivit ovat samalla tasolla
    print()

    # Tulostetaan totuustaulukko ja pysty- sekä vaakaviivat erottamaan taulukon arvot toisistaan.
    print(col_print[0] + "|", end = '')
    for i in range(0,table_size[0]):
        print(logic_count_string[i] + col_print[0] + "|", end = '')
        row_count += (logic_calculation[i][3] + 1)
    print("\n" + "-" * row_count)

    for i2 in range(0,table_size[1]):
        print(col_print[0] + "|", end = '')
        for i in range(0,table_size[0]):
            if (logic_calculation[i][3] - 1) > 0:
                empty_space = " " * (logic_calculation[i][3] - 1)
            else :
                empty_space = ""
            print(col_print[2] + str(logic_count_result[i][i2]) + empty_space + col_print[0] + "|", end = '')
        print("")
    print("", flush = True)
    tautologia = 0
    for i in range(0,table_size[1]):                            # lasketaan totuustaulukon viimeiset arvot yhteen ja jos kaikki ovat arvoa 1, niin lauseke
        tautologia += logic_count_result[table_size[0]-1][i]    # on tautologia. Jos kaikki arvot ovat 0, niin lauseke on kotradiktio.
    if tautologia == table_size[1]:
        print ("Lauseke on tautologia.\n")
    elif tautologia == 0:
        print ("Lauseke on kontradiktio.\n")
    return

# Pääfunktio mikä suoritetaan käynnistäessä ohjelma.
# argv sisältää ohjelmaa käynnistäessä syötetyt parametrit
def main(argv):

    global COLORS                   # globaalit muuttujat esitellään jotta niitä voidaan muokata funktiossa
    global NUM_OR_ALPH
    arguments = len(sys.argv) - 1   # käynnistysparametrien määrä

    if arguments > 0:                                   # tarkistetaan käynnistysparametrit ja muutetaan vakioita tarvittaessa
        for i in range(1, arguments+1):
            if sys.argv[i] == "-c": COLORS = 1
            elif sys.argv[i] == "-b": COLORS = 0
            elif sys.argv[i] == "-n": NUM_OR_ALPH = 0
            elif sys.argv[i] == "-a": NUM_OR_ALPH = 1

    col_print = ["","","",""]       # värikoodit jos värit käytössä, muuten käytetään tyhjää merkkijonoa tulosteissa
    if COLORS:
        colorama.init()             # kyännistetän colorama - moduuli jotta värien merkit toimivat
        col_print = [color.END, color.GREEN, color.BLUE, color.YELLOW]

    global logic_statement
    global logic_stat_size
    global statement_curs
    return_value = 0
    key_press = ''

    logic_characters = ["p","q","r","~","v","^","=>","<=>","(",")"]     # symbolien merkkijonot alun ohjeeseen

    print()
    for i in range(0,10):           # tulostetaan ohje millä näppäimellä saa minkäkin symbolin lausekkeeseen
        print (col_print[1] + str((i+1)%10) + col_print[0] + ":" + col_print[3] + logic_characters[i], end = '  ', flush = True)

    print(col_print[0] + "\n\nAnna looginen lauseke:", flush = True)

    while key_press != key_code.KEY_ENTER:      # suoritetaan ohjelmaa kunnes käyttäjä painaa enteriä
        return_value = 0
        key_press = msvcrt.getch()              # odotetaan kunnes käyttäjä painaa jotain näppäintä

        if statement_curs < MAX_SIZE:           # jos maksimimäärä symboleita ei ole täynnä, tarkistetaan mitä näppäintä käyttäjä painoi
            if key_press == key_code.KEY_1: return_value = press_key(L_p)
            elif key_press == key_code.KEY_2: return_value = press_key(L_q)
            elif key_press == key_code.KEY_3: return_value = press_key(L_r)
            elif key_press == key_code.KEY_4: return_value = press_key(L_not)
            elif key_press == key_code.KEY_5: return_value = press_key(L_and)
            elif key_press == key_code.KEY_6: return_value = press_key(L_or)
            elif key_press == key_code.KEY_7: return_value = press_key(L_if)
            elif key_press == key_code.KEY_8: return_value = press_key(L_orif)
            elif key_press == key_code.KEY_9: return_value = press_key(L_brack_r)
            elif key_press == key_code.KEY_0: return_value = press_key(L_brack_l)
            elif key_press == key_code.KEY_BACKSPACE: return_value = press_key(L_backspace)
        else:
            if key_press == key_code.KEY_BACKSPACE: return_value = press_key(L_backspace)   # muuten tarkisteaan vain haluaako käyttäjä pyyhkiä symboleita

        if return_value > 0:                                    # Jos käyttäjän pyytämä symboli voidaan syöttää, niin se tallennetaan taulukkoon
            logic_statement[statement_curs] = return_value      # ja siirretään kursoria seuraavaan kohtaan lausekkeessa.
            statement_curs += 1
        elif return_value < 0:                                  # Jos symbolin pyyhkimien on mahdollista, siirretään kursoria yksi taaksepäin ja asetetaan
            statement_curs -= 1                                 # edellisen symbolin arvoksi nolla. Pyyhitty lauseke tulostetaan ruudulle uudestaan.
            logic_statement[statement_curs]=0
            for i in range(0,statement_curs):
                print(return_log_string(logic_statement[i]), end ='')
                print(end = '', flush = True)

    print(col_print[0] + "\n")

    if statement_curs == 0:                                     # Kun lauseke on muodostettu, tarkistetaan onko lauseke pätevä (sulut ovat oikein eikä lopu konnektiiviin)
        print("Tyhjä lauseke.\n")
        return 0
    elif (bracket_count[0] != bracket_count[1]) or (L_r < logic_statement[statement_curs - 1] <= L_orif):
        print("Kelvoton lauseke.\n")
        return 0

    set_count_order()           # lasketaan lauseke totuustaulukkoon
    draw_logic_table()          # tulostetaan totuustaulukko
    msvcrt.getch()

main(sys.argv)                  # pääohjelman käynnistys ja käynnistysparametrien syöttö
