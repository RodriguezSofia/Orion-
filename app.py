from flask import Flask, render_template, redirect, url_for, session, flash
from functools import wraps
app = Flask(__name__)

app.secret_key = 'mi_clave_secreta_super_segura'

# =====================================================================
# CONTROLES DE ACCESO 
# =====================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =====================================================================
# RUTAS PÚBLICAS
# =====================================================================
@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register')
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')


# =====================================================================
# RUTAS PROTEGIDAS 
# =====================================================================

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/explorar')
@login_required
def explorar():
    return render_template('explorar_proyectos.html')

@app.route('/subir')
@login_required
def subir():
    return render_template('subir_proyecto.html')

@app.route('/perfil')
@login_required
def perfil():
    return render_template('mi_perfil.html')

@app.route('/recursos')
@login_required
def recursos():
    return render_template('recursos.html')

# Ruta dinámica para ver un proyecto por su ID 
@app.route('/proyecto/<int:id>')
@login_required
def ver_proyecto(id):
    return render_template('ver_proyecto.html', proyecto_id=id)

# =====================================================================
# MANEJO DE ERRORES 
# =====================================================================
# Captura el error 404 (Página no encontrada)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('page_not_found.html'), 404

@app.route('/error-registro')
def user_not_registered_error():
    return render_template('user_not_registered_error.html')

# Ruta auxiliar para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)