# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from .. import db
from ..models.models import Project, Task, User # Import User
from ..forms import TaskForm # Importar o novo TaskForm

# Definir o Blueprint para tarefas
task_bp = Blueprint("task_bp", __name__, template_folder="../templates/tasks")

# Rota para criar uma nova tarefa DENTRO de um projeto específico
@task_bp.route("/project/<int:project_id>/tasks/new", methods=["GET", "POST"])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    form = TaskForm() # Usar o novo TaskForm
    
    # Se o formulário for válido ao submeter (POST)
    if form.validate_on_submit():
        # Criar nova instância da Tarefa
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            due_date=form.due_date.data,
            project_id=project.id,
            # Atribuir o usuário selecionado no formulário
            assigned_user=form.assigned_user.data # QuerySelectField retorna o objeto User
        )
        db.session.add(new_task)
        db.session.commit()
        flash("Tarefa criada com sucesso!", "success")
        # Redirecionar para a visualização do projeto
        return redirect(url_for("project_bp.view_project", project_id=project.id))
        
    # Se for GET ou o formulário for inválido, renderizar o template de criação
    # Passar o formulário e o projeto para o template
    return render_template("new_task.html", title="Nova Tarefa", form=form, project=project)

# Rota para editar uma tarefa existente
@task_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project # Obter o projeto associado à tarefa
    # Pré-popular o formulário com os dados da tarefa existente
    form = TaskForm(obj=task)
    
    # Se o formulário for válido ao submeter (POST)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.status = form.status.data
        task.due_date = form.due_date.data
        # Atualizar o usuário atribuído
        task.assigned_user = form.assigned_user.data
        db.session.commit()
        flash("Tarefa atualizada com sucesso!", "success")
        # Redirecionar para a visualização do projeto
        return redirect(url_for("project_bp.view_project", project_id=project.id))
        
    # Se for GET ou o formulário for inválido, renderizar o template de edição
    # Passar o formulário, a tarefa e o projeto para o template
    return render_template("edit_task.html", title="Editar Tarefa", form=form, task=task, project=project)

# Rota para excluir uma tarefa
@task_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id # Guardar o ID do projeto antes de excluir
    db.session.delete(task)
    db.session.commit()
    flash("Tarefa excluída com sucesso!", "success")
    return redirect(url_for("project_bp.view_project", project_id=project_id))

# Rota para atualizar o status de uma tarefa (ex: via drag-and-drop)
@task_bp.route("/tasks/<int:task_id>/update_status", methods=["POST"])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.json.get("status")
    new_position = request.json.get("position")

    if new_status not in ["a_fazer", "em_andamento", "finalizada"]:
        return abort(400, "Status inválido")

    task.status = new_status
    if new_position is not None:
        try:
            task.position = int(new_position)
        except ValueError:
            pass # Ignorar se a posição não for um inteiro válido
            
    db.session.commit()
    return {"message": "Status da tarefa atualizado com sucesso!"}

