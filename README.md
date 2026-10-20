# ZÁVIA — E-commerce v1.3 • InfinitePay (integração experimental)

Atualização do projeto Django publicado no Render. **Não altere o banco `zavia-db` e não mude a Gucci Cremas**. Esta versão preserva a migração `0002_mercadopago_checkout.py` por compatibilidade histórica: o nome da migração não determina o gateway ativo.

## O que foi trocado
- Sai o adaptador Mercado Pago. Entra **InfinitePay Checkout Integrado** (`store/infinitepay.py`).
- A cliente seleciona itens e endereço na ZÁVIA; o servidor gera um link de pagamento pelo endpoint `https://api.checkout.infinitepay.io/links`.
- A InfinitePay retorna uma URL de checkout. Um webhook ou retorno passa identificadores; o servidor **sempre consulta o status via API autenticada `/payment_check`**, confere o pedido e total (centavos) antes de registrar pagamento.
- Pix e cartão dependem de disponibilidade/configurações InfinitePay.
- As cobranças ficam **desligadas** por padrão (`ZAVIA_CHECKOUT_ENABLED=0`).

## Como atualizar mantendo seus dados
1. Faça um backup do PostgreSQL da ZÁVIA antes de modificar a aplicação.
2. Envie os arquivos e pastas deste ZIP para o repositório GitHub da ZÁVIA, substituindo os anteriores. **Não** exclua o banco existente.
3. O Render fará o deploy e executará as migrações (`build.sh`). O arquivo `render.yaml` permanece conectado ao mesmo serviço e mesmo banco.
4. Teste `/health/`, `/admin/`, carrinho e páginas de produtos; mantenha o checkout desligado.
5. Abra o app InfinitePay > Vendas > Checkout > Configurações > Habilitar Checkout Integrado e gere uma API Key (documentação oficial: https://ajuda.infinitepay.io/pt-BR/articles/10766888-como-usar-o-checkout-integrado-da-infinitepay).
6. No Render > `zavia-loja` > Environment, configure:
   - `INFINITEPAY_TAG`: sua InfiniteTag, sem `$`.
   - `INFINITEPAY_API_KEY`: segredo `inchk_...` criado no aplicativo InfinitePay. **Não publique**.
   - `ZAVIA_SHIPPING_FLAT`: frete fixo para testes, por exemplo `12.00` (em reais, decimal com ponto).
   - `ZAVIA_CHECKOUT_ENABLED`: mantenha `0` enquanto os testes não forem concluídos.
7. A URL que o backend envia ao gateway é `https://zavia-loja.onrender.com/pagamento/webhook/`. O provedor notifica a cada link pela configuração `webhook` enviada ao criar o checkout.
8. A API pode receber `order_nsu` no retorno (formato `ZAVIA-123`) e não aceita parâmetro de URL como prova de quitação.

## Antes de vendas reais
**NÃO ativar o checkout apenas porque o deploy subiu.** Precisamos verificar:
- habilitação real da API Key, estrutura de respostas e notificações da sua conta InfinitePay;
- ciclo de checkout fim-a-fim com transação real de valor pequeno e estorno;
- cálculo/contratação do frete para CEPs reais (nesta versão, frete FIXO sem cotação);
- produtos reais com preços, disponibilidade e fotos adequados (`is_demo=True` bloqueia venda);
- cancelamentos e estornos, especialmente reconciliação de reservas de estoque de pedidos abandonados (pendência da v1.2).

### Configuração do Render
Não precisa criar novos serviços ou bancos. `render.yaml`, `requirements.txt`, `manage.py` e `build.sh` permanecem na raiz.

### Limitações técnicas de segurança
A documentação oficial do webhook InfinitePay não descreve assinatura para esta interface; o sistema trata **todo webhook como não confiável** e exige confirmação no endpoint autenticado `payment_check` com a API Key. Eventos de reembolso não alteram automaticamente o status do pedido; exigem conferência administrativa. **Sem testes reais, não há garantia de compatibilidade operacional em produção.**

Links oficiais:
- https://www.infinitepay.io/checkout-documentacao
- https://ajuda.infinitepay.io/pt-BR/articles/10766888-como-usar-o-checkout-integrado-da-infinitepay
