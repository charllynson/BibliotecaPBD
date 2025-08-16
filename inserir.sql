
INSERT INTO usuario (nome, email, senha_hash) VALUES ('Luana Oliveira', 'luana@email.com', 'hashed_password_1');
INSERT INTO usuario (nome, email, senha_hash) VALUES ('Professor Teste', 'prof@email.com', 'hashed_password_2');
INSERT INTO usuario (nome, email, senha_hash) VALUES ('Maria Souza', 'maria@email.com', 'hashed_password_3');

INSERT INTO material_bibliografico (usuario_id, autor, titulo, ano, categoria) VALUES (1, 'Machado de Assis', 'Memórias Póstumas de Brás Cubas', 1881, 'livro');
INSERT INTO material_bibliografico (usuario_id, autor, titulo, ano, categoria) VALUES (1, 'Clarice Lispector', 'A Hora da Estrela', 1977, 'livro');
INSERT INTO material_bibliografico (usuario_id, autor, titulo, ano, categoria) VALUES (2, 'Stephen Hawking', 'Uma Breve História do Tempo', 1988, 'livro');
INSERT INTO material_bibliografico (usuario_id, autor, titulo, ano, categoria) VALUES (2, 'Tim Berners-Lee', 'A teia global', 1999, 'ebook');
INSERT INTO material_bibliografico (usuario_id, autor, titulo, ano, categoria) VALUES (3, 'National Geographic', 'A Revolução da IA', 2024, 'revista');
INSERT INTO material_bibliografico (usuario_id, autor, titulo, ano, categoria) VALUES (3, 'Física Moderna', 'Introdução à Física Quântica', 2023, 'apostila');


INSERT INTO livro (id, genero, movimento, editora) VALUES (1, 'Romance', 'Realismo', 'Nova Fronteira');
INSERT INTO livro (id, genero, movimento, editora) VALUES (2, 'Romance', 'Modernismo', 'Rocco');
INSERT INTO livro (id, genero, movimento, editora) VALUES (3, 'Divulgação Científica', 'N/A', 'Zahar');
INSERT INTO ebook (id, genero, movimento, url) VALUES (4, 'Tecnologia', 'Contemporâneo', 'https://exemplo.com/ebook_ia.pdf');
INSERT INTO revista (id, editora) VALUES (5, 'Editora Abril');
INSERT INTO apostila (id, turma, disciplina) VALUES (6, 'Engenharia de Software', 'Banco de Dados');


INSERT INTO emprestimo (usuario_id, material_id, data_emprestimo, data_devolucao_prevista) VALUES (1, 3, '2024-05-10 10:00:00', '2024-05-25 10:00:00');
INSERT INTO emprestimo (usuario_id, material_id, data_emprestimo, data_devolucao_prevista, data_devolucao_real) VALUES (2, 1, '2024-04-15 14:30:00', '2024-04-30 14:30:00', '2024-04-28 11:00:00');


INSERT INTO favorita (usuario_id, material_id) VALUES (1, 2);
INSERT INTO favorita (usuario_id, material_id) VALUES (2, 4);
INSERT INTO favorita (usuario_id, material_id) VALUES (3, 1);


INSERT INTO avaliacao (usuario_id, material_id, nota) VALUES (1, 1, 5);
INSERT INTO avaliacao (usuario_id, material_id, nota) VALUES (2, 2, 4);
INSERT INTO avaliacao (usuario_id, material_id, nota) VALUES (3, 1, 4.5);
INSERT INTO avaliacao (usuario_id, material_id, nota) VALUES (1, 3, 5);


INSERT INTO resenha (usuario_id, material_id, texto_resenha) VALUES (1, 1, 'Um clássico da literatura brasileira, leitura essencial!');
INSERT INTO resenha (usuario_id, material_id, texto_resenha) VALUES (2, 2, 'Gostei muito, mas a leitura é um pouco densa.');
INSERT INTO resenha (usuario_id, material_id, texto_resenha) VALUES (3, 1, 'Fantástico, superou minhas expectativas!');