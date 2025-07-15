import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:pass@localhost:5432/mycruddb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Trailer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    youtube_url = db.Column(db.String(200), nullable=False)
    fecha_estreno = db.Column(db.Date, nullable=True)

# Crear tablas al iniciar la app
def init_db():
    with app.app_context():
        db.create_all()
init_db()

@app.route('/')
def index():
    trailers = Trailer.query.order_by(Trailer.fecha_estreno).all()
    return render_template('index.html', trailers=trailers)

@app.route('/trailer/<int:id>')
def detail(id):
    tr = Trailer.query.get_or_404(id)
    return render_template('detail.html', trailer=tr)

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        fecha = None
        if request.form.get('fecha_estreno'):
            fecha = datetime.strptime(request.form['fecha_estreno'], '%Y-%m-%d').date()
        new = Trailer(
            titulo=request.form['titulo'],
            youtube_url=request.form['youtube_url'],
            fecha_estreno=fecha
        )
        db.session.add(new)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', action='Agregar', trailer=None)

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    tr = Trailer.query.get_or_404(id)
    if request.method == 'POST':
        tr.titulo = request.form['titulo']
        tr.youtube_url = request.form['youtube_url']
        if request.form.get('fecha_estreno'):
            tr.fecha_estreno = datetime.strptime(request.form['fecha_estreno'], '%Y-%m-%d').date()
        db.session.commit()
        return redirect(url_for('detail', id=tr.id))
    return render_template('form.html', action='Editar', trailer=tr)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    tr = Trailer.query.get_or_404(id)
    db.session.delete(tr)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))