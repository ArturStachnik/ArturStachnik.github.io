from flask import Flask, render_template, request
from datetime import datetime, timedelta
import pytz
import ephem

app = Flask(__name__)

# Definir los sitios precargados con sus latitudes y longitudes
sitios_precargados = {
    "Madrid": (40.4168, -3.7038),
    "Barruelo de Santullán": (42.9748, -4.3257),
    "Cameros": (42.2858, 2.4260),
    "Castromonte": (41.4961, -5.0725),
    "Chamonix (FR)": (45.9237, 6.8694),
    "Gredos": (40.250602, -5.280043),
    "Malmö (SW)": (55.599170, 13.017323),
    "Mt Saint-Michell (FR)": (48.636002, -1.511400),
    "Pirineo Central": (42.7679, -0.2317),
    "Reykjavík (IC)": (64.141554, -21.927632),
    "Santiago de Compostela": (42.8782, -8.5448),
    "Tenerife": (28.2916, -16.6291),
    "Wien": (48.210033, 16.363449),
    "Wysokie Tatry (PL)": (49.2992, 19.9496),
    "Żukowo (PL)": (54.222, 18.438)
}

def calcular_eventos_celestes(latitud, longitud, fecha):
    eventos = {}

    for i in range(15):
        fecha_actual = fecha + timedelta(days=i)
        observador = ephem.Observer()
        observador.lat = str(latitud)
        observador.long = str(longitud)
        observador.date = fecha_actual

        sol = ephem.Sun()

        # Crepúsculo civil
        crepusculo_civil = observador.next_setting(sol, use_center=True).datetime().astimezone(pytz.timezone('Europe/Madrid'))
        alba_civil = observador.previous_rising(sol, use_center=True).datetime().astimezone(pytz.timezone('Europe/Madrid'))

        # Crepúsculo náutico
        observador.horizon = '-6'
        crepusculo_nautico = observador.next_setting(sol, use_center=True).datetime().astimezone(pytz.timezone('Europe/Madrid'))
        alba_nautico = observador.previous_rising(sol, use_center=True).datetime().astimezone(pytz.timezone('Europe/Madrid'))

        # Crepúsculo astronómico
        observador.horizon = '-12'
        crepusculo_astronomico = observador.next_setting(sol, use_center=True).datetime().astimezone(pytz.timezone('Europe/Madrid'))
        alba_astronomico = observador.previous_rising(sol, use_center=True).datetime().astimezone(pytz.timezone('Europe/Madrid'))

        # Mediodía solar
        mediodia_solar = observador.next_transit(sol).datetime().astimezone(pytz.timezone('Europe/Madrid'))

        # Calcular horas de luz
        segundos_luz = (crepusculo_civil - alba_civil).seconds
        horas_luz = segundos_luz // 3600
        minutos_luz = (segundos_luz % 3600) // 60
        horas_luz_minutos = f"{horas_luz} horas {minutos_luz} minutos"

        eventos[fecha_actual.strftime("%Y-%m-%d")] = {
            "Alba Astronómico": alba_astronomico.strftime("%H:%M:%S"),
            "Alba Náutico": alba_nautico.strftime("%H:%M:%S"),
            "Alba Civil": alba_civil.strftime("%H:%M:%S"),
            "Mediodía Solar": mediodia_solar.strftime("%H:%M:%S"),
            "Crepúsculo Civil": crepusculo_civil.strftime("%H:%M:%S"),
            "Crepúsculo Náutico": crepusculo_nautico.strftime("%H:%M:%S"),
            "Crepúsculo Astronómico": crepusculo_astronomico.strftime("%H:%M:%S"),
            "Horas de Luz": horas_luz_minutos
        }

    return eventos

@app.route('/')
def index():
    # Página principal donde el usuario selecciona un sitio
    return render_template('index.html', sitios=sitios_precargados)

@app.route('/eventos', methods=['POST'])
def mostrar_eventos():
    # Obtener el sitio seleccionado por el usuario desde el formulario
    sitio_seleccionado = request.form['sitio']
    latitud, longitud = sitios_precargados[sitio_seleccionado]

    # Calcular eventos celestes para el sitio seleccionado
    fecha_actual = datetime.now(pytz.utc)
    eventos_por_dia = calcular_eventos_celestes(latitud, longitud, fecha_actual)

    # Mostrar la información en formato de tabla y gráfica
    return render_template('eventos_celestes.html', eventos=eventos_por_dia, sitio=sitio_seleccionado)

if __name__ == "__main__":
    app.run()