// HireFlow – Main JavaScript

document.addEventListener('DOMContentLoaded', () => {

  // ─── Auto-dismiss messages ───────────────────────────────────
  const alerts = document.querySelectorAll('.alert-auto-dismiss');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(100%)';
      setTimeout(() => alert.remove(), 300);
    }, 4000);
  });

  // ─── Animate elements on scroll ─────────────────────────────
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in-up');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));

  // ─── Skill tags input ────────────────────────────────────────
  const skillsInput = document.getElementById('id_skills_required') || document.getElementById('id_skills');
  if (skillsInput) {
    const preview = document.createElement('div');
    preview.className = 'mt-2 skills-preview';
    skillsInput.parentNode.insertBefore(preview, skillsInput.nextSibling);

    const renderTags = () => {
      const tags = skillsInput.value.split(',').filter(s => s.trim());
      preview.innerHTML = tags.map(t =>
        `<span class="skill-tag">${t.trim()}</span>`
      ).join('');
    };

    skillsInput.addEventListener('input', renderTags);
    renderTags();
  }

  // ─── Job search - live filter count ─────────────────────────
  const searchForm = document.getElementById('job-search-form');
  if (searchForm) {
    const inputs = searchForm.querySelectorAll('input, select');
    inputs.forEach(input => {
      input.addEventListener('change', () => {
        const count = [...inputs].filter(i => i.value).length;
        const badge = document.getElementById('filter-badge');
        if (badge) {
          badge.textContent = count > 0 ? count : '';
          badge.style.display = count > 0 ? 'inline' : 'none';
        }
      });
    });
  }

  // ─── Confirm delete dialogs ──────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', e => {
      if (!confirm(btn.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // ─── Status update AJAX (for pipeline) ──────────────────────
  document.querySelectorAll('.status-quick-update').forEach(select => {
    select.addEventListener('change', async (e) => {
      const appId = select.dataset.appId;
      const newStatus = select.value;
      const csrf = document.querySelector('[name=csrfmiddlewaretoken]');

      try {
        const resp = await fetch(`/api/applications/${appId}/update_status/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf ? csrf.value : '',
          },
          body: JSON.stringify({ status: newStatus }),
        });

        if (resp.ok) {
          const card = select.closest('.pipeline-card');
          if (card) {
            card.style.opacity = '0.5';
            card.style.transform = 'scale(0.95)';
            setTimeout(() => location.reload(), 500);
          }
          showToast('Status updated successfully!', 'success');
        } else {
          showToast('Failed to update status.', 'error');
        }
      } catch (err) {
        showToast('Network error. Please try again.', 'error');
      }
    });
  });

  // ─── Chart initialization (if Chart.js loaded) ──────────────
  if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
    Chart.defaults.font.family = 'Inter';

    // Pipeline donut chart
    const pipelineCanvas = document.getElementById('pipeline-chart');
    if (pipelineCanvas) {
      const data = JSON.parse(pipelineCanvas.dataset.values || '{}');
      new Chart(pipelineCanvas, {
        type: 'doughnut',
        data: {
          labels: Object.keys(data).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
          datasets: [{
            data: Object.values(data),
            backgroundColor: [
              'rgba(59,130,246,0.8)',
              'rgba(6,182,212,0.8)',
              'rgba(245,158,11,0.8)',
              'rgba(16,185,129,0.8)',
              'rgba(239,68,68,0.8)',
              'rgba(100,116,139,0.8)',
            ],
            borderWidth: 2,
            borderColor: '#0f0f1a',
          }],
        },
        options: {
          responsive: true,
          cutout: '65%',
          plugins: {
            legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true } },
          },
        },
      });
    }

    // Monthly trends line chart
    const trendsCanvas = document.getElementById('trends-chart');
    if (trendsCanvas) {
      const labels = JSON.parse(trendsCanvas.dataset.labels || '[]');
      const values = JSON.parse(trendsCanvas.dataset.values || '[]');
      new Chart(trendsCanvas, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Applications',
            data: values,
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99,102,241,0.1)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#6366f1',
            pointRadius: 4,
          }],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
            x: { grid: { color: 'rgba(255,255,255,0.05)' } },
          },
        },
      });
    }

    // Jobs by category bar chart
    const categoryCanvas = document.getElementById('category-chart');
    if (categoryCanvas) {
      const labels = JSON.parse(categoryCanvas.dataset.labels || '[]');
      const values = JSON.parse(categoryCanvas.dataset.values || '[]');
      new Chart(categoryCanvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Jobs',
            data: values,
            backgroundColor: 'rgba(99,102,241,0.7)',
            borderRadius: 6,
            borderSkipped: false,
          }],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
            x: { grid: { display: false } },
          },
        },
      });
    }
  }
});

// ─── Toast notification ──────────────────────────────────────────────────────
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container') || createToastContainer();
  const toast = document.createElement('div');
  const icon = type === 'success' ? 'bi-check-circle-fill' : type === 'error' ? 'bi-x-circle-fill' : 'bi-info-circle-fill';
  const color = type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#6366f1';

  toast.className = 'alert-glass p-3 mb-2 alert-auto-dismiss';
  toast.style.cssText = `border-left: 3px solid ${color}; transition: all 0.3s ease;`;
  toast.innerHTML = `
    <div class="d-flex align-items-center gap-2">
      <i class="bi ${icon}" style="color:${color}"></i>
      <span style="color: #f1f5f9; font-size: 0.875rem;">${message}</span>
    </div>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.className = 'messages-container';
  document.body.appendChild(container);
  return container;
}
