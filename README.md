O Gemini disse
Este novo README.md foi estruturado para refletir a maturidade técnica do seu projeto após as atualizações. Ele destaca não apenas o código, mas a solução de negócio para a indústria, o que é fundamental para sua avaliação no SENAI e para seu perfil como Trainee de TI na JBS Seara.

Magistral - Sistema de Gestão Logística e Operacional Industrial
Descrição do Projeto
Este software é o resultado do Trabalho de Conclusão de Curso (TCC) desenvolvido no SENAI Campo Mourão - PR. O projeto surgiu como resposta a um desafio real do setor industrial frigorífico: a necessidade de integrar a logística de recepção de gado com a programação de abate, garantindo conformidade com normas de bem-estar animal e agilidade na comunicação entre setores.

O sistema gerencia o ciclo completo, desde a notificação de embarque pelo produtor até a visualização da programação de abate em monitores industriais no chão de fábrica.

Módulos do Sistema
1. Logística e Recebimento
Notificação de Embarque: Interface para o fornecedor registrar o lote, anexar Nota Fiscal e realizar busca inteligente de propriedades.

Controle de Bem-Estar Animal: O sistema calcula automaticamente o período obrigatório de 2 horas de descanso pré-abate a partir da confirmação da chegada física.

Validação de Dados: Implementação de travas de segurança para coleta de CNPJ (14 dígitos) e quantidades, impedindo a entrada de caracteres inválidos.

2. Monitor de Produção (Shop Floor Visibility)
Layout de Alta Visibilidade: Interface otimizada para visualização em TVs e monitores industriais espalhados pela planta.

Gestão à Vista: Exibição em tempo real do total de cabeças programadas para o dia e status de liberação por lote.

Especificação de Categoria: Identificação visual imediata do tipo de gado (Boi, Novilha ou Vaca) para ajuste da linha de produção.

Tecnologias e Arquitetura
Backend: Python 3.11 com framework Flask.

Banco de Dados: SQLite3 com normalização de dados (Busca insensível a caixa alta/baixa).

Frontend: HTML5, CSS3 e Bootstrap 5, utilizando unidades de medida relativas (VH/VW) para adaptação em grandes telas.

Fuso Horário: Sincronização obrigatória com o horário de Brasília via biblioteca pytz.

Cloud & Deploy: Sistema hospedado e operacional via PythonAnywhere.

Estrutura de Diretórios
Plaintext
├── app.py              # Lógica central e rotas do servidor
├── requirements.txt    # Dependências do sistema
├── .gitignore          # Filtro de arquivos sensíveis e banco de dados
├── templates/          # Arquivos HTML (Layouts e Monitores)
│   ├── producao.html   # Monitor de TV para o chão de fábrica
│   ├── dashboard.html  # Monitor de logística
│   └── ...             # Interfaces de cadastro e registro
└── static/             # Ativos estáticos (Logos e CSS)
    └── uploads/        # Repositório de Notas Fiscais (Armazenamento local)


Desenvolvedora:
Maysa Eduarda Lada
Maysa Eduarda
