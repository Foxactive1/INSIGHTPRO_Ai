# InsightPro AI - Sistema de Análise de Negócios Inteligente

![Banner](https://via.placeholder.com/1200x400/667eea/ffffff?text=InsightPro+AI+-+Análise+Inteligente+de+Negócios)

Sistema portátil de análise de indicadores financeiros com IA para geração de insights estratégicos.

## 📌 Visão Geral

O InsightPro AI é uma aplicação web que ajuda empreendedores e gestores a monitorar e analisar seus indicadores financeiros com:

- 📊 Dashboard interativo com KPIs
- 🤖 Sistema de IA para sugestões estratégicas
- 📝 Interface para adicionar e gerenciar dados
- 🚀 Versão portátil que roda em qualquer ambiente

## ✨ Funcionalidades Principais

### Dashboard Inteligente
- Visualização de KPIs (Vendas, Despesas, Lucro, Crescimento, etc.)
- Análise por diferentes períodos (dia, semana, mês, trimestre)
- Gráficos e métricas coloridas por desempenho

### Sistema de IA
- Análise de margem e rentabilidade
- Detecção de tendências e padrões
- Recomendações estratégicas priorizadas
- Alertas para situações críticas

### Gerenciamento de Dados
- Formulário intuitivo para adição de registros
- Tabela com histórico recente
- Opção para exclusão de registros
- Cálculos automáticos (lucro, margem, etc.)

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **IA**: Análise preditiva e regras especialistas
- **Design**: Interface responsiva e moderna

## 🚀 Como Executar

### Pré-requisitos
- Python 3.6+
- pip (gerenciador de pacotes)

### Instalação
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/insightpro-ai.git

# Acesse o diretório
cd insightpro-ai

# Execute o aplicativo
python app_v3.py
```

### Acesso
Após iniciar, acesse no navegador:
- http://localhost:5000 (para dashboard)
- http://localhost:5000/adicionar-dados (para inserir dados)

## 📊 Estrutura do Banco de Dados
O sistema utiliza um banco SQLite embutido (`insightpro.db`) com a seguinte estrutura:

```sql
CREATE TABLE indicadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendas REAL NOT NULL DEFAULT 0,
    despesas REAL NOT NULL DEFAULT 0,
    lucro REAL NOT NULL DEFAULT 0,
    crescimento REAL NOT NULL DEFAULT 0,
    ticket_medio REAL DEFAULT 0,
    clientes_ativos INTEGER DEFAULT 0,
    data_registro TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## 📝 Como Contribuir
1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença
Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## ✉️ Contato
Dione Castro Alves - [@InNovaIdeia](https://github.com/InNovaIdeia) - contato@innovadieia.com

---

<div align="center">
  <sub>Criado com ❤︎ por <a href="https://github.com/InNovaIdeia">InNovaIdeia</a></sub>
</div>
