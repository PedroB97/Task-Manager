from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Project, Task
from __init__ import db
from datetime import datetime

project_bp = Blueprint('project_bp', __name__)

@project_bp.route('/projects')
def list_projects():
    projects = Project.query.all()
    return render_template('projects/list.html', projects=projects)

@project_bp.route('/projects/new', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('O nome do projeto é obrigatório!', 'error')
            return render_template('projects/new.html')
        
        project = Project(name=name, description=description)
        db.session.add(project)
        db.session.commit()
        
        flash('Projeto criado com sucesso!', 'success')
        return redirect(url_for('project_bp.view_project', project_id=project.id))
    
    return render_template('projects/new.html')

@project_bp.route('/projects/<int:project_id>')
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    tasks_a_fazer = Task.query.filter_by(project_id=project_id, status='a_fazer')
    tasks_em_andamento = Task.query.filter_by(project_id=project_id, status='em_andamento')
    tasks_finalizadas = Task.query.filter_by(project_id=project_id, status='finalizadas')
    
    return render_template('projects/view.html',
                         project=project,
                         tasks_a_fazer=tasks_a_fazer,
                         tasks_em_andamento=tasks_em_andamento,
                         tasks_finalizadas=tasks_finalizadas)

@project_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('O nome do projeto é obrigatório!', 'error')
            return render_template('projects/edit.html', project=project)
        
        project.name = name
        project.description = description
        db.session.commit()
        
        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('project_bp.view_project', project_id=project.id))
    
    return render_template('projects/edit.html', project=project)

@project_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Deletar todas as tarefas associadas primeiro
    Task.query.filter_by(project_id=project_id).delete()
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Projeto deletado com sucesso!', 'success')
    return redirect(url_for('project_bp.list_projects'))

