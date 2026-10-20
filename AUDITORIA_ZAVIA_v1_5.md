# AUDITORIA TÉCNICA ZÁVIA | v1.5 (20/10/2026)

## Alcance e grau de comprovação

**Base analisada:** código integral da v1.4 entregue nesta conversa (Django, SQL migrations, Admin, URLs, HTML/CSS, formulário, carrinho e adaptador InfinitePay). Não houve acesso autenticado ao PostgreSQL, Render, InfinitePay ou código do repositório atualmente em produção. As imagens enviadas pelo lojista confirmam somente o carrinho, a página de checkout bloqueado, a inicialização do servidor e o deploy Live.

**Testes realizados neste ambiente:** inspeção estática e análise sintática de todos os Python após as alterações. Não foi possível instalar Django neste ambiente (rede de pacotes indisponível), portanto **não foram executados os testes Django, migrações reais, pagamentos, webhook ou testes de navegador da versão nova**. A configuração de CI no GitHub foi adicionada para executar `manage.py check` e os testes automatizados após o upload.

**Classificação:** a v1.5 é uma **candidata a homologação**, NÃO autoriza o lançamento público de cobranças.

## 1. Achados e correções

| Prioridade | Área | Achado objetivo | Medida na v1.5 | Pendência antes de vender |
|---|---|---|---|---|
| Alta | Exclusão de fictícios | `OrderItem.variant` tem `on_delete=PROTECT`: o Django não exclui produto cuja variação consta de pedido. Além disso, há imagens editoriais estáticas na home, que não são registros do banco. | Botão para arquivar fictícios no `/painel/` e ação no Admin para excluir fictícios com confirmação; produtos com histórico são arquivados. | Verificar no banco publicado se os produtos desejados são `is_demo=True`; fazer backup antes de apagar. |
| Alta | Estoque x falha de rede | v1.4 devolvia estoque automaticamente quando `create_payment_link` lançava exceção, mesmo em timeout incerto. | Falhas incertas mantêm reserva com estado `link_creation_uncertain`; conferência manual após período de segurança. Reservas criadas sem link salvo também exigem revisão. | Executar teste no PostgreSQL com falha de rede simulada, sem pagamentos reais. |
| Alta | Pagamento | Webhook confirma aprovação com `payment_check` autenticado e valor esperado, mas **não reconcilia automaticamente estorno/cancelamento** e não há teste de ponta a ponta com credenciais reais. | Nenhuma falsa confirmação; mantém checkout desligado. | Homologar pagamento Pix/cartão, recusas, estornos, atrasos e duplicatas antes de ativar. |
| Alta | Banco | Plano gratuito PostgreSQL do Render é inadequado para reter pedidos reais de forma durável sem plano de permanência/backup verificado. | Banco/migrações originais preservados. | Migrar para banco persistente com backup e política de restauração antes do lançamento real. |
| Alta | Produtos reais | `image_url` e galeria usam endereços externos/estáticos; não há armazenamento persistente de upload de imagens para produção. | Administração enfatiza URLs de imagem e múltiplas galerias. | Definir armazenamento durável (S3, Cloudinary ou serviço equivalente) antes de depender de uploads no Render. |
| Média | Painel | `/painel/` anterior tinha 4 números e poucos atalhos; pouca clareza entre pedidos e receita. | Novo painel responsivo, ações de catálogo, pedidos recentes, reservas, estoque baixo, distinção de produtos fictícios e reais. | Validar layout em mobile/desktop, acessos e permissões no Render. |
| Média | Admin | Django Admin padrão sem design consistente com a marca. | Marca ZÁVIA champagne/rosé, botões, tabelas e navegação customizadas. | Validar contraste e navegação em diferentes telas. |
| Média | Duplicidade de checkout | Postagens simultâneas com mesmo nonce podiam disputar reserva/violar unicidade. | Bloqueio transacional no registro do cliente e verificação de nonce existente. | Teste de concorrência real com PostgreSQL (SQLite não replica `SELECT FOR UPDATE`). |
| Média | Acesso | Cadastro/login ainda sem rate limiting, verificação de e-mail e mecanismo SMTP de recuperação verificado. | Não modificados sem serviço de e-mail. | Implementar proteção antiautomação, SMTP e proteção de dados. |
| Média | Comercial | Ausência de dados e políticas de troca/devolução, privacidade e canal de suporte publicados/validados. | Checklist documentado. | Preencher conteúdo real e revisar obrigações de comércio eletrônico. |
| Média | Segredos | Variáveis `ZAVIA_ADMIN_PASSWORD` e `ZAVIA_ADMIN_EMAIL` continuavam visíveis como chaves no Render nas capturas anteriores. | Rotina de bootstrap existente nunca troca senha de usuário presente. | Depois de confirmar acesso de admin, REMOVER as duas variáveis temporárias. Nunca printar valores. |
| Média | Catálogo | Banners e fotos editoriais da home são **estáticos**; apagar produtos no banco não remove imagens do layout. | Mantidas imagens para não quebrar identidade. | Decidir imagens comerciais definitivas e interface futura de edição de banners. |
| Média | Frete | Preço fixo (`ZAVIA_SHIPPING_FLAT`), não valida preço por CEP. | Mantido por decisão comercial do lojista. | Confirmar cobertura geográfica, prazos e preços reais sem fazer alegações automáticas. |

