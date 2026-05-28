from flask import Flask, render_template, redirect, url_for, session, flash, jsonify, request, get_flashed_messages
from werkzeug.security import check_password_hash
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
app = Flask(__name__)

app.secret_key = 'mi_clave_secreta_super_segura'

# =====================================================================
# CONFIGURACIÓN DE LA BASE DE DATOS POSTGRESQL
# =====================================================================
DB_HOST = "localhost"
DB_NAME = "arion_db"     
DB_USER = "postgres"      
DB_PASS = "123456"  

def get_db_connection():
    """Establece una conexión limpia con la base de datos."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

# =====================================================================
# RUTA DE PRUEBA PARA CONEXIÓN
# =====================================================================
@app.route('/test-db')
def test_db():
    try:
        # 1. Conectamos a la base de datos
        conn = get_db_connection()
        # Usamos RealDictCursor para que nos devuelva los resultados como diccionarios Python
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 2. Hacemos una consulta para traer al usuario que creamos
        cursor.execute("SELECT id, nombre, email FROM usuarios;")
        usuarios_registrados = cursor.fetchall()
        
        # 3. Cerramos los flujos de conexión de forma limpia
        cursor.close()
        conn.close()
        
        # 4. Mostramos el resultado en formato JSON en el navegador para verificar
        return jsonify({
            "status": "Conexión exitosa a PostgreSQL 🚀",
            "usuarios_en_bd": usuarios_registrados
        }), 200
        
    except Exception as e:
        # Si algo falla (contraseña mal puesta, BD apagada, etc.), te dirá el error exacto
        return jsonify({
            "status": "Error de conexión ❌",
            "detalles": str(e)
        }), 500

# =====================================================================
# CONTROLES DE ACCESO Y DEMÁS RUTAS... (Tu código se mantiene abajo)
# =====================================================================
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
@app.route('/login', methods=['GET', 'POST']) # <-- ¡Aquí agregamos methods=['GET', 'POST']!
def login():
    # Si el usuario ya está logueado, lo mandamos al home
    if 'user_id' in session:
        return redirect(url_for('home'))

    # PROCESAR EL FORMULARIO CUANDO PRESIONAN EL BOTÓN (POST)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Validación básica de campos vacíos
        if not email or not password:
            flash('Por favor, completa todos los campos.', 'error')
            return render_template('login.html')

        conn = None
        cursor = None
        try:
            # Conexión segura a tu base de datos PostgreSQL
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Consulta preparada para mitigar inyecciones SQL
            query = "SELECT id, nombre, email, password FROM usuarios WHERE email = %s;"
            cursor.execute(query, (email,))
            usuario = cursor.fetchone()
            
        except Exception as e:
            flash('Ocurrió un error en el servidor. Inténtalo más tarde.', 'error')
            return render_template('login.html')
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

        # Validación de las credenciales
        # NOTA: check_password_hash evalúa el hash seguro de PostgreSQL.
        # Si hiciste la prueba con texto plano ('clave123'), cambia temporalmente esta línea por:
        # if usuario and usuario['password'] == password:
        # CAMBIO TEMPORAL: Compara texto plano directo con la base de datos
        if usuario and usuario['password'] == password:
            session.clear()
            session['user_id'] = usuario['id']
            session['user_name'] = usuario['nombre']
            
            flash(f'¡Bienvenido de nuevo, {usuario["nombre"]}!', 'success')
            return redirect(url_for('home'))
            # MOSTRAR LA PÁGINA NORMALMENTE (GET)
            # Limpiamos los mensajes acumulados si el usuario no viene rebotado del guard de acceso
    if not session.pop('redirected_by_guard', None):
        get_flashed_messages(with_categories=True)
        
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