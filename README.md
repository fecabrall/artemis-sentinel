# 🚀 ARTEMIS Sentinel — AI-RPA Mission Validation System

> **Global Solution 2026 — AI for RPA**
> Sistema AI-RPA para validação operacional de uma missão lunar simulada, integrando telemetria sintética, APIs da NASA, motor de risco, ML local, dashboard, SQLite, Excel e notificações opcionais.

---

# 📑 Sumário

* [👥 Equipe](#-equipe)
* [🎯 Visão Geral](#-visão-geral)
* [⚠️ Aviso Técnico](#️-aviso-técnico)
* [🧠 Funcionalidades](#-funcionalidades)
* [🏗️ Arquitetura](#️-arquitetura)
* [🧩 Stack Técnica](#-stack-técnica)
* [🛰️ Integrações NASA](#️-integrações-nasa)
* [🤖 Machine Learning](#-machine-learning)
* [📊 Critérios de Risco](#-critérios-de-risco)
* [💻 Execução](#-execução)
* [📈 Dashboard](#-dashboard)
* [📄 Relatório Excel](#-relatório-excel)
* [📧 Notificações SMTP](#-notificações-smtp)
* [🧪 Testes Automatizados](#-testes-automatizados)
* [🔐 Segurança](#-segurança)
* [📚 Documentação Técnica](#-documentação-técnica)
* [🛠️ Troubleshooting](#️-troubleshooting)
* [📄 Licença](#-licença)

---

# 👥 Equipe

| Nome          | RM        |
| ------------- | --------- |
| Augusto Codo  | RM 562080 |
| Felipe Cabral | RM 561720 |
| Sofia Souza   | RM 565818 |

---

# 🎯 Visão Geral

O **ARTEMIS Sentinel** é um sistema desenvolvido para a **Global Solution 2026** na disciplina de **AI for RPA**.

O projeto simula um pipeline operacional de validação de missão Terra–Lua com automação completa de análise, monitoramento e tomada de decisão baseada em risco.

```text
NASA POWER + NASA DONKI
          │
          ▼
Telemetria simulada
          │
          ▼
Validações operacionais
          │
          ▼
Motor de risco + ML local
          │
          ▼
SQLite + Excel + Dashboard + SMTP
```

O sistema possui dois modos principais de operação:

| Modo     | Comando                    |
| -------- | -------------------------- |
| Normal   | `python main.py`           |
| Anomalia | `python main.py --anomaly` |

---

# ⚠️ Aviso Técnico

O ARTEMIS Sentinel utiliza elementos reais, simulados e referenciais.

| Elemento            | Tipo                    |
| ------------------- | ----------------------- |
| Telemetria          | `TELEMETRY_SIMULATED`   |
| Dashboard Terra–Lua | Visualização conceitual |
| NASA POWER          | API real                |
| NASA DONKI          | API real                |
| Apollo 11           | Referência histórica    |
| ML local            | Detecção de anomalias   |

> O objetivo do projeto é validar operações simuladas utilizando AI-RPA, e não realizar cálculos orbitais reais.

---

# 🧠 Funcionalidades

* Simulação operacional por fases:

  * `PRE_LAUNCH`
  * `LAUNCH`
  * `TRANS_LUNAR_INJECTION`
  * `CRUISE`
  * `LUNAR_ORBIT`
  * `DESCENT`
  * `LANDING`
* Integração com NASA POWER.
* Integração com NASA DONKI.
* Sistema de fallback local.
* Motor de validação operacional.
* Sistema de alertas:

  * `WARNING`
  * `CRITICAL`
* Score de risco de `0` a `100`.
* Status operacional:

  * `GO`
  * `GO WITH CAUTION`
  * `WARNING`
  * `NO-GO`
* Machine Learning local com `IsolationForest`.
* Fallback estatístico com `Z-score`.
* Dashboard interativo com Streamlit.
* Persistência SQLite.
* Exportação Excel multiaba.
* Notificações SMTP opcionais.
* Testes automatizados com `pytest`.

---

# 🏗️ Arquitetura

```text
artemis-sentinel/
├── main.py
├── app.py
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
│
├── data/
│   ├── fallback/
│   ├── raw/
│   ├── processed/
│   └── reports/
│
├── database/
├── logs/
│
├── src/
│   ├── collectors/
│   ├── telemetry/
│   ├── intelligence/
│   ├── notifications/
│   ├── reports/
│   ├── utils/
│   ├── config.py
│   ├── database.py
│   ├── logger.py
│   └── pipeline.py
│
├── tests/
└── docs/
```

---

# 🧩 Stack Técnica

| Camada      | Tecnologia         |
| ----------- | ------------------ |
| Linguagem   | Python 3.11+       |
| Dados       | pandas             |
| APIs        | requests           |
| Ambiente    | python-dotenv      |
| Dashboard   | Streamlit + Plotly |
| Banco local | SQLite             |
| Excel       | openpyxl           |
| ML          | scikit-learn       |
| Testes      | pytest             |

---

# 🛰️ Integrações NASA

## NASA POWER

Coleta de dados ambientais associados ao ponto geográfico configurado.

### Metadados

| Campo           | Exemplo           |
| --------------- | ----------------- |
| `source`        | `NASA_POWER_LIVE` |
| `records_count` | `7`               |
| `fallback_used` | `false`           |

---

## NASA DONKI

Consulta de eventos solares relevantes para análise operacional.

### Metadados

| Campo           | Exemplo           |
| --------------- | ----------------- |
| `source`        | `NASA_DONKI_LIVE` |
| `event_count`   | `9`               |
| `fallback_used` | `false`           |

---

## Modos de dados

| Modo                  | Significado               |
| --------------------- | ------------------------- |
| `NASA_POWER_LIVE`     | Dados reais da NASA POWER |
| `NASA_POWER_FALLBACK` | Fallback local            |
| `NASA_DONKI_LIVE`     | Dados reais da NASA DONKI |
| `NASA_DONKI_FALLBACK` | Fallback local            |
| `TELEMETRY_SIMULATED` | Telemetria sintética      |
| `READ_ONLY_REFERENCE` | Referência histórica      |

---

# 🤖 Machine Learning

O sistema utiliza:

```text
IsolationForest
```

Objetivo:

> Detectar desvios operacionais em telemetria simulada.

### Métricas analisadas

* bateria;
* oxigênio;
* combustível;
* pressão;
* temperatura;
* radiação;
* latência;
* sinal;
* velocidade;
* altitude.

### Campos ML

| Campo              | Descrição                 |
| ------------------ | ------------------------- |
| `ml_model_name`    | Modelo utilizado          |
| `ml_anomaly_score` | Intensidade das anomalias |
| `ml_anomaly_count` | Quantidade detectada      |
| `ml_anomaly_ratio` | Proporção de anomalias    |

---

# 📊 Critérios de Risco

## Classificação

| Risk Level | Score  |
| ---------- | ------ |
| `LOW`      | 0–24   |
| `MODERATE` | 25–49  |
| `HIGH`     | 50–74  |
| `CRITICAL` | 75–100 |

---

## Status operacional

| Status            | Interpretação          |
| ----------------- | ---------------------- |
| `GO`              | Operação estável       |
| `GO WITH CAUTION` | Operação monitorada    |
| `WARNING`         | Alto risco operacional |
| `NO-GO`           | Missão não autorizada  |

---

# 💻 Execução

## Clonar projeto

```bash
git clone <repo_url>
cd artemis-sentinel
```

---

## Criar ambiente virtual

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Configurar ambiente

Criar arquivo `.env`:

```env
NASA_API_KEY=DEMO_KEY
EMAIL_ENABLED=false
```

---

## Validar APIs NASA

```bash
python -m src.utils.verify_nasa_live
```

---

## Executar testes

```bash
python -m pytest -q
```

---

## Executar pipeline

### Modo normal

```bash
python main.py
```

### Modo anomalia

```bash
python main.py --anomaly
```

---

## Executar dashboard

```bash
streamlit run app.py
```

---

# 📈 Dashboard

O dashboard inclui:

* status operacional;
* score de risco;
* alertas;
* telemetria;
* visualização Terra–Lua;
* gráficos operacionais;
* dados NASA;
* métricas ML;
* exportação Excel;
* envio opcional por e-mail.

> A trajetória exibida é conceitual e não representa cálculo orbital real.

---

# 📄 Relatório Excel

Os relatórios são exportados automaticamente em:

```text
data/reports/
```

### Abas geradas

| Aba               | Conteúdo               |
| ----------------- | ---------------------- |
| `mission_summary` | Sumário da missão      |
| `telemetry`       | Telemetria detalhada   |
| `alerts`          | Alertas operacionais   |
| `external_data`   | Dados NASA e metadados |

---

# 📧 Notificações SMTP

Configuração via `.env`:

```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_APP_PASSWORD=sua_senha_de_app
ALERT_EMAIL_TO=destino@gmail.com
SEND_EXCEL_ATTACHMENT=true
```

### Status possíveis

| Status           | Descrição               |
| ---------------- | ----------------------- |
| `skipped`        | Envio desabilitado      |
| `missing_config` | Configuração incompleta |
| `sent`           | E-mail enviado          |
| `failed`         | Falha tratada           |

---

# 🧪 Testes Automatizados

Execução:

```bash
python -m pytest -q
```

Cobertura principal:

* APIs NASA;
* fallback;
* telemetria;
* ML;
* SQLite;
* Excel;
* dashboard;
* SMTP;
* pipeline integrado.

---

# 🔐 Segurança

## Arquivos ignorados

```text
.env
.venv/
__pycache__/
.pytest_cache/
database/*.db
logs/*.log
data/reports/*.xlsx
```

---

## Arquivos versionados

```text
README.md
requirements.txt
pytest.ini
main.py
app.py
src/
tests/
docs/
data/fallback/
```

---

# 📚 Documentação Técnica

Arquivos disponíveis em `docs/`:

| Arquivo                                 | Finalidade                  |
| --------------------------------------- | --------------------------- |
| `RELATORIO_TECNICO_ARTEMIS_SENTINEL.md` | Relatório técnico           |
| `RELATORIO_FINAL_VALIDACAO.md`          | Evidências de validação     |
| `PDD_ARTEMIS_SENTINEL.md`               | Process Definition Document |
| `SDD_ARTEMIS_SENTINEL.md`               | Software Design Document    |
| `POP_ARTEMIS_SENTINEL.md`               | Procedimento Operacional    |
| `ROTEIRO_PITCH_ARTEMIS_SENTINEL.md`     | Pitch técnico               |
| `COMO_EXPORTAR_DOCUMENTACAO.md`         | Exportação DOCX/PDF         |

---

# 🛠️ Troubleshooting

| Problema                 | Solução                  |
| ------------------------ | ------------------------ |
| `ModuleNotFoundError`    | Ativar `.venv`           |
| DONKI fallback constante | Verificar `NASA_API_KEY` |
| Streamlit não inicia     | Alterar porta            |
| SQLite ausente           | Executar pipeline        |
| Excel não gerado         | Rodar pipeline/dashboard |

---

# 📄 Licença

Projeto acadêmico desenvolvido para a **FIAP — Global Solution 2026 — AI for RPA**.

Uso exclusivamente educacional.
