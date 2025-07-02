# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from __init__ import db
from models.models import Project, Task, User  # Import User
from forms import TaskForm  # Importar o novo TaskForm

# Definir o Blueprint para tarefas
task_bp = Blueprint("task_bp", __name__, template_folder="../templates/tasks")

# Rota para criar uma nova tarefa DENTRO de um projeto específico
@task_bp.route("/projects/<int:project_id>/tasks/new", methods=["GET", "POST"])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    form = TaskForm()  # Usar o novo TaskForm
    
    # Se o formulário for válido ao submeter (POST)
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            due_date=form.due_date.data,
            project_id=project_id,
            assigned_user_id=form.assigned_user.data.id if form.assigned_user.data else None
        )
        db.session.add(task)
        db.session.commit()
        flash("Tarefa criada com sucesso!", "success")
        return redirect(url_for("project_bp.view_project", project_id=project_id))
    
    return render_template("tasks/new.html", form=form, project=project)

# Rota para editar uma tarefa existente
@task_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)  # Pré-preencher o formulário com dados da tarefa
    
    # Pré-selecionar o usuário atribuído se existir
    if task.assigned_user_id:
        form.assigned_user.data = User.query.get(task.assigned_user_id)
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.status = form.status.data
        task.due_date = form.due_date.data
        task.assigned_user_id = form.assigned_user.data.id if form.assigned_user.data else None
        db.session.commit()
        flash("Tarefa atualizada com sucesso!", "success")
        return redirect(url_for("project_bp.view_project", project_id=task.project_id))
    
    return render_template("tasks/edit.html", form=form, task=task)

# Rota para deletar uma tarefa
@task_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    flash("Tarefa deletada com sucesso!", "success")
    return redirect(url_for("project_bp.view_project", project_id=project_id))

# Rota para visualizar uma tarefa específica
@task_bp.route("/tasks/<int:task_id>")
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("tasks/view.html", task=task)

