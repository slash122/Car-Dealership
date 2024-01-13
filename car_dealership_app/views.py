from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from datetime import datetime
from .utils.helpers import *
# from django.cursors import DictCursor


def handle_pojazdy(request):
    error_msg = None
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                data_produkcji = datetime.strptime(request.POST["data_produkcji"], '%Y-%m-%d')
                marka_id = get_marka_id(cursor, request.POST["marka"])
                print(marka_id)

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
                       FROM pojazd p JOIN marka m ON p.marka_id = m.marka_id;""")
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
                       FROM pojazd p JOIN marka m ON p.marka_id = m.marka_id;""")
        result = fetchall_and_prepare(cursor)
        marki =  get_marki_pojazdow(cursor)
    
    return render(request, 'pojazd_forms.html', {"data" : result, "error_msg" : error_msg, "marki" : marki})





def get_salony(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT nazwa, adres FROM salon;")
        result = fetchall_and_prepare(cursor)

    return render(request, 'sql_query_table.html', {"data" : result})


def get_klienci(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT klient_id, imie, nazwisko, data_urodzenia FROM klient;")
        result = fetchall_and_prepare(cursor)
    
    return render(request, 'sql_query_table.html', {"data" : result})


def get_pracownicy(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM pracownik;")
        result = fetchall_and_prepare(cursor)
    
    return render(request, 'sql_query_table.html', {"data" : result})


def get_faktury(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM faktura;")
        result = fetchall_and_prepare(cursor)
    
    return render(request, 'sql_query_table.html', {"data" : result})


def get_serwisy(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM serwis;")
        result = fetchall_and_prepare(cursor)
    
    return render(request, 'sql_query_table.html', {"data" : result})