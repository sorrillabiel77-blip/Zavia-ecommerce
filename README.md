# ZÁVIA v1.7 — Apresentação comercial + Checkout InfinitePay

**Base:** ZÁVIA v1.6.3 (Carrinho Corrigido). Esta entrega melhora a comunicação e a apresentação da loja **sem alterar a lógica de cobrança ou o banco de dados**.

## Melhorias para a cliente

- Removeu da vitrine, do carrinho, da página de produto e do checkout textos sobre "testes", "integração em andamento", "quando habilitado" e termos internos.
- Incluiu mensagens honestas de pagamento via **checkout da InfinitePay**, sem usar selos de certificação não fornecidos pelo provedor ou prometer segurança absoluta.
- Modernizou a barra superior e os ícones de conta e carrinho.
- Acrescentou etapas explicativas de compra na página inicial.
- Reorganizou o resumo final do checkout com valor das peças, frete e total.
- Melhorou a galeria de fotos, navegação mobile e acessibilidade.
- Criou a página pública **`/como-comprar/`**, explicando tamanhos, frete fixo, checkout InfinitePay e acompanhamento de pedidos.
- Preparou metadados Open Graph com a logo oficial para prévias de compartilhamento (a exibição depende de cada aplicativo e seu cache).
- Quando o checkout estiver desligado, mostra aviso neutro de indisponibilidade, sem linguagem de testes.

## O que ficou idêntico à v1.6.3

- Produtos reais, várias fotografias por produto e estoque por variação.
- Painel `/painel/` e Django Admin `/admin/`.
- Limpeza de produtos fictícios e sincronização do contador do carrinho.
- Frete fixo `ZAVIA_SHIPPING_FLAT`.
- InfinitePay: funções API, geração de links, webhook, verificação, controle de reserva.
- Variáveis do Render, migrações e PostgreSQL existentes.
- Logo oficial, favicon, cores champagne/nude/rosé.

**Esta versão não muda automaticamente** `ZAVIA_CHECKOUT_ENABLED`. Caso esteja `1`, clientes conseguem iniciar cobranças reais. Caso esteja `0`, verá mensagem temporária de indisponibilidade. Nunca compartilhe chaves API.

## Instalar mantendo os dados

1. Salve o commit de retorno da v1.6.3. Se existem pagamentos ou clientes, obtenha um backup restaurável do banco antes da mudança.
2. Extraia **o conteúdo** do ZIP e envie para a raiz do repositório GitHub conectado ao serviço `zavia-loja`. Nunca envie segredos de `.env` ao GitHub.
3. Confira `GitHub → Actions → ZAVIA - testes Django`: o job executa `manage.py check` e `manage.py test store`.
4. Com o CI aprovado, Render → `zavia-loja` → Manual Deploy → Deploy latest commit.
5. Confira páginas `/`, `/como-comprar/`, `/carrinho/`, `/finalizar/`, `/admin/` e `/painel/`.
6. Confirme o valor dos produtos e do frete, o redirecionamento InfinitePay e os registros de pedidos.

**Nenhuma migração nova:** o banco e os produtos já cadastrados não devem ser apagados por esta atualização (supondo que as migrações antigas já foram executadas).

## Validação e pendências

- Verificações locais: sintaxe Python e JavaScript, nomes de URLs, fechamento dos blocos de template, estrutura do ZIP e conferência por hash dos módulos de pagamento/estoque.
- Sem teste Django completo local (instalação de dependências indisponível); executar o CI antes do deploy.
- **Importante:** o redirecionamento InfinitePay ter funcionado **não comprova** que o pagamento, webhook, reembolso e reconciliação do estoque estão homologados. Acompanhe a primeira compra autorizada em ambos os painéis antes de declarar tudo pronto.
- Antes de receber vendas de clientes de verdade: publicar os dados comerciais aplicáveis e canal de contato, política de entrega e trocas/devoluções, política de privacidade e confirmar backups/infra de banco persistentes. Não foram inventados dados legais ou canais de atendimento.

Leia também **`CHECKLIST_LANCAMENTO.md`** para a próxima fase.
