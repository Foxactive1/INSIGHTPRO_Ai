# ===== INSIGHTPRO AI - VERSÃO PORTÁVEL =====
# Desenvolvido por Dione Castro Alves - InNovaIdeia
# Versão otimizada para execução em qualquer ambiente

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
import random

# Configuração automática de dependências
def verificar_dependencias():
    """Verifica e instala dependências automaticamente"""
    try:
        import flask
        print("✅ Flask já instalado")
    except ImportError:
        print("📦 Instalando Flask...")
        os.system(f"{sys.executable} -m pip install flask")
        import flask

# Verificar dependências na inicialização
verificar_dependencias()

from flask import Flask, render_template_string, request, jsonify

# ===== CONFIGURAÇÕES PORTÁVEIS =====
class Config:
    # Detecta automaticamente o diretório de execução
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'insightpro.db')
    SECRET_KEY = 'insightpro-portable-key'
    
    # Configuração para diferentes ambientes
    HOST = '0.0.0.0' if os.getenv('TERMUX_VERSION') else '127.0.0.1'
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = True

# ===== GERENCIAMENTO DE BANCO PORTÁVEL =====
class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DB_PATH
        self.inicializar_db()
    
    def conectar(self):
        """Conexão robusta com tratamento de erros"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute('PRAGMA journal_mode=WAL')  # Melhor performance
            return conn
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return None
    
    def inicializar_db(self):
        """Inicializa banco com dados de exemplo se necessário"""
        conn = self.conectar()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS indicadores (
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
            ''')
            
            # Inserir dados de exemplo apenas se tabela estiver vazia
            if cursor.execute('SELECT COUNT(*) FROM indicadores').fetchone()[0] == 0:
                self.popular_dados_exemplo(cursor)
            
            conn.commit()
            print("✅ Banco de dados inicializado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao inicializar BD: {e}")
        finally:
            conn.close()
    
    def popular_dados_exemplo(self, cursor):
        """Popula dados de exemplo para demonstração"""
        print("📊 Gerando dados de exemplo...")
        datas = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        
        for i, data in enumerate(datas):
            vendas = max(8000 + i*200 + random.randint(-1000, 1500), 1000)
            despesas = max(vendas * 0.6 + random.randint(-500, 800), 500)
            lucro = vendas - despesas
            crescimento = (i/10) - 1.5 + random.uniform(-2, 2)
            ticket_medio = 120 + i*1.5 + random.randint(-20, 30)
            clientes_ativos = max(80 + i*2 + random.randint(-10, 15), 20)
            
            cursor.execute('''
                INSERT INTO indicadores 
                (vendas, despesas, lucro, crescimento, ticket_medio, clientes_ativos, data_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (vendas, despesas, lucro, crescimento, ticket_medio, clientes_ativos, data))
    
    def get_kpis(self, periodo='semana'):
        """Obtém KPIs do período especificado"""
        conn = self.conectar()
        if not conn:
            return self.get_kpis_fallback()
        
        try:
            cursor = conn.cursor()
            
            # Mapear período para dias
            dias_map = {'dia': 1, 'semana': 7, 'mes': 30, 'trimestre': 90}
            dias = dias_map.get(periodo, 7)
            
            data_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT 
                    AVG(vendas) as vendas,
                    AVG(despesas) as despesas,
                    AVG(lucro) as lucro,
                    AVG(crescimento) as crescimento,
                    AVG(ticket_medio) as ticket_medio,
                    AVG(clientes_ativos) as clientes_ativos
                FROM indicadores 
                WHERE data_registro >= ?
            ''', (data_limite,))
            
            row = cursor.fetchone()
            return {
                'vendas': round(row[0] or 0, 2),
                'despesas': round(row[1] or 0, 2),
                'lucro': round(row[2] or 0, 2),
                'crescimento': round(row[3] or 0, 2),
                'ticket_medio': round(row[4] or 0, 2),
                'clientes_ativos': int(row[5] or 0)
            }
        except Exception as e:
            print(f"❌ Erro ao obter KPIs: {e}")
            return self.get_kpis_fallback()
        finally:
            conn.close()
    
    def get_kpis_fallback(self):
        """KPIs de fallback em caso de erro"""
        return {
            'vendas': 12500.0,
            'despesas': 8200.0,
            'lucro': 4300.0,
            'crescimento': 2.5,
            'ticket_medio': 185.0,
            'clientes_ativos': 145
        }
    
    def get_historico(self, limite=30):
        """Obtém histórico limitado para análise"""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM indicadores 
                ORDER BY data_registro DESC 
                LIMIT ?
            ''', (limite,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erro ao obter histórico: {e}")
            return []
        finally:
            conn.close()

    def get_dados_recentes(self, limite=10):
        """Obtém dados recentes para exibição na tabela"""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, vendas, despesas, lucro, crescimento, 
                       ticket_medio, clientes_ativos, data_registro,
                       created_at
                FROM indicadores 
                ORDER BY data_registro DESC, created_at DESC 
                LIMIT ?
            ''', (limite,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erro ao obter dados recentes: {e}")
            return []
        finally:
            conn.close()
    
    def inserir_dados(self, vendas, despesas, lucro, crescimento, ticket_medio, clientes_ativos, data_registro):
        """Insere novos dados no banco"""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO indicadores 
                (vendas, despesas, lucro, crescimento, ticket_medio, clientes_ativos, data_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (vendas, despesas, lucro, crescimento, ticket_medio, clientes_ativos, data_registro))
            
            conn.commit()
            print(f"✅ Dados inseridos com sucesso para {data_registro}")
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir dados: {e}")
            return False
        finally:
            conn.close()
    
    def deletar_dados(self, id):
        """Remove dados específicos pelo ID"""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM indicadores WHERE id = ?', (id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ Dados ID {id} removidos com sucesso")
                return True
            else:
                print(f"⚠️ Nenhum dado encontrado com ID {id}")
                return False
        except Exception as e:
            print(f"❌ Erro ao deletar dados: {e}")
            return False
        finally:
            conn.close()

# ===== SISTEMA DE IA PARA SUGESTÕES =====
# ===== SISTEMA DE IA PARA SUGESTÕES (MELHORADO) =====
class SugestaoIA:
    @staticmethod
    def gerar_sugestao_completa(kpis, historico=None):
        """Sistema inteligente de sugestões baseado em KPIs e análise preditiva"""
        sugestoes = []
        
        vendas = kpis.get('vendas', 0)
        despesas = kpis.get('despesas', 0)
        lucro = kpis.get('lucro', 0)
        crescimento = kpis.get('crescimento', 0)
        ticket_medio = kpis.get('ticket_medio', 0)
        clientes_ativos = kpis.get('clientes_ativos', 0)
        
        # === ANÁLISE FUNDAMENTAL AVANÇADA ===
        margem = (lucro / vendas * 100) if vendas > 0 else 0
        razao_despesas = (despesas / vendas * 100) if vendas > 0 else 0
        receita_por_cliente = vendas / clientes_ativos if clientes_ativos > 0 else 0
        
        # Análise de saúde financeira
        if margem < 10:
            sugestoes.append(f"⚠️ <strong>Margem crítica</strong> ({margem:.1f}%): Risco de prejuízo! Revisar custos operacionais e precificação")
        elif margem < 20:
            sugestoes.append(f"🔸 <strong>Margem moderada</strong> ({margem:.1f}%): Otimize processos e reduza desperdícios para melhorar")
        elif margem > 40:
            sugestoes.append(f"✅ <strong>Margem excelente</strong> ({margem:.1f}%): Considere investir em expansão ou novos produtos")
        
        # Análise de eficiência operacional
        if razao_despesas > 75:
            sugestoes.append(f"🔴 <strong>Despesas muito altas</strong> ({razao_despesas:.1f}% da receita): Priorize redução de custos urgentemente")
        elif razao_despesas > 60:
            sugestoes.append(f"🔸 <strong>Despesas acima do ideal</strong> ({razao_despesas:.1f}%): Analise contratos e negocie melhores condições")
        
        # Análise de crescimento sustentável
        if crescimento < -5:
            sugestoes.append(f"📉 <strong>Queda acentuada</strong> ({crescimento:.1f}%): Realize promoções urgentes e análise de mercado")
        elif crescimento < 0:
            sugestoes.append(f"🔻 <strong>Desaceleração</strong> ({crescimento:.1f}%): Revise estratégias de marketing e vendas")
        elif crescimento > 15:
            sugestoes.append(f"🚀 <strong>Crescimento acelerado</strong> ({crescimento:.1f}%): Garanta capacidade operacional para sustentar")
        
        # Análise de valor do cliente
        if receita_por_cliente < 50:
            sugestoes.append(f"💡 <strong>Baixo valor por cliente</strong> (R${receita_por_cliente:.2f}): Implemente programas de fidelização e upsell")
        elif receita_por_cliente > 200:
            sugestoes.append(f"💎 <strong>Alto valor por cliente</strong> (R${receita_por_cliente:.2f}): Invista em experiência premium e retenção")
        
        # === ANÁLISE PREDITIVA E TENDÊNCIAS ===
        if historico and len(historico) >= 7:
            try:
                # Tendência dos últimos 7 dias
                vendas_recentes = [h['vendas'] for h in historico[:7]]
                lucros_recentes = [h['lucro'] for h in historico[:7]]
                
                # Cálculo de tendência
                tendencia_vendas = (vendas_recentes[0] - vendas_recentes[-1]) / vendas_recentes[-1] * 100
                tendencia_lucros = (lucros_recentes[0] - lucros_recentes[-1]) / lucros_recentes[-1] * 100
                
                if tendencia_vendas < -5:
                    sugestoes.append(f"📉 <strong>Tendência negativa de vendas</strong> ({tendencia_vendas:.1f}%): Investigar causas imediatamente")
                elif tendencia_vendas > 5:
                    sugestoes.append(f"📈 <strong>Tendência positiva de vendas</strong> ({tendencia_vendas:.1f}%): Capitalize no momento favorável")
                
                if tendencia_lucros < -8:
                    sugestoes.append(f"⚠️ <strong>Erosão de lucros</strong> ({tendencia_lucros:.1f}%): Revisar estrutura de custos urgentemente")
                
                # Detecção de padrões sazonais
                dias_semana = [datetime.strptime(h['data_registro'], '%Y-%m-%d').weekday() for h in historico[:7]]
                melhor_dia = max(set(dias_semana), key=dias_semana.count)
                dias_nome = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                sugestoes.append(f"📅 <strong>Padrão semanal</strong>: Melhor desempenho às {dias_nome[melhor_dia]}s-feiras")
                
            except Exception as e:
                print(f"Erro na análise preditiva: {e}")
        
        # === RECOMENDAÇÕES ESTRATÉGICAS PERSONALIZADAS ===
        if lucro > 5000 and crescimento > 8:
            sugestoes.append("🌟 <strong>Performance excepcional</strong>: Considere investir em novos mercados ou aquisições")
        
        if clientes_ativos > 100 and ticket_medio < 80:
            sugestoes.append("💡 <strong>Oportunidade de valor</strong>: Desenvolva produtos premium para aumentar ticket médio")
        
        if vendas > 20000 and razao_despesas > 70:
            sugestoes.append("⚠️ <strong>Alerta de eficiência</strong>: Mesmo com alto volume, despesas comprometem lucratividade")
        
        # Fallback
        if not sugestoes:
            sugestoes.append("✅ <strong>Indicadores estáveis</strong>: Continue monitorando e buscando pequenas melhorias")
        
        # Priorização das sugestões
        priorizadas = []
        for s in sugestoes:
            if "⚠️" in s or "🔴" in s:
                priorizadas.insert(0, f"<div class='urgencia'>{s}</div>")
            else:
                priorizadas.append(s)
        
        # Rodapé com análise resumida
        priorizadas.append(f"""
        <div class='ia-resumo'>
            <p><strong>🔍 Resumo Financeiro:</strong></p>
            <p>Margem Líquida: {margem:.1f}% | Rentabilidade: {'✅' if lucro > 0 else '⚠️'}</p>
            <p>Eficiência Operacional: {'🔴' if razao_despesas > 70 else '🔸' if razao_despesas > 60 else '✅'}</p>
            <p>Saúde do Crescimento: {'🚀' if crescimento > 10 else '📈' if crescimento > 0 else '📉'}</p>
        </div>
        """)
        
        # Rodapé
        priorizadas.append("""
        <div class='ia-footer'>
            <p><strong>🤖 InsightPro AI - Análise Avançada</strong></p>
            <p>Desenvolvido por Dione Castro Alves | InNovaIdeia © 2025</p>
        </div>
        """)
        
        return priorizadas

# ===== TEMPLATE PARA ADICIONAR DADOS =====
ADICIONAR_DADOS_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adicionar Dados - InsightPro AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .nav-buttons {
            margin: 20px 0;
        }
        
        .nav-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 10px;
            border-radius: 25px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .nav-btn:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.05);
        }
        
        .form-section {
            padding: 30px;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            font-weight: bold;
            margin-bottom: 8px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .form-group input {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
        }
        
        .form-group.required label::after {
            content: '*';
            color: #e74c3c;
            margin-left: 3px;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 25px;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            max-width: 300px;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-weight: bold;
            display: none;
        }
        
        .alert.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .dados-recentes {
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #e0e0e0;
        }
        
        .table-container {
            overflow-x: auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        th {
            background: #f8f9fa;
            font-weight: bold;
            color: #333;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .delete-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .delete-btn:hover {
            background: #c0392b;
        }
        
        .loading {
            text-align: center;
            color: #666;
            padding: 20px;
        }
        
        .margem-display {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        @media (max-width: 768px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
            
            .nav-btn {
                display: block;
                margin: 5px 0;
            }
            
            table {
                font-size: 14px;
            }
            
            th, td {
                padding: 8px 10px;
            }
        }
           .urgencia {
        background: #fff8e6;
        padding: 12px;
        border-left: 4px solid #ff9800;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    
    .ia-resumo {
        background: #f0f7ff;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        border: 1px solid #d1e3f8;
    }
    
    .ia-footer {
        margin-top: 20px;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        color: white;
        text-align: center;
    }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Adicionar Dados</h1>
            <p>Insira os dados financeiros do seu negócio</p>
            
            <div class="nav-buttons">
                <a href="/dashboard" class="nav-btn">📈 Dashboard</a>
                <a href="/" class="nav-btn">🏠 Início</a>
            </div>
        </div>
        
        <div class="form-section">
            <form id="dadosForm">
                <div class="form-grid">
                    <div class="form-group required">
                        <label for="vendas">💰 Vendas (R$)</label>
                        <input type="number" id="vendas" name="vendas" step="0.01" min="0" required>
                    </div>
                    
                    <div class="form-group required">
                        <label for="despesas">💸 Despesas (R$)</label>
                        <input type="number" id="despesas" name="despesas" step="0.01" min="0" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="crescimento">📊 Crescimento (%)</label>
                        <input type="number" id="crescimento" name="crescimento" step="0.01">
                    </div>
                    
                    <div class="form-group">
                        <label for="ticket_medio">🎫 Ticket Médio (R$)</label>
                        <input type="number" id="ticket_medio" name="ticket_medio" step="0.01" min="0">
                    </div>
                    
                    <div class="form-group">
                        <label for="clientes_ativos">👥 Clientes Ativos</label>
                        <input type="number" id="clientes_ativos" name="clientes_ativos" min="1" value="1">
                    </div>
                    
                    <div class="form-group">
                        <label for="data_registro">📅 Data</label>
                        <input type="date" id="data_registro" name="data_registro">
                    </div>
                </div>
                
                <div id="previewCalculos" class="margem-display"></div>
                
                <div class="alert" id="alertBox"></div>
                
                <button type="submit" class="submit-btn" id="submitBtn">
                    💾 Salvar Dados
                </button>
            </form>
            
            <div class="dados-recentes">
                <h2>📋 Dados Recentes</h2>
                <div id="tabelaDados" class="loading">Carregando dados...</div>
            </div>
        </div>
    </div>

    <script>
        // Definir data atual como padrão
        document.getElementById('data_registro').value = new Date().toISOString().split('T')[0];
        
        // Calcular valores em tempo real
        function calcularPreview() {
            const vendas = parseFloat(document.getElementById('vendas').value) || 0;
            const despesas = parseFloat(document.getElementById('despesas').value) || 0;
            const lucro = vendas - despesas;
            const margem = vendas > 0 ? (lucro / vendas * 100) : 0;
            
            if (vendas > 0 || despesas > 0) {
                document.getElementById('previewCalculos').innerHTML = `
                    <strong>💡 Prévia dos Cálculos:</strong><br>
                    Lucro: R$ ${lucro.toFixed(2)} | 
                    Margem: ${margem.toFixed(1)}% 
                    ${margem < 15 ? '⚠️' : margem > 40 ? '🎯' : '✅'}
                `;
            } else {
                document.getElementById('previewCalculos').innerHTML = '';
            }
        }
        
        // Eventos para cálculo em tempo real
        ['vendas', 'despesas'].forEach(id => {
            document.getElementById(id).addEventListener('input', calcularPreview);
        });
        
        // Submissão do formulário
        document.getElementById('dadosForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const alertBox = document.getElementById('alertBox');
            
            // Desabilitar botão durante envio
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Salvando...';
            
            // Coletar dados do formulário
            const formData = new FormData(e.target);
            const dados = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/api/salvar-dados', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(dados)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Sucesso
                    alertBox.className = 'alert success';
                    alertBox.textContent = `✅ ${result.message} | Lucro: R$ ${result.dados.lucro} | Margem: ${result.dados.margem}%`;
                    alertBox.style.display = 'block';
                    
                    // Limpar formulário
                    e.target.reset();
                    document.getElementById('data_registro').value = new Date().toISOString().split('T')[0];
                    document.getElementById('previewCalculos').innerHTML = '';
                    
                    // Atualizar tabela
                    carregarDadosRecentes();
                } else {
                    // Erro
                    alertBox.className = 'alert error';
                    alertBox.textContent = `❌ ${result.message}`;
                    alertBox.style.display = 'block';
                }
            } catch (error) {
                alertBox.className = 'alert error';
                alertBox.textContent = `❌ Erro de conexão: ${error.message}`;
                alertBox.style.display = 'block';
            } finally {
                // Reabilitar botão
                submitBtn.disabled = false;
                submitBtn.textContent = '💾 Salvar Dados';
                
                // Esconder alerta após 5 segundos
                setTimeout(() => {
                    alertBox.style.display = 'none';
                }, 5000);
            }
        });
        
        // Carregar dados recentes
        async function carregarDadosRecentes() {
            try {
                const response = await fetch('/api/dados-recentes');
                const result = await response.json();
                
                if (result.dados && result.dados.length > 0) {
                    let html = `
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Data</th>
                                        <th>Vendas</th>
                                        <th>Despesas</th>
                                        <th>Lucro</th>
                                        <th>Margem</th>
                                        <th>Crescimento</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    result.dados.forEach(item => {
                        const margem = item.vendas > 0 ? (item.lucro / item.vendas * 100) : 0;
                        const margemColor = margem < 15 ? '#e74c3c' : margem > 40 ? '#27ae60' : '#333';
                        
                        html += `
                            <tr>
                                <td>${new Date(item.data_registro).toLocaleDateString('pt-BR')}</td>
                                <td>R$ ${parseFloat(item.vendas).toFixed(2)}</td>
                                <td>R$ ${parseFloat(item.despesas).toFixed(2)}</td>
                                <td style="color: ${item.lucro >= 0 ? '#27ae60' : '#e74c3c'}">
                                    R$ ${parseFloat(item.lucro).toFixed(2)}
                                </td>
                                <td style="color: ${margemColor}">
                                    ${margem.toFixed(1)}%
                                </td>
                                <td style="color: ${item.crescimento >= 0 ? '#27ae60' : '#e74c3c'}">
                                    ${parseFloat(item.crescimento).toFixed(1)}%
                                </td>
                                <td>
                                    <button class="delete-btn" onclick="deletarDados(${item.id})">
                                        🗑️ Excluir
                                    </button>
                                </td>
                            </tr>
                        `;
                    });
                    
                    html += '</tbody></table></div>';
                    document.getElementById('tabelaDados').innerHTML = html;
                } else {
                    document.getElementById('tabelaDados').innerHTML = '<p>📝 Nenhum dado encontrado. Adicione o primeiro registro!</p>';
                }
            } catch (error) {
                document.getElementById('tabelaDados').innerHTML = '<p>❌ Erro ao carregar dados recentes.</p>';
            }
        }
        
        // Deletar dados
        async function deletarDados(id) {
            if (!confirm('⚠️ Tem certeza que deseja excluir este registro?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/deletar-dados/${id}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('✅ Dados removidos com sucesso!');
                    carregarDadosRecentes();
                } else {
                    alert(`❌ ${result.message}`);
                }
            } catch (error) {
                alert(`❌ Erro ao remover dados: ${error.message}`);
            }
        }
        
        // Carregar dados ao inicializar
        carregarDadosRecentes();
        
        // Auto-atualizar dados a cada 30 segundos
        setInterval(carregarDadosRecentes, 30000);
    </script>
</body>
</html>
"""

