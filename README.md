# ZÁVIA v1.6.1 — somente catálogo vazio e fotos reais

Esta atualização modifica **somente** a limpeza dos produtos antigos e o cadastro de fotos. O restante da v1.5 (layout, painel, InfinitePay, frete, autenticação, banco e URLs) permanece igual.

## O que acontece no primeiro deploy

- A migração `0005_limpeza_unica_catalogo` remove **TODOS** os produtos atualmente cadastrados, inclusive fictícios e reais anteriores, junto com variações e respectivas fotos. A exclusão não deixa produtos antigos arquivados no Admin.
- **Categorias, clientes e pedidos NÃO são apagados.** Se existirem pedidos antigos, a descrição, o SKU, a quantidade e o preço permanecem no histórico, mas a referência à variação antiga fica vazia (`NULL`).
- O catálogo público e a administração de **Produtos** começarão com zero itens.
- A limpeza roda **uma única vez**. Nenhum produto novo será apagado em futuras implantações.
- Imagens estáticas de produtos fictícios foram removidas da vitrine. A logo oficial continua.

**ATENÇÃO:** a remoção de todos os produtos antigos é permanente. Verifique antes que não haja pagamentos em aberto ligados a eles, e salve um backup antes de publicar. Se já implantou o ZIP v1.6 anterior, consulte o histórico de migrações antes de instalar esta revisão: a migração `0005` que já rodou não executa novamente.

## Como cadastrar seus produtos COM suas fotos

1. Acesse `https://zavia-loja.onrender.com/admin/`.
2. Entre em **Produtos → Adicionar produto**.
3. Preencha nome, categoria, preço, descrição e estoque nas variações.
4. No fim da página, na seção **Fotos reais**, clique em **Selecionar arquivo** e escolha uma foto JPG/PNG/WebP do seu aparelho.
5. Use **Adicionar outra Imagem de produto** para enviar a segunda, terceira e outras fotos.
6. Coloque **Posição 0** na foto principal, 1 na seguinte, 2 na próxima etc.
7. Salve. Todas as fotos aparecerão na galeria da página do produto.

Nesta versão de teste, as novas fotos ficam gravadas em formato WebP otimizado no PostgreSQL, não no disco temporário do Render. **Não guardamos nem reutilizamos fotos de produtos antigos.** Novas fotos precisam ser armazenadas para a loja poder mostrá-las.

**Limitação do Render Free:** o banco de testes possui prazo de validade e não substitui um armazenamento duradouro para fotos. Não libere vendas reais sem validar pagamentos, backups e armazenamento permanente.

## Atualização e checagem

1. Preserve um backup/commit anterior. Confirme que deseja excluir permanentemente TODO o catálogo antigo.
2. Extraia o ZIP e envie os arquivos à raiz do GitHub da ZÁVIA. Espere os testes em GitHub Actions passarem.
3. Faça o deploy no Render, confirmando a execução da migração 0005.
4. Confira **Produtos = 0** em `/admin/store/product/`, a vitrine vazia e `/health/` respondendo `ok`.
5. Cadastre um produto real com duas fotos e confira a capa e as miniaturas na loja.

Mantenha `ZAVIA_CHECKOUT_ENABLED=0` por enquanto; nenhuma alteração foi feita ao módulo de pagamento.
