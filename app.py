from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Emiliovc22@172.20.144.1:5434/Quadra'  # URL de tu base de datos
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Ruta para guardar las imágenes
app.config['MAX_CONTENT_PATH'] = 1024 * 1024  # Tamaño máximo de la imagen 1MB

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

# Modelos
class Usuarios(db.Model, UserMixin):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.contraseña = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.contraseña, password)

    def get_id(self):
        return str(self.id_usuario)

class Puestos(db.Model):
    id_puesto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    foto = db.Column(db.String(255), nullable=True)  # Ruta a la imagen
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    ubicacion = db.relationship('Ubicaciones', backref='puesto', uselist=False, cascade="all, delete-orphan")

class Ubicaciones(db.Model):
    id_ubicacion = db.Column(db.Integer, primary_key=True)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    id_puesto = db.Column(db.Integer, db.ForeignKey('puestos.id_puesto'), nullable=False)

class Calificaciones(db.Model):
    id_calificacion = db.Column(db.Integer, primary_key=True)
    calificacion = db.Column(db.Integer, nullable=False)
    id_puesto = db.Column(db.Integer, db.ForeignKey('puestos.id_puesto'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

class Comentarios(db.Model):
    id_comentario = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.Text, nullable=False)
    id_puesto = db.Column(db.Integer, db.ForeignKey('puestos.id_puesto'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

# Cargar usuario
@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        user = Usuarios.query.filter_by(email=email).first()
        if user:
            flash('El correo electrónico ya está registrado. Por favor, usa uno diferente.', 'danger')
            return redirect(url_for('signup'))

        new_user = Usuarios(nombre=nombre, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Usuarios.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Inicio de sesión incorrecto', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/subir_puesto', methods=['GET', 'POST'])
@login_required
def subir_puesto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        foto = request.files['foto']

        # Procesar la imagen
        if foto:
            filename = secure_filename(foto.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(filepath)

        # Crear y guardar el puesto
        nuevo_puesto = Puestos(
            nombre=nombre,
            descripcion=descripcion,
            foto=filename if foto else None,
            id_usuario=current_user.id_usuario
        )
        db.session.add(nuevo_puesto)
        db.session.commit()

        # Guardar ubicación
        nueva_ubicacion = Ubicaciones(
            latitud=latitud,
            longitud=longitud,
            id_puesto=nuevo_puesto.id_puesto
        )
        db.session.add(nueva_ubicacion)
        db.session.commit()

        flash('Puesto subido exitosamente', 'success')
        return redirect(url_for('home'))

    return render_template('subir_puesto.html')

@app.route('/ver_puesto/<int:id_puesto>')
def ver_puesto(id_puesto):
    puesto = Puestos.query.get_or_404(id_puesto)
    comentarios = Comentarios.query.filter_by(id_puesto=id_puesto).all()
    return render_template('ver_puestos.html', puesto=puesto, comentarios=comentarios)

@app.route('/ver_puestos')
@login_required
def ver_todos_los_puestos():
    puestos = Puestos.query.all()  # Obtén todos los puestos de la base de datos
    return render_template('ver_puestos.html', puestos=puestos)

@app.route('/calificar/<int:id_puesto>', methods=['POST'])
@login_required
def calificar(id_puesto):
    calificacion = request.form['calificacion']
    nueva_calificacion = Calificaciones(
        calificacion=calificacion,
        id_puesto=id_puesto,
        id_usuario=current_user.id_usuario
    )
    db.session.add(nueva_calificacion)
    db.session.commit()
    flash('Puesto calificado exitosamente', 'success')
    return redirect(url_for('ver_puesto', id_puesto=id_puesto))

@app.route('/comentar/<int:id_puesto>', methods=['POST'])
@login_required
def comentar(id_puesto):
    comentario = request.form['comentario']
    nuevo_comentario = Comentarios(
        comentario=comentario,
        id_puesto=id_puesto,
        id_usuario=current_user.id_usuario
    )
    db.session.add(nuevo_comentario)
    db.session.commit()
    flash('Comentario agregado exitosamente', 'success')
    return redirect(url_for('ver_puesto', id_puesto=id_puesto))

if __name__ == '__main__':
    app.run(debug=True)
