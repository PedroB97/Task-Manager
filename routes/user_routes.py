# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from forms import CreateUserForm, UserForm, UpdateUserPasswordForm
from models.models import User
from __init__ import db
import functools

user_bp = Blueprint('user_bp', __name__, url_prefix='/users')

# Decorador para exigir que o usuário seja administrador
def admin_required(f):
    @functools.wraps(f)  # Preserva os metadados da função original
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('project_bp.list_projects'))
        return f(*args, **kwargs)
    return decorated_function

# Esta linha é a chave: define o nome do endpoint explicitamente
# para que o Flask possa encontrá-lo quando chamado de outros blueprints
@user_bp.route('/')
@admin_required
def list_users():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@user_bp.route('/new', methods=['GET', 'POST'])
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Usuário {user.username} criado com sucesso!', 'success')
        return redirect(url_for('user_bp.list_users'))
    return render_template('users/new.html', form=form)

@user_bp.route('/<int:user_id>')
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/view.html', user=user)

@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(original_user=user, obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash(f'Usuário {user.username} atualizado com sucesso!', 'success')
        return redirect(url_for('user_bp.view_user', user_id=user.id))
    return render_template('users/edit.html', form=form, user=user)

@user_bp.route('/<int:user_id>/change-password', methods=['GET', 'POST'])
@admin_required
def change_user_password(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateUserPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(f'Senha do usuário {user.username} alterada com sucesso!', 'success')
        return redirect(url_for('user_bp.view_user', user_id=user.id))
    return render_template('users/change_password.html', form=form, user=user)

@user_bp.route('/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Não permitir deletar o próprio usuário
    if user.id == current_user.id:
        flash('Você não pode deletar sua própria conta!', 'danger')
        return redirect(url_for('user_bp.list_users'))
    
    # TODO: Verificar se o usuário tem tarefas atribuídas e lidar com isso
    # Por enquanto, vamos apenas deletar
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuário {username} deletado com sucesso!', 'success')
    return redirect(url_for('user_bp.list_users'))

