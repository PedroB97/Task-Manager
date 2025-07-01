# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from src import db
from src.models.models import User
from src.forms import LoginForm, RegistrationForm

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
        # if existing_user_username:
        #     flash("Nome de usuário já existe. Por favor, escolha outro.", "danger")
        #     return render_template("register.html", title="Registrar", form=form)
        # if existing_user_email:
        #     flash("Endereço de email já cadastrado. Por favor, use outro.", "danger")
        #     return render_template("register.html", title="Registrar", form=form)

        # Criar novo usuário
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Sua conta foi criada com sucesso! Você já pode fazer login.", "success")
        return redirect(url_for("auth_bp.login"))
    return render_template("register.html", title="Registrar", form=form)

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
            flash("Login realizado com sucesso!", "success")
            return redirect(next_page) if next_page else redirect(url_for("project_bp.list_projects"))
        else:
            flash("Login falhou. Verifique seu email e senha.", "danger")
    return render_template("login.html", title="Login", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth_bp.login"))

# --- ROTA TEMPORÁRIA PARA CRIAR O PRIMEIRO ADMIN ---
# REMOVA ESTA ROTA APÓS CRIAR SEU PRIMEIRO USUÁRIO ADMINISTRADOR!
def create_first_admin():
    # Verifica se já existe algum usuário administrador
    if User.query.filter_by(is_admin=True).first():
        flash('Já existe um administrador. Esta rota é apenas para configuração inicial.', 'info')
        return redirect(url_for('auth_bp.login')) # Redireciona para o login se já houver admin

    # Se não houver admin, cria um
    admin_user = User(username='admin', email='admin@example.com', is_admin=True)
    admin_user.set_password('adminpassword') # MUDE PARA UMA SENHA FORTE E SEGURA!
    db.session.add(admin_user)
    db.session.commit()
    flash('Primeiro usuário administrador criado! Usuário: admin, Senha: adminpassword', 'success')
    return redirect(url_for('auth_bp.login'))

# REGISTRO MANUAL DA ROTA (ADICIONE ESTAS DUAS LINHAS NO FINAL DO ARQUIVO)
auth_bp.add_url_rule('/create_first_admin', view_func=create_first_admin)
