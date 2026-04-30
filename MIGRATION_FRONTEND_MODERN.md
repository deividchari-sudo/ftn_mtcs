# Plano de Migração Frontend - Arquitetura Moderna

## 🎯 Objetivo
Migrar de Dash (Python) para React + TypeScript + Vite - stack moderna e profissional.

---

## 📊 Análise do Frontend Atual

### Stack Atual (Dash)
- **Framework**: Plotly Dash (Python)
- **UI**: Dash Bootstrap Components (dbc)
- **Gráficos**: Plotly
- **Estado**: Callbacks do Dash (limitado)
- **Build**: Server-side rendering Python

### Limitações Identificadas
1. ❌ Performance - recarrega página inteira
2. ❌ UX limitada - componentes básicos
3. ❌ Mobile não otimizado
4. ❌ SEO ruim (client-side rendering pesado)
5. ❌ Escalabilidade limitada
6. ❌ Sem TypeScript (type safety)

---

## 🚀 Nova Arquitetura Proposta

### Stack Moderno (2024/2025)
```
Frontend: React 18 + TypeScript 5 + Vite 5
├─ UI: TailwindCSS + shadcn/ui + Radix UI
├─ Gráficos: Recharts + Plotly (para compatibilidade)
├─ Estado: Zustand (simples) ou Redux Toolkit (complexo)
├─ Roteamento: React Router 6
├─ HTTP Client: Axios + React Query (TanStack Query)
├─ Build: Vite (ultra-rápido)
├─ Testes: Vitest + React Testing Library + Playwright
└─ Lint/Format: ESLint + Prettier
```

### Por Que Esta Stack?

| Critério | Dash (Atual) | React Moderno |
|----------|--------------|---------------|
| Performance | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| UX/UI | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Mobile | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Developer Experience | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Comunidade/Ecosystem | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Type Safety | ⭐ | ⭐⭐⭐⭐⭐ |
| Hiring/Dev Pool | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 📁 Nova Estrutura de Pastas

```
frontend/                          # Novo projeto React
├── src/
│   ├── components/               # Componentes reutilizáveis
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── charts/               # Gráficos (Recharts/Plotly)
│   │   ├── layout/               # Layout, Header, Sidebar
│   │   └── metrics/              # Cards de métricas
│   │
│   ├── pages/                    # Páginas/Routes
│   │   ├── Dashboard.tsx
│   │   ├── AdvancedAnalytics.tsx
│   │   ├── Calendar.tsx
│   │   ├── Goals.tsx
│   │   ├── Wellness.tsx
│   │   ├── AIChat.tsx
│   │   ├── Details.tsx
│   │   └── Config.tsx
│   │
│   ├── hooks/                    # Custom React Hooks
│   │   ├── useMetrics.ts
│   │   ├── useWorkouts.ts
│   │   ├── usePowerCurve.ts
│   │   └── useACWR.ts
│   │
│   ├── stores/                   # Estado global (Zustand)
│   │   ├── metricsStore.ts
│   │   ├── configStore.ts
│   │   └── authStore.ts
│   │
│   ├── services/                 # API calls
│   │   ├── api.ts
│   │   ├── metricsService.ts
│   │   ├── workoutsService.ts
│   │   └── calculationsService.ts
│   │
│   ├── types/                    # TypeScript definitions
│   │   ├── metrics.ts
│   │   ├── workouts.ts
│   │   └── calculations.ts
│   │
│   ├── utils/                    # Utilitários
│   │   ├── formatters.ts
│   │   ├── calculations.ts
│   │   └── constants.ts
│   │
│   ├── lib/                      # Configurações de libs
│   │   ├── queryClient.ts
│   │   └── utils.ts
│   │
│   ├── App.tsx                   # Root component
│   ├── main.tsx                  # Entry point
│   └── index.css                 # Global styles + Tailwind
│
├── public/                       # Assets estáticos
├── tests/                        # Testes
│   ├── unit/
│   ├── integration/
│   └── e2e/                      # Playwright
│
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
├── tailwind.config.js
└── eslint.config.js

# Backend API (FastAPI - já existe, expandir)
api/
├── main.py                       # FastAPI app
├── routers/
│   ├── metrics.py               # Endpoints de métricas
│   ├── workouts.py              # Endpoints de workouts
│   ├── calculations.py          # Endpoints de cálculos
│   ├── power_curve.py           # Power curve API
│   └── advanced.py              # ACWR, TSS by sport
└── schemas/                     # Pydantic models
```

---

## 🔄 Estratégia de Migração

### Fase 1: Setup e API (Semana 1)
1. Criar estrutura frontend React
2. Expandir API FastAPI com endpoints REST
3. Criar types TypeScript mapeando models Python

### Fase 2: Componentes Base (Semana 2)
1. Layout (Header, Sidebar, Footer)
2. Sistema de temas (Dark/Light)
3. Componentes de UI (Button, Card, Table)
4. Sistema de gráficos (Recharts)

### Fase 3: Páginas Core (Semana 3-4)
1. Dashboard (paridade com Dash atual)
2. Advanced Analytics (novas features P0-P3)
3. Integração real-time com backend

### Fase 4: Testes e Otimização (Semana 5)
1. Testes unitários (Vitest)
2. Testes E2E (Playwright)
3. Performance optimization
4. Mobile responsiveness

