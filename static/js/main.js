// Funcionalidades principais do sistema
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar Sortable.js para o quadro Kanban
    const taskLists = document.querySelectorAll('.task-list');
    
    taskLists.forEach(taskList => {
        new Sortable(taskList, {
            group: 'tasks',
            animation: 150,
            ghostClass: 'task-card-ghost',
            onEnd: function(evt) {
                const taskId = evt.item.getAttribute('data-task-id');
                const newStatus = evt.to.getAttribute('data-status');
                
                // Atualizar status da tarefa via AJAX
                if (taskId && newStatus) {
                    const formData = new FormData();
                    formData.append('status', newStatus);
                    
                    fetch(`/tasks/${taskId}/status`, {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (!data.success) {
                            console.error('Erro ao atualizar status da tarefa');
                            // Reverter a mudança visual se houver erro
                            location.reload();
                        }
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                        location.reload();
                    });
                }
            }
        });
    });
    
    // Inicializar gráficos no dashboard se estiver na página correta
    const chartContainer = document.getElementById('tasks-chart');
    if (chartContainer) {
        const projectId = chartContainer.getAttribute('data-project-id');
        
        // Buscar dados para o gráfico
        fetch(`/api/projects/${projectId}/tasks/stats`)
            .then(response => response.json())
            .then(data => {
                const ctx = chartContainer.getContext('2d');
                new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            data: data.data,
                            backgroundColor: [
                                '#0d6efd',  // Azul para "A Fazer"
                                '#fd7e14',  // Laranja para "Em Andamento"
                                '#198754'   // Verde para "Finalizadas"
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            })
            .catch(error => console.error('Erro ao carregar dados do gráfico:', error));
    }
    
    // Manipulação de modais para criação/edição de tarefas
    const taskModals = document.querySelectorAll('.task-modal');
    taskModals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = modal.querySelector('input[type="text"]');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
    
    // Preview de anexos antes do upload
    const fileInput = document.getElementById('attachment-file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const filePreview = document.getElementById('file-preview');
            if (filePreview) {
                if (this.files.length > 0) {
                    const file = this.files[0];
                    const fileSize = (file.size / 1024 / 1024).toFixed(2); // em MB
                    
                    filePreview.innerHTML = `
                        <div class="alert alert-info">
                            <strong>${file.name}</strong> (${fileSize} MB)
                        </div>
                    `;
                    
                    // Verificar tamanho do arquivo
                    if (file.size > 10 * 1024 * 1024) { // 10MB
                        filePreview.innerHTML += `
                            <div class="alert alert-danger">
                                O arquivo excede o limite de 10MB.
                            </div>
                        `;
                    }
                } else {
                    filePreview.innerHTML = '';
                }
            }
        });
    }
});
