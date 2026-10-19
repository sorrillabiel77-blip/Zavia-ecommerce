# ZÁVIA — E-commerce Fitness Feminino | v1.0 (Django + Render)

**Esta é uma aplicação Python REAL, diferente da prévia estática anterior.**
Usa Django, produtos/categorias/variações em banco, sessões, carrinho, cadastro/login, dashboard e Django Admin.
Utiliza a logo oficial ZÁVIA e campanha visual demonstrativa.

## O que funciona nesta entrega
- Loja pública responsiva, buscas e filtros por categoria.
- Catálogo editável, preços, descrição e imagens por URL.
- SKU + tamanho + cor + estoque por variação, gerenciados no painel.
- Registro de clientes, login, sessões, carrinho persistente após login.
- Painel `/painel/` (apenas staff) + Django Admin `/admin/` (usuário admin).
- Migração de banco versionada e 6 produtos *demonstrativos*, cadastrados de modo idempotente.
- Preparação PostgreSQL no Render. Arquivos CSS e imagens coletados por WhiteNoise.

## O que AINDA NÃO funciona (não confundir com loja pronta para vender)
- Pagamento Mercado Pago, PIX/cartão/boleto, webhooks e pedidos pagos.
- Cálculo real de frete, rastreamento e faturamento real.
- Upload persistente de mídia (Render tem armazenamento efêmero por padrão; use URLs externas permanentes ou configure storage antes de fotos definitivas).
- Recuperação de senha por e-mail, cupons, avaliações, LGPD/políticas completas.
- Reservas de estoque, concorrência em checkout e processamento de pedidos.
A página de checkout explica claramente que **pagamentos não estão ativos**.

## Deploy RECOMENDADO no Render com um Blueprint

**Atenção: o antigo serviço `Static Site` não suporta esta versão Django.**
Crie um novo **Web Service Python**, ou use a opção **New > Blueprint**. O ZIP só é entregue para facilitar o envio: não é enviado diretamente ao Render.

1. Extraia todo o ZIP no Windows.
2. Crie um novo repositório GitHub (recomendado `zavia-ecommerce`, evitando confusão com o `zaviasite` estático).
3. Faça upload de **todos os arquivos e pastas extraídos**, mantendo `render.yaml`, `manage.py`, `build.sh` e `requirements.txt` na RAIZ. Não envie apenas o ZIP nem crie uma pasta extra no repositório.
4. Em https://dashboard.render.com abra **New > Blueprint**.
5. Conecte o repositório e confirme os recursos propostos: `zavia-loja` (Web Python) e `zavia-db` (Postgres).
6. Verifique eventuais custos e limitações do plano Render antes de clicar **Apply**. Os recursos free podem ter suspensão/expiração e não são recomendados como infraestrutura de uma loja em produção.
7. Aguarde: o Render executa `bash build.sh` para instalar dependências, publicar estáticos e migrar/sementar o banco.
8. Abra o endereço `.onrender.com` fornecido pelo Render e verifique `/health/`.

### Criar usuário do painel no Render
No ambiente local, use `python manage.py createsuperuser`.
No Render, execute o comando `python manage.py createsuperuser` em um console/shell do serviço (a disponibilidade do shell depende do plano). Se não houver shell, conecte-se ao PostgreSQL a partir de uma máquina local de confiança com `DATABASE_URL` **mantida em segredo**, rode `python manage.py createsuperuser` e encerre a conexão segura. Outra alternativa é um **job administrativo de execução única** configurado de modo seguro — nunca deixe senhas fixas no código nem publique scripts de superusuário.

### Forma fácil de ativar o painel sem shell no Render
No serviço **zavia-loja > Environment**, adicione temporariamente:
- `ZAVIA_ADMIN_EMAIL` = seu e-mail de administração.
- `ZAVIA_ADMIN_PASSWORD` = uma senha forte, exclusiva, com 12+ caracteres.

Em **Manual Deploy > Deploy latest commit**, o comando `bootstrap_admin` criará
um único superusuário caso ainda não exista nenhum. Depois que conseguir fazer
login em `/admin/`, **exclua as duas variáveis do Render** (sem apagar o usuário
no banco). O comando nunca mostra a senha nos logs e nunca altera senhas existentes.
Não use senha repetida nem coloque as variáveis no GitHub ou no ZIP.

### Alternativa: Web Service manual
- Runtime: Python
- Branch: `main`
- Root Directory: vazio
- Build Command: `bash build.sh`
- Start Command: `gunicorn zavia.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- `DATABASE_URL`: string privada de conexão de banco PostgreSQL existente
- `SECRET_KEY`: chave secreta longa, gerada no Render
- `DEBUG`: `0`
- **Nunca selecionar `Static Site` para este ZIP.**

## Testar no Windows localmente
Requer Python 3.11+ e conexão à internet para instalar bibliotecas.
Abra o terminal na pasta extraída:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DEBUG="1"
py manage.py migrate
py manage.py seed_demo
py manage.py createsuperuser
py manage.py runserver
```

Acesse `http://127.0.0.1:8000/` (loja) e `http://127.0.0.1:8000/admin/` (painel).
Testes automatizados: `py manage.py test`.

## Sobre o design
A marca, logo e paleta oficial champagne/nude/rosé/preto estão incluídas. Fotografias de campanha e preços são ilustrações; devem ser substituídos por produtos reais antes da operação. Não utilize demo como catálogo comercial real.

## Segurança / migrações
- `SECRET_KEY` e `DATABASE_URL` são variáveis de ambiente; arquivo `.env` não vai para GitHub.
- `DEBUG=0`, HTTPS, CSRF e cookies seguros no Render.
- Os arquivos `store/migrations/` registram o esquema v1; usar `python manage.py makemigrations` apenas após mudanças nos modelos.
- Não use uploads locais do Django no Render como armazenamento definitivo. Preferir serviço de objetos (S3/R2 etc.).
- Backup de banco e termos/políticas comerciais devem ser configurados antes de liberar pagamento real.

## Próximas entregas
1. Integração Mercado Pago segura (Checkout Pro ou API oficial) com webhook, idempotência e validação.
2. Frete e endereços persistentes.
3. Checkout com transação e reserva de estoque.
4. Análises financeiras sem dados fictícios.
5. Armazenamento de imagens, testes end-to-end, revisão jurídica.

**Nota de QA desta entrega:** o código contém testes Django em `store/tests.py`, mas a execução depende de instalar as dependências (PyPI/Render). A validação local estática não substitui um teste end-to-end no Render.
