"""
Estilos CSS customizados para o Fitness Metrics Dashboard
"""
CUSTOM_CSS = """
<style>
/* ========== ANIMAÇÕES E TRANSIÇÕES ========== */
@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes progressFill {
    from {
        width: 0;
    }
    to {
        width: var(--progress-width);
    }
}

@keyframes pulse {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4);
    }
    50% {
        box-shadow: 0 0 0 8px rgba(102, 126, 234, 0);
    }
}

/* ========== CARDS COM HIERARQUIA VISUAL ========== */
.card {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    animation: slideInUp 0.5s ease-out;
    border: none !important;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.12), 0 8px 16px rgba(0,0,0,0.08) !important;
}

/* Cards de status com destaque */
.status-card {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.status-card:hover {
    transform: scale(1.03);
    animation: pulse 2s infinite;
}

.status-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.1) 100%);
    opacity: 0;
    transition: opacity 0.3s;
}

.status-card:hover::before {
    opacity: 1;
}

/* ========== PROGRESS BARS ANIMADAS COM GRADIENTE ========== */
.progress {
    border-radius: 12px;
    background: linear-gradient(90deg, #e9ecef 0%, #f8f9fa 100%);
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
    height: 12px !important;
    overflow: visible;
    position: relative;
}

.progress-bar {
    border-radius: 12px;
    transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

/* Gradientes para diferentes cores de progresso */
.progress-bar.bg-success {
    background: linear-gradient(90deg, #28a745 0%, #20c997 50%, #28a745 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmer 3s infinite;
    box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.progress-bar.bg-primary {
    background: linear-gradient(90deg, #007bff 0%, #0056b3 50%, #007bff 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmer 3s infinite;
    box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}

.progress-bar.bg-warning {
    background: linear-gradient(90deg, #ffc107 0%, #ffb300 50%, #ffc107 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmer 3s infinite;
    box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
}

.progress-bar.bg-info {
    background: linear-gradient(90deg, #17a2b8 0%, #138496 50%, #17a2b8 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmer 3s infinite;
    box-shadow: 0 2px 8px rgba(23, 162, 184, 0.3);
}

.progress-bar.bg-danger {
    background: linear-gradient(90deg, #dc3545 0%, #c82333 50%, #dc3545 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmer 3s infinite;
    box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

@keyframes shimmer {
    0% {
        background-position: 200% 0;
    }
    100% {
        background-position: -200% 0;
    }
}

/* Indicador de porcentagem na barra */
.progress-bar::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(to bottom, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 100%);
    border-radius: 12px;
}

/* ========== TABELAS MODERNAS ========== */
.table {
    font-size: 0.9rem;
    border-collapse: separate;
    border-spacing: 0;
}

.table th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
    border: none;
    padding: 0.75rem 0.5rem;
    text-align: center;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    position: relative;
}

.table th::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
}

.table td {
    vertical-align: middle;
    padding: 0.6rem 0.5rem;
    border-bottom: 1px solid #e9ecef;
    font-size: 0.85rem;
    transition: background-color 0.2s ease;
}

.table tbody tr:nth-of-type(odd) {
    background-color: rgba(0, 123, 255, 0.02);
}

.table tbody tr:hover {
    background: linear-gradient(90deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
    transform: scale(1.01);
    transition: all 0.2s ease;
}

/* ========== SEPARADORES VISUAIS ========== */
hr {
    border: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, #e9ecef 20%, #e9ecef 80%, transparent);
    margin: 3rem 0;
    position: relative;
}

hr::after {
    content: '';
    position: absolute;
    top: -1px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 5px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 3px;
}

/* ========== HEADERS DE SEÇÃO ========== */
.section-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
    display: inline-block;
}

/* ========== TIPOGRAFIA COM HIERARQUIA ========== */
h1 {
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}

h2 {
    font-weight: 700 !important;
    letter-spacing: -0.3px;
    line-height: 1.3;
}

h3, h4 {
    font-weight: 600 !important;
    letter-spacing: -0.2px;
}

h5, h6 {
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.85rem;
}

/* ========== ACCORDION MODERNO ========== */
.accordion-button {
    border-radius: 10px !important;
    font-weight: 600;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.accordion-button:not(.collapsed) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.accordion-button:hover {
    transform: translateX(4px);
}

/* ========== ESPAÇAMENTO COM HIERARQUIA ========== */
.mb-5 {
    margin-bottom: 3rem !important;
}

.mb-4 {
    margin-bottom: 2rem !important;
}

.mb-3 {
    margin-bottom: 1.5rem !important;
}

.py-4 {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

.py-3 {
    padding-top: 1.5rem !important;
    padding-bottom: 1.5rem !important;
}

/* ========== BADGES MODERNOS ========== */
.badge {
    font-weight: 600;
    padding: 0.4em 0.8em;
    border-radius: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: all 0.2s ease;
}

.badge:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* ========== EFEITOS DE FOCO E INTERAÇÃO ========== */
*:focus {
    outline: 2px solid rgba(102, 126, 234, 0.5);
    outline-offset: 2px;
}

/* ========== LOADING E SKELETON ========== */
@keyframes skeleton-loading {
    0% {
        background-position: 200% 0;
    }
    100% {
        background-position: -200% 0;
    }
}

.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
}

/* ========== MODO ESCURO ========== */
body.dark-mode {
    background-color: #1a1a1a !important;
    color: #e0e0e0 !important;
}

body.dark-mode .card {
    background-color: #2d2d2d !important;
    color: #e0e0e0 !important;
}

body.dark-mode .bg-light {
    background-color: #2d2d2d !important;
}

body.dark-mode .table {
    background-color: #2d2d2d !important;
    color: #e0e0e0 !important;
}

body.dark-mode .table tbody tr:hover {
    background: linear-gradient(90deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
}

body.dark-mode .text-muted {
    color: #999 !important;
}

/* Botão de toggle modo escuro */
.dark-mode-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    border-radius: 50px;
    padding: 8px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
    font-weight: 600;
    font-size: 0.9rem;
}

.dark-mode-toggle:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

/* ========== ESTILOS MODO ESCURO ========== */
/* Background e cores base */
#app-container[style*="background-color: rgb(36, 36, 40)"],
#app-container[style*="backgroundColor: #242428"] {
    background-color: #0d1117 !important;
}

/* Cards - estilo Strava dark */
#app-container[style*="background-color: rgb(36, 36, 40)"] .card,
#app-container[style*="backgroundColor: #242428"] .card {
    background-color: #2D2D31 !important;
    color: #FFFFFF !important;
    border: 1px solid #404044 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .card:hover,
#app-container[style*="backgroundColor: #242428"] .card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    border-color: #505054 !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .card-header,
#app-container[style*="backgroundColor: #242428"] .card-header {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    border-bottom: 1px solid #30363d !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .card-body,
#app-container[style*="backgroundColor: #242428"] .card-body {
    background-color: #2D2D31 !important;
    color: #c9d1d9 !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .bg-light,
#app-container[style*="backgroundColor: #242428"] .bg-light {
    background-color: #2D2D31 !important;
}

/* Todos os títulos e textos */
#app-container[style*="background-color: rgb(36, 36, 40)"] h1,
#app-container[style*="backgroundColor: #242428"] h1,
#app-container[style*="background-color: rgb(36, 36, 40)"] h2,
#app-container[style*="backgroundColor: #242428"] h2,
#app-container[style*="background-color: rgb(36, 36, 40)"] h3,
#app-container[style*="backgroundColor: #242428"] h3,
#app-container[style*="background-color: rgb(36, 36, 40)"] h4,
#app-container[style*="backgroundColor: #242428"] h4,
#app-container[style*="background-color: rgb(36, 36, 40)"] h5,
#app-container[style*="backgroundColor: #242428"] h5,
#app-container[style*="background-color: rgb(36, 36, 40)"] h6,
#app-container[style*="backgroundColor: #242428"] h6,
#app-container[style*="background-color: rgb(36, 36, 40)"] p,
#app-container[style*="backgroundColor: #242428"] p,
#app-container[style*="background-color: rgb(36, 36, 40)"] span,
#app-container[style*="backgroundColor: #242428"] span,
#app-container[style*="background-color: rgb(36, 36, 40)"] div,
#app-container[style*="backgroundColor: #242428"] div,
#app-container[style*="background-color: rgb(36, 36, 40)"] label,
#app-container[style*="backgroundColor: #242428"] label,
#app-container[style*="background-color: rgb(36, 36, 40)"] strong,
#app-container[style*="backgroundColor: #242428"] strong,
#app-container[style*="background-color: rgb(36, 36, 40)"] b,
#app-container[style*="backgroundColor: #242428"] b {
    color: #c9d1d9 !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .text-muted,
#app-container[style*="backgroundColor: #242428"] .text-muted {
    color: #8b949e !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .text-secondary,
#app-container[style*="backgroundColor: #242428"] .text-secondary {
    color: #8b949e !important;
}

/* Forçar cor clara em elementos específicos */
#app-container[style*="background-color: rgb(36, 36, 40)"] [style*="color: rgb(33, 37, 41)"],
#app-container[style*="backgroundColor: #242428"] [style*="color: rgb(33, 37, 41)"],
#app-container[style*="background-color: rgb(36, 36, 40)"] [style*="color: #212529"],
#app-container[style*="backgroundColor: #242428"] [style*="color: #212529"] {
    color: #c9d1d9 !important;
}

/* Tabelas */
#app-container[style*="background-color: rgb(36, 36, 40)"] .table,
#app-container[style*="backgroundColor: #242428"] .table {
    background-color: transparent !important;
    color: #c9d1d9 !important;
    border-color: #30363d !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .table thead th,
#app-container[style*="backgroundColor: #242428"] .table thead th {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    border-color: #30363d !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .table tbody td,
#app-container[style*="backgroundColor: #242428"] .table tbody td {
    color: #c9d1d9 !important;
    border-color: #30363d !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .table tbody tr:hover,
#app-container[style*="backgroundColor: #242428"] .table tbody tr:hover {
    background-color: rgba(56, 139, 253, 0.1) !important;
}

/* Badges - cores vibrantes Strava */
#app-container[style*="background-color: rgb(36, 36, 40)"] .badge,
#app-container[style*="backgroundColor: #242428"] .badge {
    background-color: #38383C !important;
    color: #6BB6FF !important;
    border: 1px solid #404044 !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .badge-success,
#app-container[style*="backgroundColor: #242428"] .badge-success {
    background-color: #2EA043 !important;
    color: white !important;
    border-color: #3FB950 !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .badge-warning,
#app-container[style*="backgroundColor: #242428"] .badge-warning {
    background-color: #FFA500 !important;
    color: white !important;
    border-color: #FFB84D !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .badge-danger,
#app-container[style*="backgroundColor: #242428"] .badge-danger {
    background-color: #F85149 !important;
    color: white !important;
    border-color: #FF6B6B !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .badge-primary,
#app-container[style*="backgroundColor: #242428"] .badge-primary {
    background-color: #FC5200 !important;
    color: white !important;
    border-color: #FF6B35 !important;
}

/* Progress bars - estilo Strava */
#app-container[style*="background-color: rgb(36, 36, 40)"] .progress,
#app-container[style*="backgroundColor: #242428"] .progress {
    background-color: #38383C !important;
    border-radius: 8px !important;
    height: 12px !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3) !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .progress-bar,
#app-container[style*="backgroundColor: #242428"] .progress-bar {
    background: linear-gradient(135deg, #FC5200 0%, #FF6B35 100%) !important;
    box-shadow: 0 2px 4px rgba(252, 82, 0, 0.3) !important;
    transition: width 0.6s ease !important;
}

/* Botões no modo escuro */
#app-container[style*="background-color: rgb(36, 36, 40)"] .btn-primary,
#app-container[style*="backgroundColor: #242428"] .btn-primary {
    background: linear-gradient(135deg, #FC5200 0%, #FF6B35 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(252, 82, 0, 0.3) !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .btn-primary:hover,
#app-container[style*="backgroundColor: #242428"] .btn-primary:hover {
    box-shadow: 0 6px 16px rgba(252, 82, 0, 0.5) !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .btn-success,
#app-container[style*="backgroundColor: #242428"] .btn-success {
    background: linear-gradient(135deg, #2EA043 0%, #3FB950 100%) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(46, 160, 67, 0.3) !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .btn-success:hover,
#app-container[style*="backgroundColor: #242428"] .btn-success:hover {
    box-shadow: 0 6px 16px rgba(46, 160, 67, 0.5) !important;
}

/* Abas */
#app-container[style*="background-color: rgb(36, 36, 40)"] .nav-tabs,
#app-container[style*="backgroundColor: #242428"] .nav-tabs {
    border-bottom-color: #30363d !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .nav-tabs .nav-link,
#app-container[style*="backgroundColor: #242428"] .nav-tabs .nav-link {
    color: #A0A0A5 !important;
    border-color: transparent !important;
    background-color: transparent !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .nav-tabs .nav-link.active,
#app-container[style*="backgroundColor: #242428"] .nav-tabs .nav-link.active {
    background-color: #2D2D31 !important;
    color: #FFFFFF !important;
    border-color: #404044 #404044 #2D2D31 !important;
    font-weight: 600 !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .nav-tabs .nav-link:hover,
#app-container[style*="backgroundColor: #242428"] .nav-tabs .nav-link:hover {
    color: #FFFFFF !important;
    border-color: #404044 #404044 transparent !important;
    background-color: rgba(45, 45, 49, 0.5) !important;
}

/* Alertas - cores vibrantes Strava */
#app-container[style*="background-color: rgb(36, 36, 40)"] .alert,
#app-container[style*="backgroundColor: #242428"] .alert {
    background-color: #2D2D31 !important;
    border: 1px solid #404044 !important;
    color: #FFFFFF !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .alert-info,
#app-container[style*="backgroundColor: #242428"] .alert-info {
    background-color: rgba(56, 139, 253, 0.15) !important;
    border-color: #388bfd !important;
    color: #6BB6FF !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .alert-success,
#app-container[style*="backgroundColor: #242428"] .alert-success {
    background-color: rgba(46, 160, 67, 0.15) !important;
    border-color: #2ea043 !important;
    color: #5DD879 !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .alert-warning,
#app-container[style*="backgroundColor: #242428"] .alert-warning {
    background-color: rgba(255, 165, 0, 0.15) !important;
    border-color: #FFA500 !important;
    color: #FFB84D !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] .alert-danger,
#app-container[style*="backgroundColor: #242428"] .alert-danger {
    background-color: rgba(248, 81, 73, 0.15) !important;
    border-color: #f85149 !important;
    color: #FF6B6B !important;
}

/* HR separador */
#app-container[style*="background-color: rgb(36, 36, 40)"] hr,
#app-container[style*="backgroundColor: #242428"] hr {
    border-color: #404044 !important;
    opacity: 1 !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] hr::after,
#app-container[style*="backgroundColor: #242428"] hr::after {
    background: linear-gradient(90deg, #FC5200, #FF6B35) !important;
}

/* Botão modo escuro quando ativo - laranja Strava */
#app-container[style*="background-color: rgb(36, 36, 40)"] .dark-mode-toggle,
#app-container[style*="backgroundColor: #242428"] .dark-mode-toggle {
    background: linear-gradient(135deg, #FC5200 0%, #FF6B35 100%) !important;
    box-shadow: 0 4px 16px rgba(252, 82, 0, 0.4) !important;
}

/* Inputs e forms */
#app-container[style*="background-color: rgb(36, 36, 40)"] input,
#app-container[style*="backgroundColor: #242428"] input,
#app-container[style*="background-color: rgb(36, 36, 40)"] select,
#app-container[style*="backgroundColor: #242428"] select,
#app-container[style*="background-color: rgb(36, 36, 40)"] textarea,
#app-container[style*="backgroundColor: #242428"] textarea {
    background-color: #1A1A1E !important;
    color: #FFFFFF !important;
    border-color: #404044 !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] input:focus,
#app-container[style*="backgroundColor: #242428"] input:focus,
#app-container[style*="background-color: rgb(36, 36, 40)"] select:focus,
#app-container[style*="backgroundColor: #242428"] select:focus,
#app-container[style*="background-color: rgb(36, 36, 40)"] textarea:focus,
#app-container[style*="backgroundColor: #242428"] textarea:focus {
    border-color: #FC5200 !important;
    box-shadow: 0 0 0 0.2rem rgba(252, 82, 0, 0.25) !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] input::placeholder,
#app-container[style*="backgroundColor: #242428"] input::placeholder {
    color: #8b949e !important;
}

/* Scrollbar customizada modo escuro */
#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar {
    width: 12px !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar-track,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar-track {
    background: #1A1A1E !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar-thumb,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar-thumb {
    background: #404044 !important;
    border-radius: 6px !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar-thumb:hover,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar-thumb:hover {
    background: #505054 !important;
}

/* Links no modo escuro */
#app-container[style*="background-color: rgb(36, 36, 40)"] a,
#app-container[style*="backgroundColor: #242428"] a {
    color: #6BB6FF !important;
    transition: color 0.2s ease !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] a:hover,
#app-container[style*="backgroundColor: #242428"] a:hover {
    color: #FC5200 !important;
}

/* Scrollbar customizada modo escuro */
#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar {
    width: 12px !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar-track,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar-track {
    background: #1A1A1E !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar-thumb,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar-thumb {
    background: #404044 !important;
    border-radius: 6px !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar-thumb:hover,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar-thumb:hover {
    background: #505054 !important;
}

/* Links no modo escuro */
#app-container[style*="background-color: rgb(36, 36, 40)"] a,
#app-container[style*="backgroundColor: #242428"] a {
    color: #6BB6FF !important;
    text-decoration: none !important;
    transition: color 0.2s ease !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] a:hover,
#app-container[style*="backgroundColor: #242428"] a:hover {
    color: #FC5200 !important;
    text-decoration: underline !important;
}

/* Scrollbar customizada modo escuro */
#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar {
    width: 12px !important;
    height: 12px !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar-track,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar-track {
    background: #1A1A1E !important;
    border-radius: 6px !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar-thumb,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar-thumb {
    background: #404044 !important;
    border-radius: 6px !important;
}

#app-container[style*="background-color: rgb(36, 36, 40)"] ::-webkit-scrollbar-thumb:hover,
#app-container[style*="backgroundColor: #242428"] ::-webkit-scrollbar-thumb:hover {
    background: #505054 !important;
}

/* ========== BOTÕES MODERNOS ========== */
.btn {
    transition: all 0.3s ease;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
}

.btn-success {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    border: none;
}

/* ========== TOOLTIPS INFORMATIVOS ========== */
.info-tooltip {
    position: relative;
    display: inline-block;
    margin-left: 5px;
    cursor: help;
}

.info-tooltip .tooltip-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 11px;
    font-weight: bold;
}

.info-tooltip .tooltip-text {
    visibility: hidden;
    width: 280px;
    background-color: #2D2D31;
    color: #FFFFFF;
    text-align: left;
    border-radius: 8px;
    padding: 12px;
    position: absolute;
    z-index: 10000;
    bottom: 125%;
    left: 50%;
    margin-left: -140px;
    opacity: 0;
    transition: opacity 0.3s;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    font-size: 0.85rem;
    line-height: 1.4;
}

.info-tooltip .tooltip-text::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: #2D2D31 transparent transparent transparent;
}

.info-tooltip:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}

/* ========== BADGE DE ÚLTIMA ATUALIZAÇÃO ========== */
.last-update-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 20px;
    font-size: 0.8rem;
    color: #667eea;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

/* ========== ATALHOS DE TECLADO ========== */
.keyboard-shortcuts {
    position: fixed;
    bottom: 20px;
    left: 20px;
    z-index: 9998;
    background: rgba(45, 45, 49, 0.95);
    color: white;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.75rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    display: none;
}

.keyboard-shortcuts.show {
    display: block;
    animation: slideInUp 0.3s ease;
}

.keyboard-shortcuts kbd {
    background: #38383C;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    border: 1px solid #404044;
}
</style>
"""