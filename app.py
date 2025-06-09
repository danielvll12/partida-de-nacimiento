from flask import Flask, render_template, request, redirect, url_for, send_file, session
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import io
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'



@app.route('/pago_tarjeta', methods=['GET', 'POST'])
def pago_tarjeta():
    if 'partida' not in session:
        return redirect(url_for('solicitar'))
    
    if request.method == 'POST':
        numero_tarjeta = request.form.get('numero_tarjeta')
        codigo_tarjeta = request.form.get('codigo_tarjeta')
        monto = request.form.get('monto')

        # Aquí iría la validación o integración con pasarela real.
        # Por ahora solo simulamos éxito si hay datos:

        if not (numero_tarjeta and codigo_tarjeta and monto):
            flash("Por favor complete todos los campos.", "error")
            return render_template('pago_tarjeta.html')

        # Simulación de pago exitoso:
        flash("Pago realizado con éxito. Gracias.", "success")
        return redirect(url_for('confirmacion_pago'))

    return render_template('pago_tarjeta.html')


@app.route('/confirmacion_pago')
def confirmacion_pago():
    return render_template('confirmacion_pago.html')

@app.route('/pago_banco')
def pago_banco():
    if 'partida' not in session:
        return redirect(url_for('solicitar'))

    datos_pago = {
        'banco': 'Banco Agrícola',
        'numero_cuenta': '1234567890',
        'titular_cuenta': 'Alcaldía Municipal Ejemplo',
        'monto': '5.00 USD',
        'codigo_referencia': 'PARTIDA-' + datetime.now().strftime('%Y%m%d%H%M%S'),
        'instrucciones': 'Por favor haga su pago en ventanilla o banca móvil y envíe el comprobante al correo pago@ejemplo.com'
    }
    return render_template('pago_banco.html', datos=datos_pago)


@app.route('/')
def inicio():
    return redirect(url_for('solicitar'))



@app.route('/solicitar', methods=['GET', 'POST'])
def solicitar():
    if request.method == 'POST':
        session['partida'] = {
            'nombre': request.form['nombre'],
            'fecha_nacimiento': request.form['fecha_nacimiento'],
            'lugar_nacimiento': request.form['lugar_nacimiento'],
            'nombre_padre': request.form['nombre_padre'],
            'nombre_madre': request.form['nombre_madre']
        }
        # Cambia aquí la redirección:
        return redirect(url_for('pago_tarjeta'))
    return render_template('solicitar.html')

# Ruta para mostrar el botón de descarga
@app.route('/descargar_pdf')
def descargar_pdf():
    # Comprobar que hay datos en sesión
    if 'partida' not in session:
        return redirect(url_for('solicitar'))
    return render_template('mostrar_pdf.html')  # Esta plantilla debe tener el botón para descargar

@app.route('/generar_pdf')
def generar_pdf():
    partida = session.get('partida')
    if not partida:
        return "No hay datos de partida.", 400

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 50, "ALCALDÍA MUNICIPAL DE COJUTEPEQUE")
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 80, "PARTIDA DE NACIMIENTO ORIGINAL")

    y = height - 130
    espacio = 20
    pdf.setFont("Helvetica", 12)
    pdf.drawString(80, y, f"Nombre del inscrito: {partida['nombre']}")
    y -= espacio
    pdf.drawString(80, y, f"Fecha de nacimiento: {partida['fecha_nacimiento']}")
    y -= espacio
    pdf.drawString(80, y, f"Lugar de nacimiento: {partida['lugar_nacimiento']}")
    y -= espacio
    pdf.drawString(80, y, f"Nombre del padre: {partida['nombre_padre']}")
    y -= espacio
    pdf.drawString(80, y, f"Nombre de la madre: {partida['nombre_madre']}")
    y -= 60
    pdf.drawString(80, y, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y')}")
    y -= 40
    pdf.drawString(80, y, "Firma del Registrador Municipal: _______________________")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="partida_nacimiento.pdf", mimetype="application/pdf")

if __name__ == '__main__':
    app.run(debug=True)
