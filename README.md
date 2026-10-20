# ZÁVIA v1.6.3 — Correção pontual do carrinho após exclusão de produtos

Esta versão é derivada **diretamente da v1.6.2** e conserva frete fixo, favicon oficial,
catálogo destinado aos produtos reais, galeria de fotos, painel administrativo e InfinitePay.

## Erro corrigido
Ao excluir ou desativar produtos no Admin, os identificadores permaneciam na sessão
`zavia_cart_v1`. O badge do cabeçalho contabilizava o conteúdo antigo da sessão,
independentemente da existência do produto no banco de dados. Por isso aparecia
"1" apesar de o catálogo estar vazio.

Agora tanto o contador quanto a página do carrinho consultam os SKUs ativos no
banco. Produtos/variações inexistentes ou desativados são removidos **automaticamente
da sessão** na próxima requisição. Itens ainda válidos permanecem, assim como seus
tamanhos, cores e quantidades. Produtos apenas esgotados permanecem visíveis, com aviso.
Entradas inválidas na sessão também são descartadas.

## Arquivos de código alterados
- `store/cart.py`: validação/sincronização da sessão com catálogo; contador consistente;
  normalização de valores e invalidação do cache de requisição ao alterar itens.
- `store/context_processors.py`: contador usa a mesma função de validação do carrinho.
- `store/tests.py`: testes de exclusão, arquivamento/desativação, alterações de variação,
  sessão inválida e preservação de produtos válidos.

Não foram feitas modificações nas migrações, no banco de dados, na identidade visual,
no frete, nos métodos de pagamento ou no painel administrativo.

## Atualização sem recriar a loja
1. Guarde o commit estável do GitHub; faça backup do banco se houver dados comerciais.
2. Extraia o ZIP e envie **seu conteúdo** ao mesmo repositório da ZÁVIA,
   mantendo os arquivos na raiz; evite excluir o repositório.
3. Confira GitHub Actions: `python manage.py test store`.
4. Se passar, no Render `zavia-loja` publique `Deploy latest commit`.
5. Abra a loja/carrinho: sem produtos cadastrados, o badge deve exibir **0**;
   ao cadastrar e adicionar um produto real ao carrinho, a contagem volta a funcionar.

**Mantenha `ZAVIA_CHECKOUT_ENABLED=0`.** Não é uma validação do pagamento InfinitePay.

Validação local: compilação de código, testes isolados da sincronização com modelos
simulados e conferência dos arquivos ZIP. A execução integral de Django cabe ao CI.