### Fase 5: Deploy (Semana 6)
1. Build de produção
2. CI/CD pipeline
3. Deploy staging
4. Deploy produção

---

## 📡 API Endpoints Necessários

```python
# metrics.py
GET    /api/v1/metrics                    # Lista métricas
GET    /api/v1/metrics/latest            # Últimas métricas
GET    /api/v1/metrics/pmc               # PMC calculado
GET    /api/v1/metrics/acwr              # ACWR

# workouts.py
GET    /api/v1/workouts                  # Lista workouts
GET    /api/v1/workouts/{id}             # Detalhe workout
GET    /api/v1/workouts/summary          # Resumo semanal
POST   /api/v1/workouts/sync             # Sincronizar Garmin

# calculations.py
POST   /api/v1/calculate/tss             # Calcular TSS
POST   /api/v1/calculate/fitness         # Calcular CTL/ATL/TSB
POST   /api/v1/calculate/power-curve      # Calcular Power Curve
POST   /api/v1/calculate/critical-power  # Calcular CP

# advanced.py
GET    /api/v1/advanced/pmc-by-sport     # PMC por esporte
GET    /api/v1/advanced/acwr            # ACWR detalhado
GET    /api/v1/advanced/running-zones     # Time in Zones
GET    /api/v1/advanced/power-curve       # Dados Power Curve
POST   /api/v1/advanced/season-plan       # Criar season plan

# config.py
GET    /api/v1/config                    # Config atual
PUT    /api/v1/config                    # Atualizar config
```

---

## 🧪 Estratégia de Testes

### Testes Unitários (Vitest)
```typescript
// Exemplo: Teste de cálculo TSS
describe('TSS Calculation', () => {
  it('calculates TSS correctly for known values', () => {
    const result = calculateTSS({ power: 200, ftp: 250, duration: 3600 });
    expect(result).toBe(64); // (200/250)^2 * 100
  });
});
```

### Testes de Integração
- API endpoints respondem corretamente
- Frontend consome API sem erros
- Estados globais funcionam

### Testes E2E (Playwright)
```typescript
// Exemplo: Fluxo completo
test('user views advanced analytics', async ({ page }) => {
  await page.goto('/advanced');
  await expect(page.getByText('ACWR')).toBeVisible();
  await expect(page.getByText('Power Curve')).toBeVisible();
});
```

---

## 📊 Funcionalidades a Preservar (Mapeamento)

### Dashboard (Tab 1)
| Feature Atual (Dash) | Implementação React |
|----------------------|---------------------|
| Cards CTL/ATL/TSB | Componente MetricCard |
| Gráfico PMC | Recharts AreaChart |
| Alertas inteligentes | AlertBanner component |
| Resumo semanal | WeeklySummaryCard |
| Tabela de atividades | DataTable com sorting |

### Advanced Analytics (Tab 2)
| Feature Atual | Implementação React |
|---------------|---------------------|
| ACWR card | ACWRPanel com color coding |
| PMC by Sport | SportMetricsGrid |
| Power Curve | Plotly wrapper ou Recharts |
| Critical Power | CPCard |
| Running Zones | DonutChart + ZoneTable |

### Outras Tabs
- Calendário: Migrar para FullCalendar.js
- Metas: Custom goal tracking UI
- Wellness: Habit tracker UI
- AI Chat: Chat interface moderna
- Config: Form wizard com validation

---

## 🎨 Design System

### Cores (Tailwind)
```javascript
// tailwind.config.js
colors: {
  primary: {
    50: '#f0f9ff',
    500: '#0ea5e9',
    600: '#0284c7',
    900: '#0c4a6e',
  },
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
}
```

### Tipografia
- Font: Inter (Google Fonts)
- Headings: Semibold, tracking-tight
- Body: Normal, leading-relaxed

### Componentes shadcn/ui
- Button (variants: primary, secondary, ghost, danger)
- Card (with header, content, footer)
- Table (sortable, paginated)
- Dialog/Modal
- Tabs
- Form (Input, Select, Checkbox)
- Alert
- Badge
- Progress
- Skeleton (loading states)

---

## 🚀 Performance Targets

| Métrica | Target |
|---------|--------|
| First Contentful Paint | < 1.5s |
| Time to Interactive | < 3s |
| Bundle size (gzipped) | < 200KB |
| Lighthouse Score | > 90 |
| Mobile responsiveness | 100% |

---

## 📅 Timeline Estimada

| Fase | Duração | Entregável |
|------|---------|------------|
| 1. Setup + API | 5 dias | API REST completa, estrutura React |
| 2. Componentes | 5 dias | Design system, layout base |
| 3. Páginas Core | 10 dias | Dashboard, Advanced Analytics |
| 4. Testes | 5 dias | >80% coverage, E2E passando |
| 5. Deploy | 3 dias | Produção live |
| **Total** | **~28 dias** | **Frontend moderno completo** |

---

## ✅ Checklist de Sucesso

- [ ] Todas as 7 tabs funcionando
- [ ] 243 testes de backend passando
- [ ] 100+ testes de frontend passando
- [ ] Lighthouse score > 90
- [ ] Mobile responsive
- [ ] Feature parity 100% com Dash atual
- [ ] Zero regressões
- [ ] Deploy automático (CI/CD)

---

**Data:** 2026-04-29  
**Versão:** 1.0  
**Status:** Pronto para implementação
