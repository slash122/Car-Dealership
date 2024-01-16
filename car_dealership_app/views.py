from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from datetime import datetime
from .utils.helpers import *
# from django.cursors import DictCursor

# ---------- POJAZDY
def handle_pojazdy(request):
    error_msg = None
    # Dodawanie nowego pojazdu
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                data_produkcji = datetime.strptime(request.POST["data_produkcji"], '%Y-%m-%d')
                marka_id = get_marka_id(cursor, request.POST["marka"])

                insert_pojazd = """INSERT INTO pojazd(salon_id, marka_id, typ, model, numer_vin, cena, przebieg, data_produkcji) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
                values = (request.POST["salon_id"], marka_id, 
                          request.POST["typ"], request.POST["model"],
                          request.POST["numer_vin"], request.POST["cena"], 
                          request.POST["przebieg"], data_produkcji)
                
                cursor.execute(insert_pojazd, values)
        except Exception as e: 
            error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("""SELECT p.pojazd_id, p.salon_id, m.marka, p.typ, p.model, p.numer_vin, p.cena, p.przebieg, p.data_produkcji 
                       FROM pojazd p JOIN marka m ON p.marka_id = m.marka_id ORDER BY p.salon_id, p.pojazd_id ASC;""")
        result = fetchall_and_prepare(cursor)
        marki =  get_marki_pojazdow(cursor)
    
    return render(request, 'pojazd_forms.html', {"data" : result, "error_msg" : error_msg, "marki" : marki})


def get_pojazdy_raport1(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT m.marka, COUNT(*) as ilość, SUM(p.cena) as cena  FROM pojazd p JOIN marka m ON p.marka_id = m.marka_id GROUP BY m.marka ORDER BY ilość DESC;")
        result = fetchall_and_prepare(cursor)
        marki =  get_marki_pojazdow(cursor)
    
    return render(request, 'pojazd_forms.html', {"data" : result, "error_msg" : None, "marki" : marki})


def get_pojazdy_raport2(request):
    with connection.cursor() as cursor:
        cursor.execute("""WITH CTE AS (SELECT m.marka, p.model, p.typ, p.cena, p.przebieg, p.data_produkcji FROM pojazd p JOIN marka m ON p.marka_id = m.marka_id)
                        SELECT dense_rank() OVER (ORDER BY cena DESC) as cena_rank,
                        DENSE_RANK() OVER (PARTITION BY marka ORDER BY cena DESC) as marka_rank,
                        marka, model, typ, cena, przebieg FROM CTE;""")
        result = fetchall_and_prepare(cursor)
        marki =  get_marki_pojazdow(cursor)

    return render(request, 'pojazd_forms.html', {"data" : result, "error_msg" : None, "marki" : marki})


def get_pojazdy_raport3(request):
    error_msg = None
    result: tuple[list, list[dict]] = ([],[{}])
    try:
        with connection.cursor() as cursor:
            sql_query = """SELECT p.pojazd_id, p.salon_id, m.marka, p.typ, p.model, p.numer_vin, p.cena, p.przebieg, p.data_produkcji 
                        FROM pojazd p JOIN marka m ON p.marka_id = m.marka_id WHERE m.marka = %s;"""
            cursor.execute(sql_query, (request.GET["marka"],))
            result = fetchall_and_prepare(cursor) 
    except Exception as e:
        error_msg = str(e)

    with connection.cursor() as cursor:
        marki = get_marki_pojazdow(cursor)

    return render(request, 'pojazd_forms.html', {"data" : result, "error_msg" : error_msg, "marki" : marki})


def delete_pojazd(request):
    error_msg = None
    with connection.cursor() as cursor:
        try:
            delete_sql = "SELECT usun_pojazd_z_wyjatkiem(%s)"
            cursor.execute(delete_sql, (request.POST["usun_id"],))
        except Exception as e:
            error_msg = str(e)

        cursor.execute("""SELECT p.pojazd_id, p.salon_id, m.marka, p.typ, p.model, p.numer_vin, p.cena, p.przebieg, p.data_produkcji 
                       FROM pojazd p JOIN marka m ON p.marka_id = m.marka_id ORDER BY p.salon_id, p.pojazd_id ASC;""")
        result = fetchall_and_prepare(cursor)
        marki =  get_marki_pojazdow(cursor)
    
    return render(request, 'pojazd_forms.html', {"data" : result, "error_msg" : error_msg, "marki" : marki})
# -----------------


# SALONY
def handle_salony(request):
    error_msg = None
    # Dodawanie nowego pojazdu
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                insert_pojazd = """INSERT INTO salon(nazwa, adres) VALUES (%s, %s);"""
                values = (request.POST["nazwa"], request.POST["adres"])
                
                cursor.execute(insert_pojazd, values)
        except Exception as e: 
            error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM salon")
        result = fetchall_and_prepare(cursor)
    
    return render(request, 'salony_forms.html', {"data" : result, "error_msg" : error_msg})


def get_salony_przychody(request):
    error_msg = None
    result: tuple[list, list[dict]] = ([],[{}])
    try: 
        with connection.cursor() as cursor:
            wybrany_miesiac = request.GET["miesiac"]
            sql_miesiac = f"{wybrany_miesiac}-01"
            select_przychody = """SELECT s.salon_id, s.nazwa, SUM(w_f_v.wartość) FROM salon s JOIN pracownik p
            ON p.salon_id = s.salon_id JOIN wartosc_faktury_view w_f_v ON w_f_v.pracownik_id = p.pracownik_id JOIN faktura f
            ON w_f_v.faktura_id = f.faktura_id WHERE f.data > %s AND f.data < (%s::date + INTERVAL '1 month') GROUP BY s.salon_id, s.nazwa"""        
            cursor.execute(select_przychody, (sql_miesiac, sql_miesiac))
            result = fetchall_and_prepare(cursor)

    except Exception as e:
        error_msg = str(e)

    return render(request, 'salony_forms.html', {"data" : result, "error_msg" : error_msg})           


def get_salony_calkowita_wartosc(request):
    with connection.cursor() as cursor:
        select_wartosc = """SELECT s.salon_id, s.nazwa, SUM(p.cena) as wartość FROM salon s JOIN pojazd p ON p.salon_id = s.salon_id
        GROUP BY s.salon_id, s.nazwa;"""
        cursor.execute(select_wartosc)
        result = fetchall_and_prepare(cursor)

    return render(request, 'salony_forms.html', {"data" : result, "error_msg" : None})


def delete_salon(request):
    error_msg = None
    try:
        with connection.cursor() as cursor:
            delete_salon = "DELETE FROM salon WHERE salon_id = %s;"
            cursor.execute(delete_salon, (request.POST["usun_id"],))
    except Exception as e:
        error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM salon")
        result = fetchall_and_prepare(cursor)

    return render(request, 'salony_forms.html', {"data" : result, "error_msg" : error_msg})
# --------------------------

def handle_pracownicy(request):
    error_msg = None
    # Dodawanie nowego pojazdu
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                insert_pracownik = """INSERT INTO pracownik(salon_id, imie, nazwisko, stanowisko) VALUES (%s, %s, %s, %s);"""
                values = (request.POST["salon_id"], request.POST["imie"], request.POST["nazwisko"], request.POST["stanowisko"])
                
                cursor.execute(insert_pracownik, values)
        except Exception as e: 
            error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM pracownik")
        result = fetchall_and_prepare(cursor)
    
    return render(request, 'pracownik_forms.html', {"data" : result, "error_msg" : error_msg})


def get_pracownicy_przychody(request):
    with connection.cursor() as cursor:
        select_wartosc = """SELECT pr.pracownik_id, pr.imie, pr.nazwisko, SUM(w_f_v.wartość) FROM pracownik pr JOIN 
        wartosc_faktury_view w_f_v ON w_f_v.pracownik_id = pr.pracownik_id GROUP BY pr.pracownik_id, pr.imie, pr.nazwisko;"""
        cursor.execute(select_wartosc)
        result = fetchall_and_prepare(cursor)

    return render(request, 'pracownik_forms.html', {"data" : result})


def get_pracownik_pojazdy(request):
    error_msg = None
    result: tuple[list, list[dict]] = ([],[{}])
    try:    
        with connection.cursor() as cursor:
            select_pojazdy = """SELECT pojazd_id, marka, model, typ, przebieg, data_produkcji FROM pracownik_pojazd_view WHERE pracownik_id = %s"""
            cursor.execute(select_pojazdy, (request.GET["pracownik_id"],))
            result = fetchall_and_prepare(cursor)
    except Exception as e:
        error_msg = str(e)
    
    return render(request, 'pracownik_forms.html', {"data" : result, "error_msg" : error_msg})


def delete_pracownik(request):
    error_msg = None
    try:
        with connection.cursor() as cursor:
            delete_pracownik = "DELETE FROM pracownik WHERE pracownik_id = %s;"
            cursor.execute(delete_pracownik, (request.POST["usun_id"],))
    except Exception as e:
        error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM pracownik")
        result = fetchall_and_prepare(cursor)

    return render(request, 'pracownik_forms.html', {"data" : result, "error_msg" : error_msg})
# --------------------------


def handle_klienci(request):
    error_msg = None
    # Dodawanie nowego pracownika
    if request.method == 'POST':
        data_urodzenia = datetime.strptime(request.POST["data_urodzenia"], '%Y-%m-%d')
        try:
            with connection.cursor() as cursor:
                insert_klient = """INSERT INTO klient(imie, nazwisko, data_urodzenia) VALUES (%s, %s, %s);"""
                values = (request.POST["imie"], request.POST["nazwisko"], data_urodzenia)
                
                cursor.execute(insert_klient, values)
        except Exception as e: 
            error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM klient")
        result = fetchall_and_prepare(cursor)
    
    return render(request, 'klient_forms.html', {"data" : result, "error_msg" : error_msg})


def get_klient_obsluga(request):
    error_msg = None
    result: tuple[list, list[dict]] = ([],[{}])
    try:
        with connection.cursor() as cursor:
            obsluga_klient = """SELECT * FROM klient_obsluga_view WHERE klient_id = %s;"""
            cursor.execute(obsluga_klient, (request.GET["o_klient_id"],))
            result = fetchall_and_prepare(cursor)
    
    except Exception as e:
        error_msg = str(e)

    return render(request, 'klient_forms.html', {"data" : result, "error_msg" : error_msg})


def get_klient_pojazd(request):
    error_msg = None
    result: tuple[list, list[dict]] = ([],[{}])
    try:
        with connection.cursor() as cursor:
            pojazd_klienta = "SELECT * FROM klient_pojazd_view WHERE klient_id = %s;"
            cursor.execute(pojazd_klienta, (request.GET["klient_id"],))
            result = fetchall_and_prepare(cursor)
    except Exception as e:
        error_msg = str(e)
    
    return render(request, 'klient_forms.html', {"data" : result, "error_msg" : error_msg})


def delete_klient(request):
    error_msg = None
    try:
        with connection.cursor() as cursor:
            delete_klient = "DELETE FROM klient WHERE klient_id = %s;"
            cursor.execute(delete_klient, (request.POST["usun_id"],))
    except Exception as e:
        error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM klient")
        result = fetchall_and_prepare(cursor)

    return render(request, 'klient_forms.html', {"data" : result, "error_msg" : error_msg})
# --------------------------


# FAKTURY
def handle_faktury(request):
    error_msg = None
    # Dodawanie nowej fakury
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                insert_faktura = "INSERT INTO faktura(data, klient_id, pracownik_id) VALUES(CURRENT_DATE, %s, %s)"
                values = (request.POST["klient_id"], request.POST["pracownik_id"])
                cursor.execute(insert_faktura, values)
        
        except Exception as e:
            error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("""SELECT f.faktura_id, f.data, f.klient_id, kl.imie as klient_imie, kl.nazwisko as klient_nazwisko, pr.pracownik_id, pr.imie, pr.nazwisko 
                       FROM faktura f JOIN klient kl ON f.klient_id = kl.klient_id JOIN pracownik pr ON f.pracownik_id = pr.pracownik_id;""")
        result = fetchall_and_prepare(cursor)

    return render(request, 'faktura_forms.html', {"data" : result, "error_msg" : error_msg})


def handle_faktura_pojazd(request):
    error_msg = None
    # Dodawanie nowej faktury
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                insert_pojazd = "INSERT INTO faktura_pojazd(faktura_id, pojazd_id) VALUES (%s, %s)"
                values = (request.POST["faktura_id"], request.POST["pojazd_id"])
                cursor.execute(insert_pojazd, values)
        
        except Exception as e:
            error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("""SELECT * FROM klient_pojazd_view;""")
        result = fetchall_and_prepare(cursor)

    return render(request, 'faktura_forms.html', {"data" : result, "error_msg" : error_msg})


def get_faktura_wartosc(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM wartosc_faktury_view")
        result = fetchall_and_prepare(cursor)

    return render(request, 'faktura_forms.html', {"data" : result})


def delete_faktura(request):
    error_msg = None
    faktura_id = request.POST["usun_id"]
    print(faktura_id)
    try:
        with connection.cursor() as cursor:
            unset_null_pojazd = "UPDATE pojazd SET salon_id = 1 WHERE pojazd_id IN (SELECT pojazd_id FROM klient_pojazd_view WHERE faktura_id = %s);"
            cursor.execute(unset_null_pojazd, (faktura_id,) )
            delete_faktura_pojazd = "DELETE FROM faktura_pojazd WHERE faktura_id = %s;"
            cursor.execute(delete_faktura_pojazd, (faktura_id,))
            delete_faktura = "DELETE FROM faktura WHERE faktura_id = %s;"
            cursor.execute(delete_faktura, (faktura_id,))
    except Exception as e:
        error_msg = str(e)

    with connection.cursor() as cursor:
        cursor.execute("""SELECT f.faktura_id, f.data, f.klient_id, kl.imie as klient_imie, kl.nazwisko as klient_nazwisko, pr.pracownik_id, pr.imie, pr.nazwisko 
                       FROM faktura f JOIN klient kl ON f.klient_id = kl.klient_id JOIN pracownik pr ON f.pracownik_id = pr.pracownik_id;""")
        result = fetchall_and_prepare(cursor)

    return render(request, 'faktura_forms.html', {"data" : result, "error_msg" : error_msg})
# ---------------------------


def handle_serwisy(request):
    error_msg = None
    # Dodawanie nowego pracownika
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                insert_serwis = """INSERT INTO serwis(nazwa) VALUES (%s);"""
                values = (request.POST["nazwa"],)
                
                cursor.execute(insert_serwis, values)
        except Exception as e: 
            error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM serwis")
        result = fetchall_and_prepare(cursor)
    
    return render(request, 'serwis_forms.html', {"data" : result, "error_msg" : error_msg})


def handle_obsluga(request):
    error_msg = None
    # result: tuple[list, list[dict]] = ([],[{}])
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                data_oddania = datetime.strptime(request.POST["data_oddania"], '%Y-%m-%d')
                data_zwrotu = datetime.strptime(request.POST["data_zwrotu"], '%Y-%m-%d')
                print(data_oddania)
                print(data_zwrotu)
                
                insert_obsluga = """INSERT INTO obsluga_serwisowa(serwis_id, pojazd_id, klient_id, data_oddania, data_zwrotu, komentarz) 
                VALUES(%s, %s, %s, %s, %s, %s)"""
                values = (request.POST["serwis_id"], request.POST["pojazd_id"],
                          request.POST["klient_id"], data_oddania, data_zwrotu,
                          request.POST["komentarz"])
                
                cursor.execute(insert_obsluga, values)
                
        except Exception as e:
            error_msg = str(e)

    with connection.cursor() as cursor:
        cursor.execute("""SELECT s.nazwa, o_s.obsluga_serwisowa_id, o_s.pojazd_id, m.marka, p.model, o_s.klient_id, kl.imie, kl.nazwisko 
                       FROM obsluga_serwisowa o_s JOIN serwis s ON o_s.serwis_id = s.serwis_id 
                       JOIN pojazd p ON o_s.pojazd_id = p.pojazd_id JOIN marka m ON p.marka_id = m.marka_id 
                       JOIN klient kl ON kl.klient_id = o_s.klient_id""")
        result = fetchall_and_prepare(cursor)

    return render(request, 'serwis_forms.html', {"data" : result, "error_msg" : error_msg})


def delete_obsluga(request):
    error_msg = None
    try:
        with connection.cursor() as cursor:
            delete_obsluga = "DELETE FROM obsluga_serwisowa WHERE obsluga_serwisowa_id = %s;"
            cursor.execute(delete_obsluga, (request.POST["obsluga_usun_id"],))
    except Exception as e:
        error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("""SELECT s.nazwa, o_s.obsluga_serwisowa_id, o_s.pojazd_id, m.marka, p.model, o_s.klient_id, kl.imie, kl.nazwisko 
                       FROM obsluga_serwisowa o_s JOIN serwis s ON o_s.serwis_id = s.serwis_id 
                       JOIN pojazd p ON o_s.pojazd_id = p.pojazd_id JOIN marka m ON p.marka_id = m.marka_id 
                       JOIN klient kl ON kl.klient_id = o_s.klient_id""")
        result = fetchall_and_prepare(cursor)

    return render(request, 'serwis_forms.html', {"data" : result, "error_msg" : error_msg})


def delete_serwis(request):
    error_msg = None
    try:
        with connection.cursor() as cursor:
            delete_serwis = "DELETE FROM serwis WHERE serwis_id = %s;"
            cursor.execute(delete_serwis, (request.POST["usun_id"],))
    except Exception as e:
        error_msg = str(e)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM serwis")
        result = fetchall_and_prepare(cursor)

    return render(request, 'serwis_forms.html', {"data" : result, "error_msg" : error_msg})