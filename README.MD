# Automação de Leads - AIESEC no Rio de Janeiro 🌍

Este projeto automatiza o primeiro contato com leads qualificados para a AIESEC RJ, integrando a API do Podio com disparos de e-mail via SMTP (Gmail).

## 🚀 Funcionalidades
- Autenticação via OAuth2 com a API do Podio.
- Filtro automático de leads (Região: RJ / Status: OPEN).
- Disparo de e-mails personalizados para conversão em Marketing B2C.
- Sistema de log para evitar duplicidade de envios.
- Tratamento de exceções e erros de rede (SSL/Timeout).

## 🛠️ Tecnologias
- Python 3.13
- Biblioteca Requests (Consumo de API)
- SMTPLib (Envio de e-mails)
- Dotenv (Segurança de credenciais)
