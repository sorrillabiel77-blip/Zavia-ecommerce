# ZÁVIA v1.8 — Pacote consolidado para atualizar uma única vez

**Base funcional:** ZÁVIA v1.7.1, com identidade premium rosé/champagne. Esta atualização adiciona as informações institucionais que faltavam, com gerenciamento dos dados da loja no próprio Django Admin.

## Novidades públicas

- `/politica-de-entrega/`: frete fixo e condições de envio, com prazos editáveis no Admin.
- `/trocas-e-devolucoes/`: direito de arrependimento e orientações legais gerais, com procedimentos adicionais editáveis.
- `/politica-de-privacidade/`: dados utilizados pela loja e compra via InfinitePay, contato LGPD configurável.
- `/atendimento/`: WhatsApp, e-mail, Instagram, horário e identificação comercial, exibidos somente quando cadastrados.
- Rodapé organizado em **Explorar**, **Informações** e **Compra pela InfinitePay**.
- Links de políticas junto à finalização do pedido.
- Aparência e textos rosé/champagne preservados da v1.7.1.

## Como cadastrar os dados da loja (SEM atualizar GitHub novamente)

Entre em `/admin/` com o administrador da ZÁVIA:

1. Selecione **Informações comerciais e atendimento** > **Adicionar** (aparece só na primeira vez).
2. Cadastre **razão social e CNPJ (quando aplicável), endereço comercial, e-mail, WhatsApp, horário e Instagram**.
3. Preencha **origem do envio, preparação, previsão/condições de entrega e procedimento de trocas**.
4. Salve. A alteração aparece nas páginas públicas automaticamente, sem novo deploy.
5. Para editar posteriormente, acesse o mesmo item do Admin; apenas uma configuração pode ser criada no painel.

**Formato de WhatsApp:** `5511999999999` (55 + DDD + número; exemplo ilustrativo, NÃO é contato da ZÁVIA). Nunca cadastre credenciais InfinitePay nesta tela. Os tokens permanecem apenas no Render Environment.

## O que foi preservado

- Cadastro, contas, imagens reais e galeria, catálogo, tamanhos/cores e SKU.
- Carrinho sincronizado, frete fixo, pedidos e estoque.
- Pagamento via InfinitePay, webhook, confirmação, controle de reserva.
- Painel `/painel/`, Django Admin, favicon, logo oficial e paleta premium.
- Mesmo banco `zavia-db` e as mesmas variáveis de ambiente. **Não altera nenhum dado de produtos ou de pedidos.**

## Banco de dados

Há **somente uma migração nova e não destrutiva**, `store/migrations/0006_store_information.py`: ela cria a tabela de informações comerciais. A migração de limpeza do catálogo `0005` já deve estar aplicada na sua versão atual e NÃO é reexecutada em atualizações normais.

Se estiver atualizando a partir de uma versão mais antiga que ainda não executou a 0005, **NÃO faça deploy antes de revisar as migrações**: a 0005 apaga os produtos existentes. Evite confundir bancos ou branches diferentes.

## Implantação no GitHub + Render

1. Salve o commit funcional anterior e obtenha um **backup restaurável** do PostgreSQL (o Free do Render não fornece backup automático).
2. Extraia este ZIP e atualize a raiz do mesmo repositório GitHub da ZÁVIA.
3. Aguarde **GitHub > Actions**: `python manage.py check` e `python manage.py test store` devem passar.
4. Em Render > zavia-loja > Manual Deploy, use **Deploy latest commit** (se autodeploy estiver desligado).
5. Aguarde `Live`, confira `/admin/`, `/painel/`, catálogo, carrinho, checkout, imagens e as quatro páginas de informações.
6. No Admin, **cadastre os dados comerciais verdadeiros antes de divulgar a loja**.

O Render usa `build.sh`, que executa as migrações automaticamente. Não crie outra conta, outro projeto nem outro banco para aplicar esta versão.

## Segurança, transparência e condições antes de receber clientes

- **Não há mudança** em `ZAVIA_CHECKOUT_ENABLED`. Se estiver em `1`, a loja pode iniciar pagamentos reais. Ajuste essa variável conforme a etapa de homologação de cobranças.
- O redirecionamento bem-sucedido para a InfinitePay NÃO comprova que webhook, pagamento concluído, estorno e liberação de estoque foram todos testados.
- Sem razão social/identificação comercial, contato efetivo e informações verdadeiras sobre entrega, **a loja não deve ser divulgada ao público**.
- As páginas legais são modelos de informações gerais e devem ser revisadas à luz da operação real e da legislação aplicável. Não foram inventados dados da empresa, telefone, promessas de entrega ou selos de segurança.

## Validação incluída

- Sintaxe Python e JavaScript.
- Estrutura e nomes das quatro URLs.
- Arquivos críticos de pagamento, carrinho, fotos e estoque preservados byte a byte em relação à v1.7.1.
- Migração nova verificada para não conter exclusão de produtos.
- Testes automatizados adicionais para páginas e campos comerciais.

**Limite dos testes neste ambiente:** dependências Django indisponíveis localmente. O GitHub Actions deve aprovar os testes antes da implantação.

## Atualização v1.9 — pré-vendas

- Link **Sair** em todas as páginas quando a cliente está logada; formulário POST/CSRF.
- Minha conta > detalhes de pedido, histórico e solicitação de cancelamento pelo cliente.
- Admin > Pedidos: ações **Marcar preparação**, **Marcar enviado**, **Marcar entregue** e **Registrar reembolso** (este último somente após conferência manual na InfinitePay).
- Pedidos **não pagos**: continue usando a ação de cancelamento/verificação da InfinitePay após expiração + carência de 24h. A solicitação do cliente NÃO altera cobrança e NÃO repõe estoque antes dessa conferência.
- E-mails transacionais: fila no PostgreSQL e opção de envio via Gmail Apps Script desligada por padrão. Configuração em `integrations/EMAIL_SETUP.md`. Não precisa configurar Gmail para usar pedido/cancelamento no painel.
- Nova migração `store/migrations/0007_order_workflow_notifications.py` aditiva; preserva produtos, fotos, pedidos, banco e administrador existentes.
- **Antes de ativar vendas reais:** seguir `CHECKLIST_PRE_LANCAMENTO_v1_9.md` e testar pagamento aprovado, envio, cancelamento, estornos e recuperação de estoque. Uma atualização de código não comprova homologação real.
