-- Operações de consulta no banco de dados

-- Consulta 1 (com JOIN): Listar todos os livros e seus autores, junto com o nome do usuário que os adicionou.
-- Usando INNER JOIN entre material_bibliografico, livro e usuario.
SELECT
    mb.titulo,
    mb.autor,
    l.genero,
    u.nome AS adicionado_por
FROM material_bibliografico mb
INNER JOIN livro l ON mb.id = l.id
INNER JOIN usuario u ON mb.usuario_id = u.id;

-- Consulta 2 (com JOIN): Contar quantos materiais de cada categoria foram adicionados por cada usuário.
-- Usando GROUP BY para agregação e JOIN entre usuario e material_bibliografico.
SELECT
    u.nome AS usuario,
    mb.categoria,
    COUNT(mb.id) AS total_materiais
FROM usuario u
INNER JOIN material_bibliografico mb ON u.id = mb.usuario_id
GROUP BY u.nome, mb.categoria
ORDER BY u.nome, mb.categoria;

-- Consulta 3 (com JOIN): Encontrar todos os ebooks adicionados por um usuário específico ('prof@email.com').
-- Usando JOIN entre material_bibliografico, ebook e usuario com cláusula WHERE.
SELECT
    mb.titulo,
    mb.autor,
    mb.ano,
    e.url
FROM material_bibliografico mb
INNER JOIN ebook e ON mb.id = e.id
INNER JOIN usuario u ON mb.usuario_id = u.id
WHERE u.email = 'prof@email.com';

-- Consulta 4 (com JOIN): Listar os materiais que foram emprestados, com os nomes dos usuários e os títulos dos materiais.
-- Usando JOIN entre emprestimo, material_bibliografico e usuario.
SELECT
    u.nome AS nome_usuario,
    mb.titulo AS titulo_material,
    e.data_emprestimo,
    e.data_devolucao_prevista
FROM emprestimo e
INNER JOIN usuario u ON e.usuario_id = u.id
INNER JOIN material_bibliografico mb ON e.material_id = mb.id;

-- Consulta 5 (sem JOIN): Listar os 5 materiais mais recentes, ordenados por ano de lançamento.
-- Usando ORDER BY e LIMIT.
SELECT
    titulo,
    autor,
    ano,
    categoria
FROM material_bibliografico
ORDER BY ano DESC
LIMIT 5;

-- Consulta 6 (sem JOIN): Contar o número total de materiais em cada categoria.
-- Usando GROUP BY.
SELECT
    categoria,
    COUNT(id) AS total_materiais
FROM material_bibliografico
GROUP BY categoria;

-- Consulta 7 (com JOIN e AVG): Calcular a nota média de cada material avaliado.
SELECT
    mb.titulo,
    mb.autor,
    AVG(a.nota) AS nota_media
FROM material_bibliografico mb
JOIN avaliacao a ON mb.id = a.material_id
GROUP BY mb.id
ORDER BY nota_media DESC;

-- Consulta 8 (com JOIN): Encontrar todos os amigos de um usuário (ID 1).
SELECT
    u.nome AS nome_amigo,
    u.email
FROM usuario u
INNER JOIN amizade a ON (u.id = a.usuario_id1 OR u.id = a.usuario_id2)
WHERE (a.usuario_id1 = 1 OR a.usuario_id2 = 1) AND u.id != 1;