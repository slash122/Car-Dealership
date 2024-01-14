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
            delete_sql = "DELETE FROM pojazd WHERE pojazd_id = %s;"
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
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM serwis;")
        result = fetchall_and_prepare(cursor)
    
    return render(request, 'sql_query_table.html', {"data" : result})