from __future__ import print_function
from flask import Flask, render_template, request
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import date

app = Flask(__name__)
# app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# Bootstrap(app)

SERVICE_ACCOUNT_FILE = 'key.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SPREADSHEET_ID = '1AqWqR1BZmaX8iVDoiRFO8wLspgGvOiwzdWSYynRq0mQ'
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()

def fecha(dia):
    if dia == "hoy":
        return date.today().strftime("%d/%m/%Y")
    else:
        return dia

def det_mes(date):
    date_list = date.split('/')
    mes_num = date_list[1]
    return MESES[int(mes_num)-1]

def get_prices(mes):
    num = MESES.index(mes)
    prices_info = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"datos!B{MESES.index(mes)+2}:C{MESES.index(mes)+2}").execute()
    return prices_info.get('values', [])[0]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/varios")
def varios():
    return render_template("varios.html")

@app.route("/jornal")
def jornal():
    return render_template("jornal.html")

@app.route("/jornal/add", methods=["POST"])
def jornal_add():
    fecha = request.form["fecha"]
    if fecha == "hoy":
        dia = date.today().strftime("%d/%m/%Y")
    else:
        dia = fecha
    dia_fecha = int(dia.split('/')[0])
    mes_num = dia.split('/')[1]
    mes = MESES[int(mes_num)-1]
    numero_jornadas = float(request.form["numjornadas"])
    horas_extra = float(request.form["numextras"])
    actividad = request.form["actividad"]
    zona = request.form["zona"]
    zonados = request.form["zonados"]
    zonatres = request.form["zonatres"]
    precios = get_prices(mes)
    sheet_vector = [dia, numero_jornadas, horas_extra, actividad, f"{zona}, {zonados}, {zonatres}", numero_jornadas * float(precios[0]) + horas_extra * float(precios[1])]
    print(sheet_vector)
    sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f"{mes}!A{dia_fecha+1}:Q{dia_fecha+1}", valueInputOption="USER_ENTERED", body={"values":[sheet_vector]}).execute()
    return render_template("index.html")

@app.route("/gastos/add", methods=["POST"])
def gastos_add():
    fecha = request.form["fecha"]
    if fecha == "hoy":
        dia = date.today().strftime("%d/%m/%Y")
    else:
        dia = fecha
    dia_fecha = int(dia.split('/')[0])
    mes_num = dia.split('/')[1]
    mes = MESES[int(mes_num)-1]
    concepto = request.form["concepto"]
    actividad = request.form["actividad"]
    zona = request.form["zona"]
    cantidad = float(request.form["cantidad"])
    banco = request.form["banco"]
    sheet_vector = [dia, concepto, actividad, zona, cantidad, banco]
    print(sheet_vector)
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{mes}!H1:M100").execute()
    values = result.get('values', [])
    sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f"{mes}!H{len(values)+1}:M{len(values)+1}",valueInputOption="USER_ENTERED", body={"values": [sheet_vector]}).execute()
    return render_template("index.html")

@app.route("/piso")
def piso():
    return render_template("piso.html")

@app.route("/piso/alquiler")
def alquiler():
    return render_template("alquiler.html")

@app.route("/piso/alquiler/add", methods=["POST"])
def alquiler_add():
    fecha = request.form["fecha"]
    if fecha == "hoy":
        dia = date.today().strftime("%d/%m/%Y")
    else:
        dia = fecha
    dia_fecha = int(dia.split('/')[0])
    mes_num = dia.split('/')[1]
    mes = MESES[int(mes_num) - 1]
    concepto = "Cobro Alquiler"
    cantidad = float(request.form["cantidad"])
    sheet_vector = [dia, concepto, cantidad]
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{mes}!O2:Q100").execute()
    values = result.get('values', [])
    sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f"{mes}!O{len(values) + 2}:Q{len(values) + 2}", valueInputOption="USER_ENTERED", body={"values": [sheet_vector]}).execute()
    return render_template("index.html")

@app.route("/piso/recibos")
def recibos():
    return render_template("recibos.html")

@app.route("/piso/recibos/add", methods=["POST"])
def recibos_add():
    fecha = request.form["fecha"]
    if fecha == "hoy":
        dia = date.today().strftime("%d/%m/%Y")
    else:
        dia = fecha
    dia_fecha = int(dia.split('/')[0])
    mes_num = dia.split('/')[1]
    mes = MESES[int(mes_num) - 1]
    concepto = request.form["concepto"]
    cantidad = -float(request.form["cantidad"])
    sheet_vector = [dia, concepto, cantidad]
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{mes}!O2:Q100").execute()
    values = result.get('values', [])
    sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f"{mes}!O{len(values) + 2}:Q{len(values) + 2}", valueInputOption="USER_ENTERED", body={"values": [sheet_vector]}).execute()
    return render_template("index.html")

@app.route("/gastos")
def gastos():
    return render_template("gastos.html")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)