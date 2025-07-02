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
        # Verificar se este é o primeiro usuário do sistema
        user_count = User.query.count()
        is_first_user = user_count == 0
        
        # Criar o novo usuário
        user = User(
            username=form.username.data, 
            email=form.email.data,
            is_admin=is_first_user  # Primeiro usuário automaticamente vira admin
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        if is_first_user:
            flash(f"Parabéns! Você é o primeiro usuário e foi automaticamente promovido a administrador. Bem-vindo, {user.username}!", "success")
        else:
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
            
            # Mensagem de boas-vindas diferenciada para admin
            if user.is_admin:
                flash(f"Bem-vindo de volta, {user.username}! Você tem privilégios de administrador.", "success")
            else:
                flash(f"Bem-vindo de volta, {user.username}!", "success")
            
            return redirect(next_page)
        flash("Email ou senha inválidos.", "error")
    
    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f"Até logo, {username}! Você foi desconectado.", "info")
    return redirect(url_for("auth_bp.login"))

# Importar url_parse para validação de URL
from urllib.parse import urlparse as url_parse