## 2. Funcionalidades efetivamente implementadas na v1.5

- `GET /painel/`: dashboard de gestão com produtos reais ativos, SKU/estoque, pedidos por situação, últimas vendas, estoque baixo e atalhos.
- `POST /painel/` com `action=archive_demos`: retira produtos `is_demo=True` da vitrine sem apagar pedidos nem produtos reais. Exige funcionário com permissão de alterar produtos e proteção CSRF.
- Django Admin / Produtos: filtros por fictício, criação de produtos reais com tamanhos/cores/SKU, edição, ações para arquivar, publicar real e **excluir fictícios sem histórico após confirmação textual**.
- Produtos fictícios com pedidos: ação de exclusão segura arquiva ao detectar `ProtectedError`, preservando `OrderItem` e informações fiscais/operacionais.
- Interface Django Admin modernizada por CSS próprio e link para `/painel/` e loja.
- Falhas desconhecidas ao criar link InfinitePay: mantêm estoque reservado e marcam necessidade de revisão em vez de presumir ausência de cobrança.
- Conferência manual segue sendo obrigatória para estoque preso por cobrança incerta; espera mínima de 24h após expiração do prazo.
- Workflow `.github/workflows/ci.yml` para rodar `python manage.py check` e testes Django em SQLite na branch `main`.

## 3. Padrões de segurança preservados

- Dados de pagamento sensíveis não são armazenados no banco ZÁVIA; API Key fica no Render.
- `ZAVIA_CHECKOUT_ENABLED=0` continua obrigatório durante homologação.
- Webhook sem autenticação inerente não é aceito como prova de pagamento; a confirmação depende de API autenticada e conferência de valor.
- Bloqueio transacional de estoque usa PostgreSQL em produção.
- Pedido e SKU com histórico não podem ser apagados indiscriminadamente.

## 4. Critérios de liberação de vendas (todos obrigatórios)

1. Fazer backup recuperável do banco atual, preservar commit anterior e desativar autodeploy antes de testar v1.5.
2. Subir v1.5 em ambiente de homologação ou em janela controlada, com checkout desligado; aguardar workflow **GitHub Actions** passar e Render ficar Live.
3. Validar Django Admin, exclusão/arquivamento demo, cadastramento de produto real, edição de preço, SKU e estoque em dispositivos desktop e celular.
4. Garantir imagens definitivas publicamente acessíveis em HTTPS e persistentes após novo deploy.
5. Garantir logística/frete e políticas de loja publicadas, contatos e informações comerciais corretas.
6. Conferir segurança de credenciais, cadastro/login, permissões; remover `ZAVIA_ADMIN_PASSWORD` do ambiente após primeiro uso.
7. Configurar banco com política efetiva de retenção e backups, adequada a pedidos e dados pessoais.
8. Testar com InfinitePay uma transação controlada, após cadastro de produto real, conferindo `order_nsu`, valor, link, webhooks, `payment_check`, pagamento, cancelamento, timeout e idempotência. Confirmar com painel do provedor.
9. Definir o tratamento para estornos/cancelamentos e estoque de pedidos pagos após cancelamento, bem como conciliação periódica (ainda pendente de implementação/homologação).
10. Habilitar o checkout público SOMENTE quando os itens anteriores forem comprovados e aprovados.

## 5. Como remover fictícios com segurança

Acesse `https://zavia-loja.onrender.com/painel/` como administrador. Clique em **Ocultar todos os fictícios**. Eles deixam de aparecer na vitrine sem qualquer exclusão irreversível.

Para excluir definitivamente: **Admin > Produtos > filtro 'Produto ilustrativo — não vender' = Sim > selecione os registros > ação 'Excluir fictícios selecionados SEM pedidos' > confirme**. Para cada produto protegido por pedido, a ação somente arquiva.

O banner da home e as imagens de categorias são estáticos; sua troca exige substituir os arquivos/HTML ou implementar gerenciador de banners. Não confunda os banners com o banco de produtos.

## 6. Estado de testes

- **Concluído neste ambiente:** `python -m compileall`, parse AST do código Python, integridade ZIP após empacotamento, inspeção de arquivos de configuração e migração.
- **Pendente de execução:** teste Django (`python manage.py test store`), verificação de migrações no Render/PostgreSQL, teste concorrente real, foto/arquivo persistente, API live da InfinitePay, fluxo de reembolso, auditoria de segurança dinâmica.

A liberação comercial não é recomendada enquanto esses bloqueios persistirem.
