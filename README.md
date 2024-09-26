# Forjando_el_Artefacto_Supremo
Proyecto final de la materia Programacion Avanzada
Las paqueterias que se utilizan son 
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename


Comandos para ejecutarlo:
cd  proyecto_quadra
source .venv/bin/activate
code app.py
Dentro de visual estudio abrir una nueva terminal
cd proyecto_quadra
source .venv/bin/activate
python app.py
