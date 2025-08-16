import sqlite3

def criar_tabelas(db_name='Biblioteca.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_modificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Gatilho para atualizar o timestamp de modificação do usuário
    
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS atualizar_timestamp_usuario
        BEFORE UPDATE ON usuario
        FOR EACH ROW
        BEGIN
            UPDATE usuario SET data_modificacao = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    # Tabela principal de materiais bibliográficos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS material_bibliografico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            autor TEXT NOT NULL,
            titulo TEXT NOT NULL,
            ano INTEGER,
            categoria TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE SET NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livro (
            id INTEGER PRIMARY KEY,
            genero TEXT,
            movimento TEXT,
            editora TEXT,
            FOREIGN KEY (id) REFERENCES material_bibliografico (id) ON DELETE CASCADE
        );
    """)

    # Tabela de Ebooks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ebook (
            id INTEGER PRIMARY KEY,
            genero TEXT,
            movimento TEXT,
            url TEXT,
            FOREIGN KEY (id) REFERENCES material_bibliografico (id) ON DELETE CASCADE
        );
    """)
    
    # Tabela de Apostilas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apostila (
            id INTEGER PRIMARY KEY,
            turma TEXT,
            disciplina TEXT,
            FOREIGN KEY (id) REFERENCES material_bibliografico (id) ON DELETE CASCADE
        );
    """)

    # Tabela de Revistas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revista (
            id INTEGER PRIMARY KEY,
            editora TEXT,
            FOREIGN KEY (id) REFERENCES material_bibliografico (id) ON DELETE CASCADE
        );
    """)
    
    # Tabela de Trabalhos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trabalho (
            id INTEGER PRIMARY KEY,
            FOREIGN KEY (id) REFERENCES material_bibliografico (id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resenha_material (
                   id INTEGER PRIMARY KEY,
                   FOREIGN KEY (id) REFERENCES material_bibliografico (id) ON DELETE CASCADE
                );
    """)

    # Tabela de Amizades
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS amizade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id1 INTEGER NOT NULL,
            usuario_id2 INTEGER NOT NULL,
            data_amizade TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id1) REFERENCES usuario (id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id2) REFERENCES usuario (id) ON DELETE CASCADE,
            UNIQUE (usuario_id1, usuario_id2)
        );
    """)
    
    # Tabela de Empréstimos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emprestimo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_devolucao_prevista TIMESTAMP NOT NULL,
            data_devolucao_real TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES material_bibliografico (id) ON DELETE CASCADE
        );
    """)
    
    # Tabela de Acessos a Ebooks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acesso_ebook (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            ebook_id INTEGER NOT NULL,
            data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duracao_acesso INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,
            FOREIGN KEY (ebook_id) REFERENCES ebook (id) ON DELETE CASCADE
        );
    """)
    
    # Tabela de Favoritos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorita (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            data_favorito TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES material_bibliografico (id) ON DELETE CASCADE,
            UNIQUE (usuario_id, material_id)
        );
    """)
    
    # Tabela de Avaliações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            nota REAL NOT NULL CHECK(nota >= 0 AND nota <= 5),
            data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES material_bibliografico (id) ON DELETE CASCADE,
            UNIQUE (usuario_id, material_id)
        );
    """)
    
    # Tabela de Resenhas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resenha (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            texto_resenha TEXT NOT NULL,
            data_resenha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES material_bibliografico (id) ON DELETE CASCADE,
            UNIQUE (usuario_id, material_id)
        );
    """)

    # Tabela de Reservas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reserva (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            status_reserva TEXT NOT NULL DEFAULT 'pendente',
            data_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES material_bibliografico (id) ON DELETE CASCADE
        );
    """)

    
    conn.commit()
    conn.close()