# ===== TEMPLATE HTML EMBARCADO =====
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ titulo }} - InsightPro AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .periodo-selector {
            margin: 20px 0;
        }
        
        .periodo-selector select {
            padding: 10px 15px;
            border: none;
            border-radius: 25px;
            background: rgba(255,255,255,0.2);
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        
        .kpis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        
        .kpi-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .kpi-card:hover {
            transform: translateY(-5px);
        }
        
        .kpi-card h3 {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .kpi-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .kpi-value.positive { color: #27AE60; }
        .kpi-value.negative { color: #E74C3C; }
        
        .sugestoes {
            background: #f8f9fa;
            padding: 30px;
            border-top: 3px solid #667eea;
        }
        
        .sugestoes h2 {
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .sugestao-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
            margin: 10px;
        }
        
        .refresh-btn:hover {
            background: #764ba2;
            transform: scale(1.05);
        }
        
        @media (max-width: 768px) {
            .kpis-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                padding: 20px;
            }
            
            .header h1 { font-size: 2em; }
            .kpi-value { font-size: 1.5em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 {{ titulo }}</h1>
            <p>Inteligência Artificial para Negócios</p>
            
            <div class="periodo-selector">
                <select id="periodoSelect" onchange="alterarPeriodo()">
                    <option value="dia" {{ 'selected' if periodo == 'dia' else '' }}>Último Dia</option>
                    <option value="semana" {{ 'selected' if periodo == 'semana' else '' }}>Última Semana</option>
                    <option value="mes" {{ 'selected' if periodo == 'mes' else '' }}>Último Mês</option>
                    <option value="trimestre" {{ 'selected' if periodo == 'trimestre' else '' }}>Último Trimestre</option>
                </select>
                <button class="refresh-btn" onclick="atualizarDados()">🔄 Atualizar</button>
                <a href="/adicionar-dados" class="refresh-btn" style="text-decoration: none; display: inline-block;">📝 Adicionar Dados</a>
            </div>
        </div>
        
        <div class="kpis-grid" id="kpisContainer">
            <div class="kpi-card">
                <h3>💰 Vendas</h3>
                <div class="kpi-value">R$ {{ "{:,.2f}".format(kpis.vendas) }}</div>
            </div>
            
            <div class="kpi-card">
                <h3>💸 Despesas</h3>
                <div class="kpi-value">R$ {{ "{:,.2f}".format(kpis.despesas) }}</div>
            </div>
            
            <div class="kpi-card">
                <h3>📈 Lucro</h3>
                <div class="kpi-value {{ 'positive' if kpis.lucro > 0 else 'negative' }}">
                    R$ {{ "{:,.2f}".format(kpis.lucro) }}
                </div>
            </div>
            
            <div class="kpi-card">
                <h3>📊 Crescimento</h3>
                <div class="kpi-value {{ 'positive' if kpis.crescimento > 0 else 'negative' }}">
                    {{ "{:+.1f}".format(kpis.crescimento) }}%
                </div>
            </div>
            
            <div class="kpi-card">
                <h3>🎫 Ticket Médio</h3>
                <div class="kpi-value">R$ {{ "{:,.2f}".format(kpis.ticket_medio) }}</div>
            </div>
            
            <div class="kpi-card">
                <h3>👥 Clientes Ativos</h3>
                <div class="kpi-value">{{ kpis.clientes_ativos }}</div>
            </div>
        </div>
        
        <div class="sugestoes">
            <h2>🤖 Sugestões da IA</h2>
            <div id="sugestoesContainer">
                {% for sugestao in sugestoes %}
                    <div class="sugestao-item">{{ sugestao|safe }}</div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        function alterarPeriodo() {
            const periodo = document.getElementById('periodoSelect').value;
            window.location.href = `/dashboard?periodo=${periodo}`;
        }
        
        async function atualizarDados() {
            const periodo = document.getElementById('periodoSelect').value;
            document.getElementById('sugestoesContainer').innerHTML = '<div class="loading">🔄 Atualizando dados...</div>';
            
            try {
                const response = await fetch(`/api/atualizar-dados?periodo=${periodo}`);
                const data = await response.json();
                
                // Recarregar página para atualizar todos os dados
                setTimeout(() => window.location.reload(), 500);
            } catch (error) {
                console.error('Erro ao atualizar:', error);
                alert('Erro ao atualizar dados. Tente novamente.');
            }
        }
        
        // Auto-refresh a cada 5 minutos
        setInterval(() => {
            console.log('Auto-refresh executado');
            // atualizarDados(); // Descomente para ativar auto-refresh
        }, 300000);
    </script>
</body>
</html>
"""

# ===== APLICAÇÃO FLASK PRINCIPAL =====
def criar_app():
    """Factory para criar aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar componentes
    db_manager = DatabaseManager()
    
    @app.route('/')
    def index():
        return render_template_string("""
        <div style='text-align: center; font-family: Arial; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white;'>
            <h1 style='font-size: 3em; margin-bottom: 20px;'>🚀 InsightPro AI</h1>
            <p style='font-size: 1.2em; margin-bottom: 30px;'>Sistema Inteligente de Análise de Negócios</p>
            <a href='/dashboard' style='background: white; color: #667eea; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 1.1em; margin: 10px;'>
                📊 Acessar Dashboard
            </a>
            <a href='/adicionar-dados' style='background: rgba(255,255,255,0.9); color: #667eea; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 1.1em; margin: 10px;'>
                📝 Adicionar Dados
            </a>
            <div style='margin-top: 40px; font-size: 0.9em; opacity: 0.8;'>
                <p>Desenvolvido por <strong>Dione Castro Alves</strong></p>
                <p>InNovaIdeia © 2025</p>
            </div>
        </div>
        """)
    
    @app.route('/dashboard')
    def dashboard():
        periodo = request.args.get('periodo', 'semana')
        kpis = db_manager.get_kpis(periodo)
        historico = db_manager.get_historico()
        sugestoes = SugestaoIA.gerar_sugestao_completa(kpis, historico)
        
        return render_template_string(DASHBOARD_TEMPLATE, 
                                      titulo="Dashboard Estratégico",
                                      kpis=kpis,
                                      sugestoes=sugestoes,
                                      periodo=periodo)
    
    @app.route('/api/atualizar-dados')
    def atualizar_dados():
        periodo = request.args.get('periodo', 'semana')
        kpis = db_manager.get_kpis(periodo)
        historico = db_manager.get_historico()
        sugestoes = SugestaoIA.gerar_sugestao_completa(kpis, historico)
        
        return jsonify({
            'kpis': kpis,
            'sugestoes': sugestoes,
            'status': 'success'
        })
    
    @app.route('/api/status')
    def status():
        return jsonify({
            'status': 'online',
            'version': '2.0',
            'author': 'Dione Castro Alves',
            'company': 'InNovaIdeia'
        })
    
    @app.route('/adicionar-dados')
    def adicionar_dados():
        return render_template_string(ADICIONAR_DADOS_TEMPLATE)
    
    @app.route('/api/salvar-dados', methods=['POST'])
    def salvar_dados():
        try:
            dados = request.get_json()
            
            # Validar dados obrigatórios
            campos_obrigatorios = ['vendas', 'despesas']
            for campo in campos_obrigatorios:
                if campo not in dados or dados[campo] == '':
                    return jsonify({'success': False, 'message': f'Campo {campo} é obrigatório'})
            
            # Converter e calcular valores
            vendas = float(dados['vendas'])
            despesas = float(dados['despesas'])
            lucro = vendas - despesas
            crescimento = float(dados.get('crescimento', 0))
            ticket_medio = float(dados.get('ticket_medio', vendas / max(1, int(dados.get('clientes_ativos', 1)))))
            clientes_ativos = int(dados.get('clientes_ativos', 1))
            data_registro = dados.get('data_registro', datetime.now().strftime('%Y-%m-%d'))
            
            # Salvar no banco
            resultado = db_manager.inserir_dados(
                vendas, despesas, lucro, crescimento, 
                ticket_medio, clientes_ativos, data_registro
            )
            
            if resultado:
                return jsonify({
                    'success': True, 
                    'message': 'Dados salvos com sucesso!',
                    'dados': {
                        'vendas': vendas,
                        'despesas': despesas,
                        'lucro': lucro,
                        'margem': round((lucro/vendas)*100, 2) if vendas > 0 else 0
                    }
                })
            else:
                return jsonify({'success': False, 'message': 'Erro ao salvar dados'})
                
        except ValueError as e:
            return jsonify({'success': False, 'message': 'Valores inválidos. Use apenas números.'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})
    
    @app.route('/api/dados-recentes')
    def dados_recentes():
        dados = db_manager.get_dados_recentes(limite=10)
        return jsonify({'dados': dados})
    
    @app.route('/api/deletar-dados/<int:id>', methods=['DELETE'])
    def deletar_dados(id):
        resultado = db_manager.deletar_dados(id)
        if resultado:
            return jsonify({'success': True, 'message': 'Dados removidos com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao remover dados'})
    
    return app

# ===== EXECUÇÃO PRINCIPAL =====
if __name__ == '__main__':
    print("🚀 Iniciando InsightPro AI - Versão Portável")
    print(f"📱 Ambiente detectado: {'Termux' if os.getenv('TERMUX_VERSION') else 'Padrão'}")
    print(f"💾 Banco de dados: {Config.DB_PATH}")
    
    app = criar_app()
    
    try:
        print(f"🌐 Servidor rodando em http://{Config.HOST}:{Config.PORT}")
        print("📊 Acesse /dashboard para ver o painel")
        print("🔧 Desenvolvido por Dione Castro Alves - InNovaIdeia")
        
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("💡 Verifique se a porta não está em uso e tente novamente")