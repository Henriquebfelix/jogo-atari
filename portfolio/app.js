/**
 * Aplicação JavaScript Pura (Vanilla JS)
 * Portfólio Pessoal - Henrique Silva
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Atualizar ano dinâmico no rodapé
    const currentYearEl = document.getElementById('currentYear');
    if (currentYearEl) {
        currentYearEl.textContent = new Date().getFullYear();
    }

    // 2. Base de dados fictícia dos Projetos para o modal "Ver mais"
    const projectsData = {
        '1': {
            title: 'MarketHub Store',
            category: 'E-commerce',
            categoryClass: 'bg-primary-subtle text-primary',
            icon: '<i class="bi bi-cart3 fs-1 text-primary"></i>',
            description: 'Uma solução completa para comércio eletrônico desenvolvida com foco em alta performance e experiência do cliente.',
            techs: ['HTML5', 'CSS3', 'JavaScript ES6', 'Bootstrap 5', 'REST API', 'Stripe Mock'],
            features: [
                'Catálogo de produtos com paginação e busca em tempo real',
                'Carrinho com atualização instantânea de subtotais e cálculo de frete simulado',
                'Filtro dinâmico por categorias e faixas de preço',
                'Layout 100% responsivo otimizado para dispositivos móveis'
            ]
        },
        '2': {
            title: 'FinanceFlow App',
            category: 'Finanças Pessoais',
            categoryClass: 'bg-success-subtle text-success',
            icon: '<i class="bi bi-wallet2 fs-1 text-success"></i>',
            description: 'Plataforma leve para gestão de finanças pessoais com relatórios mensais e acompanhamento de metas orçamentárias.',
            techs: ['JavaScript Puro', 'LocalStorage API', 'Bootstrap Grid', 'Canvas / Gráficos', 'CSS Modules'],
            features: [
                'Registro e categorização de receitas e despesas com datas',
                'Cálculo automático de balanço mensal e saldo disponível',
                'Persistência local dos dados utilizando LocalStorage no navegador',
                'Exportação simplificada de lançamentos em formato CSV fictício'
            ]
        },
        '3': {
            title: 'OmniMetrics Dashboard',
            category: 'Business Intelligence',
            categoryClass: 'bg-info-subtle text-info',
            icon: '<i class="bi bi-bar-chart-line fs-1 text-info"></i>',
            description: 'Painel administrativo e analítico focado no acompanhamento de indicadores-chave de performance (KPIs) empresariais.',
            techs: ['HTML5 Semântico', 'Bootstrap 5', 'JavaScript Modular', 'CSS Grid', 'Design System'],
            features: [
                'Métricas em tempo real com cartões informativos de variação percentual',
                'Tabelas de dados com ordenação dinâmica e filtros rápidos',
                'Suporte a múltiplos temas visuais (Dark Mode & Light Mode)',
                'Gráficos interativos simulando tráfego, conversão e retenção'
            ]
        }
    };

    // 3. Inicialização e controle do Modal Bootstrap via JS
    const projectModalEl = document.getElementById('projectModal');
    let projectModalInstance = null;
    if (typeof bootstrap !== 'undefined' && projectModalEl) {
        projectModalInstance = new bootstrap.Modal(projectModalEl);
    }

    const modalTitle = document.getElementById('modalProjectTitle');
    const modalCategory = document.getElementById('modalProjectCategory');
    const modalIcon = document.getElementById('modalProjectIcon');
    const modalDescription = document.getElementById('modalProjectDescription');
    const modalTechs = document.getElementById('modalProjectTechs');
    const modalFeatures = document.getElementById('modalProjectFeatures');

    const verMaisButtons = document.querySelectorAll('.btn-ver-mais');
    verMaisButtons.forEach(btn => {
        btn.addEventListener('click', (event) => {
            const projectId = event.currentTarget.getAttribute('data-project-id');
            const project = projectsData[projectId];

            if (project && projectModalInstance) {
                // Preenche os campos do modal com os dados do projeto
                modalTitle.textContent = project.title;
                modalCategory.textContent = project.category;
                modalCategory.className = `badge ${project.categoryClass}`;
                modalIcon.innerHTML = project.icon;
                modalDescription.textContent = project.description;

                // Renderiza as badges de tecnologias
                modalTechs.innerHTML = project.techs
                    .map(tech => `<span class="badge bg-dark-subtle text-light border border-secondary-subtle px-3 py-2">${tech}</span>`)
                    .join('');

                // Renderiza a lista de recursos
                modalFeatures.innerHTML = project.features
                    .map(feat => `<li class="mb-2"><i class="bi bi-check2-circle text-primary me-2"></i>${feat}</li>`)
                    .join('');

                // Exibe o modal
                projectModalInstance.show();
            }
        });
    });

    // 4. Fechar o menu colapsável do Bootstrap ao clicar em um link no mobile
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarCollapse = document.getElementById('navbarNav');
    if (navbarCollapse && typeof bootstrap !== 'undefined') {
        const bsCollapse = bootstrap.Collapse.getOrCreateInstance(navbarCollapse, { toggle: false });
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navbarCollapse.classList.contains('show')) {
                    bsCollapse.hide();
                }
            });
        });
    }

    // 5. Efeito sutil de navegação ativa com base no scroll
    const sections = document.querySelectorAll('header, section');
    window.addEventListener('scroll', () => {
        let currentSectionId = '';
        const scrollPosition = window.scrollY + 200;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                currentSectionId = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSectionId}`) {
                link.classList.add('active');
            }
        });
    });
});
