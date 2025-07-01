# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db
from models.models import User
from forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth_bp", __name__, template_folder="../templates/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("project_bp.list_projects"))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar se username ou email já existem
        # Estas validações já estão no forms.py, então podem ser removidas aqui para evitar duplicação
        # e usar as mensagens de erro do WTForms.
        
        # existing_user_username = User.query.filter_by(username=form.username.data).first()
        # existing_user_email = User.query.filter_by(email=form.email.data).first()
        # 
        # if existing_user_username:
        #     flash("Nome de usuário já existe!", "error")
        #     return render_template("auth/register.html", form=form)
        # 
        # if existing_user_email:
        #     flash("Email já está em uso!", "error")
        #     return render_template("auth/register.html", form=form)
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registro realizado com sucesso! Você pode fazer login agora.", "success")
        return redirect(url_for("auth_bp.login"))
    return render_template("auth/register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("project_bp.list_projects"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            if not next_page or url_parse(next_page).netloc != "":
                next_page = url_for("project_bp.list_projects")
            return redirect(next_page)
        flash("Email ou senha inválidos.", "error")
    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("auth_bp.login"))

# Importar url_parse para validação de URL
from urllib.parse import urlparse as url_parse

