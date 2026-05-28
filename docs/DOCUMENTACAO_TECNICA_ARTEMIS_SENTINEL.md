# Documentação Técnica — ARTEMIS Sentinel

## 1. Identificação do projeto

**Projeto:** ARTEMIS Sentinel — AI-RPA Mission Validation System  
**Disciplina:** AI for RPA — Global Solution 2026  

| Integrante | RM |
|---|---|
| Augusto Codo | RM 562080 |
| Felipe Cabral | RM 561720 |
| Sofia Souza | RM 565818 |

---

## 2. Objetivo

O ARTEMIS Sentinel é um sistema AI-RPA para validação operacional de uma missão lunar simulada.  
O projeto automatiza a coleta de dados externos, geração de telemetria sintética, validação de regras, cálculo de risco, detecção de anomalias, persistência em SQLite, geração de Excel e visualização em dashboard.

O objetivo principal é demonstrar um fluxo RPA completo com uso de APIs, banco de dados, relatórios, dashboard e inteligência local.

---

## 3. Aviso técnico

A missão, a telemetria e a trajetória Terra–Lua exibida no dashboard são simuladas.

O projeto **não realiza cálculo orbital real**, não executa código histórico da Apollo 11 e não representa uma missão espacial real.

As APIs NASA POWER e NASA DONKI são usadas como fontes externas reais quando disponíveis.

---

## 4. Arquitetura geral

O fluxo principal do sistema é:

```text
Configuração (.env)
        │
        ▼
Coleta NASA POWER / NASA DONKI
        │
        ▼
Geração de telemetria simulada
        │
        ▼
Validação de regras operacionais
        │
        ▼
Motor de risco + ML local
        │
        ▼
SQLite + Excel + Dashboard
```

Principais arquivos:

| Arquivo/Pasta | Função |
|---|---|
| `main.py` | Execução via terminal |
| `app.py` | Dashboard Streamlit |
| `src/pipeline.py` | Orquestração principal |
| `src/collectors/` | Coletores NASA POWER e NASA DONKI |
| `src/telemetry/` | Simulador de telemetria |
| `src/intelligence/` | Validações, risco e ML |
| `src/database.py` | Persistência SQLite |
| `src/reports/` | Geração de Excel |
| `src/notifications/` | E-mail SMTP opcional |
| `tests/` | Testes automatizados |

---

## 5. Fontes de dados

### NASA POWER

Usada para obter dados ambientais associados ao local configurado.

O sistema pode operar em:

- `NASA_POWER_LIVE`: quando a API responde corretamente;
- `NASA_POWER_FALLBACK`: quando há falha de rede, dados inválidos ou indisponibilidade.

### NASA DONKI

Usada para consultar eventos solares, principalmente flares solares.

O sistema pode operar em:

- `NASA_DONKI_LIVE`: quando a API responde corretamente;
- `NASA_DONKI_FALLBACK`: quando há falha de rede, chave ausente ou resposta inválida.

### Telemetria simulada

A telemetria da missão é sintética e gerada localmente.  
Ela contém métricas como bateria, oxigênio, combustível, pressão de cabine, temperatura, radiação, latência, sinal, altitude e velocidade.

---

## 6. Validação operacional

O sistema valida cada amostra de telemetria com regras de negócio.

Exemplos de métricas monitoradas:

- bateria;
- oxigênio;
- combustível;
- radiação;
- força do sinal;
- temperatura do motor;
- pressão da cabine;
- temperatura da cabine;
- latência de comunicação.

Os alertas podem ter severidade:

| Severidade | Significado |
|---|---|
| `WARNING` | Atenção operacional |
| `CRITICAL` | Condição crítica |

---

## 7. Motor de risco

O motor de risco calcula um score de 0 a 100 e classifica a missão.

| Risk Level | Score |
|---|---|
| `LOW` | 0–24 |
| `MODERATE` | 25–49 |
| `HIGH` | 50–74 |
| `CRITICAL` | 75–100 |

Status possíveis:

