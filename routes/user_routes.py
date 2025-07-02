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
            flash('Você não tem permissão para acessar esta página. Apenas administradores podem gerenciar usuários.', 'danger')
            return redirect(url_for('project_bp.list_projects'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/')
@admin_required
def list_users():
    users = User.query.all()
    total_users = len(users)
    admin_users = len([u for u in users if u.is_admin])
    regular_users = total_users - admin_users
    
    return render_template('users/list.html', 
                         users=users, 
                         total_users=total_users,
                         admin_users=admin_users,
                         regular_users=regular_users)

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
        
        user_type = "administrador" if user.is_admin else "usuário regular"
        flash(f'{user_type.capitalize()} {user.username} criado com sucesso!', 'success')
        return redirect(url_for('user_bp.list_users'))
    
    return render_template('users/new.html', form=form)

@user_bp.route('/<int:user_id>')
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    # Contar tarefas atribuídas ao usuário
    task_count = len(user.assigned_tasks) if hasattr(user, 'assigned_tasks') else 0
    return render_template('users/view.html', user=user, task_count=task_count)

@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(original_user=user, obj=user)
    
    if form.validate_on_submit():
        # Verificar se está tentando remover privilégios de admin do último admin
        if user.is_admin and not form.is_admin.data:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                flash('Erro: Não é possível remover privilégios de administrador do último administrador do sistema!', 'danger')
                return render_template('users/edit.html', form=form, user=user)
        
        old_admin_status = user.is_admin
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        
        db.session.commit()
        
        # Mensagem personalizada baseada na mudança de status
        if not old_admin_status and user.is_admin:
            flash(f'Usuário {user.username} foi promovido a administrador!', 'success')
        elif old_admin_status and not user.is_admin:
            flash(f'Privilégios de administrador removidos do usuário {user.username}.', 'warning')
        else:
            flash(f'Usuário {user.username} atualizado com sucesso!', 'success')
        
        return redirect(url_for('user_bp.view_user', user_id=user.id))
    
    return render_template('users/edit.html', form=form, user=user)

@user_bp.route('/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Não permitir alterar o próprio status de admin
    if user.id == current_user.id:
        flash('Você não pode alterar seus próprios privilégios de administrador!', 'danger')
        return redirect(url_for('user_bp.list_users'))
    
    # Se está tentando remover admin, verificar se não é o último
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Erro: Não é possível remover privilégios do último administrador do sistema!', 'danger')
            return redirect(url_for('user_bp.list_users'))
        
        user.is_admin = False
        flash(f'Privilégios de administrador removidos do usuário {user.username}.', 'warning')
    else:
        user.is_admin = True
        flash(f'Usuário {user.username} foi promovido a administrador!', 'success')
    
    db.session.commit()
    return redirect(url_for('user_bp.list_users'))

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
    
    # Não permitir deletar o último admin
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Erro: Não é possível deletar o último administrador do sistema!', 'danger')
            return redirect(url_for('user_bp.list_users'))
    
    # Verificar se o usuário tem tarefas atribuídas
    task_count = len(user.assigned_tasks) if hasattr(user, 'assigned_tasks') else 0
    if task_count > 0:
        flash(f'Não é possível deletar o usuário {user.username} pois ele tem {task_count} tarefa(s) atribuída(s). Reatribua as tarefas primeiro.', 'danger')
        return redirect(url_for('user_bp.view_user', user_id=user.id))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuário {username} deletado com sucesso!', 'success')
    return redirect(url_for('user_bp.list_users'))

