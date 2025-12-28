"""
Scripts JavaScript para funcionalidades do dashboard
"""
INDEX_STRING = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script>
        // Persistência do modo escuro
        window.addEventListener('DOMContentLoaded', function() {
            const savedDarkMode = localStorage.getItem('darkMode');
            if (savedDarkMode === 'true') {
                // Aguarda o componente carregar
                setTimeout(() => {
                    const toggleBtn = document.getElementById('dark-mode-toggle');
                    if (toggleBtn) toggleBtn.click();
                }, 100);
            }

            // Atalhos de teclado
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + D = Toggle modo escuro
                if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                    e.preventDefault();
                    const toggleBtn = document.getElementById('dark-mode-toggle');
                    if (toggleBtn) toggleBtn.click();
                }

                // Ctrl/Cmd + K = Mostrar atalhos
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    alert('Atalhos de Teclado:\\n\\n' +
                          'Ctrl+D: Alternar modo escuro\\n' +
                          'Ctrl+R: Atualizar dados\\n' +
                          'Ctrl+1/2/3/4: Navegar abas');
                }

                // Ctrl/Cmd + 1-4 = Navegar entre abas
                if ((e.ctrlKey || e.metaKey) && ['1','2','3','4'].includes(e.key)) {
                    e.preventDefault();
                    const tabs = ['dashboard', 'calendar', 'goals', 'config'];
                    const tabIndex = parseInt(e.key) - 1;
                    const tabButtons = document.querySelectorAll('[role="tab"]');
                    if (tabButtons[tabIndex]) tabButtons[tabIndex].click();
                }
            });
        });

        // Salvar preferência quando modo escuro mudar
        window.saveDarkModePreference = function(isDark) {
            localStorage.setItem('darkMode', isDark);
        };
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''