| Status | Significado |
|---|---|
| `GO` | Operação estável |
| `GO WITH CAUTION` | Operação permitida com cautela |
| `WARNING` | Risco elevado ou muitas advertências |
| `NO-GO` | Missão não recomendada |

Regra defensiva:

- `NO-GO` ocorre com 3 ou mais alertas críticos;
- ou com `risk_level == CRITICAL` e pelo menos 1 alerta crítico;
- risco crítico sem alerta crítico vira `WARNING`, não `NO-GO`.

---

## 8. Machine Learning local

O projeto usa `IsolationForest` para detectar anomalias multivariadas na telemetria simulada.

Arquivo:

```text
src/intelligence/ml_anomaly_detector.py
```

Campos gerados:

| Campo | Descrição |
|---|---|
| `ml_model_name` | Nome do modelo usado |
| `ml_source` | Origem da análise |
| `ml_anomaly_score` | Intensidade média das anomalias |
| `ml_anomaly_count` | Quantidade de anomalias |
| `ml_anomaly_ratio` | Proporção de anomalias |

Caso `scikit-learn` não esteja disponível, o sistema usa fallback estatístico baseado em Z-score.

---

## 9. Persistência e relatórios

### SQLite

O sistema grava evidências locais em SQLite.

Principais tabelas:

- `telemetry`;
- `alerts`;
- `mission_summary`;
- `external_data`;
- `email_notifications`.

O banco é gerado localmente em:

```text
database/artemis_sentinel.db
```

Esse arquivo não deve ser versionado no Git.

### Excel

O relatório Excel é gerado em:

```text
data/reports/
```

Abas principais:

- `mission_summary`;
- `telemetry`;
- `alerts`;
- `external_data`.

Os arquivos Excel também não devem ser versionados.

---

## 10. Dashboard

O dashboard foi desenvolvido com Streamlit.

Comando:

```bash
streamlit run app.py
```

Ele exibe:

- cards de status;
- score de risco;
- alertas;
- gráficos de telemetria;
- fontes NASA;
- resultado do ML;
- trajetória conceitual Terra–Lua;
- download do Excel;
- envio de e-mail opcional.

---

## 11. E-mail opcional

O sistema possui envio de e-mail via SMTP.

Arquivo:

```text
src/notifications/email_report.py
```

Por padrão, fica desabilitado:

```env
EMAIL_ENABLED=false
```

Para ativar, é necessário configurar no `.env` local:

```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_APP_PASSWORD=sua_senha_de_app
ALERT_EMAIL_TO=email_destino@gmail.com
SEND_EXCEL_ATTACHMENT=true
```

A senha deve ser uma senha de app, nunca a senha normal da conta.

---

## 12. Segurança

Boas práticas aplicadas:

- `.env` não versionado;
- `.env.example` com `NASA_API_KEY=DEMO_KEY`;
- chave NASA não aparece em logs, Excel, SQLite ou dashboard;
- credenciais SMTP não são impressas;
- arquivos gerados são ignorados pelo Git;
- testes validam ausência de segredos em artefatos.

---

## 13. Testes

O projeto possui testes automatizados com `pytest`.

Comando:

```bash
python -m pytest -q
```

Última validação registrada:

```text
55 passed
```

Os testes cobrem:

- coletores NASA;
- fallback;
- telemetria;
- validações;
- motor de risco;
- ML;
- Excel;
- SQLite;
- dashboard;
- e-mail;
- segurança.

---

## 14. Limitações

- A telemetria é simulada.
- A trajetória Terra–Lua é apenas visual/conceitual.
- O sistema não calcula órbita real.
- As APIs NASA podem operar em fallback dependendo da rede ou chave.
- O ML detecta anomalias operacionais, não prevê eventos espaciais reais.

---

## 15. Conclusão

O ARTEMIS Sentinel demonstra um pipeline AI-RPA completo para validação operacional simulada, integrando APIs externas, regras de negócio, ML local, banco SQLite, Excel, dashboard e boas práticas de segurança.

O projeto é adequado para fins acadêmicos e demonstra rastreabilidade, automação e análise de risco em um cenário inspirado em missões espaciais.
```

