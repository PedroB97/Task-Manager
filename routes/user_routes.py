# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from src.forms import CreateUserForm, UserForm, UpdateUserPasswordForm
from src.models.models import User
from src import db

user_bp = Blueprint('user_bp', __name__, url_prefix='/users')

# Decorador para exigir que o usuário seja administrador
def admin_required(f):
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('project_bp.list_projects'))
        return f(*args, **kwargs)

    # Esta linha é a chave: define o nome do endpoint explicitamente
    # para o nome da função original.
    wrapper.__name__ = f.__name__
    wrapper.__module__ = f.__module__
    wrapper.__doc__ = f.__doc__
    wrapper.__qualname__ = f.__qualname__ # Adicionado para compatibilidade

    return wrapper

@user_bp.route('/')
@admin_required
def list_users():
    users = User.query.all()
    return render_template('users/list_users.html', users=users, title="Gerenciar Usuários")

@user_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('user_bp.list_users'))
    return render_template('users/create_user.html', form=form, title="Criar Novo Usuário")

@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(original_username=user.username, original_email=user.email)
    password_form = UpdateUserPasswordForm()

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('user_bp.list_users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.is_admin.data = user.is_admin

    return render_template('users/edit_user.html', form=form, password_form=password_form, user=user, title=f"Editar Usuário: {user.username}")

@user_bp.route('/<int:user_id>/change_password', methods=['POST'])
@admin_required
def change_user_password(user_id):
    user = User.query.get_or_404(user_id)
    password_form = UpdateUserPasswordForm()
    if password_form.validate_on_submit():
        user.set_password(password_form.password.data)
        db.session.commit()
        flash('Senha do usuário alterada com sucesso!', 'success')
    else:
        for field, errors in password_form.errors.items():
            for error in errors:
                flash(f'Erro na senha: {error}', 'danger')
    return redirect(url_for('user_bp.edit_user', user_id=user.id))


@user_bp.route('/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Você não pode excluir seu próprio usuário!', 'danger')
        return redirect(url_for('user_bp.list_users'))

    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('user_bp.list_users'))
