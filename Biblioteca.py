import sqlite3
import bcrypt 
from datetime import datetime, timedelta
from MaterialBibliografico import Livro, Apostila, Ebook, Revista, Resenha, Trabalho


class Biblioteca:
    def __init__(self, db_name='Biblioteca.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        print("Conexão com o banco de dados estabelecida.")
        
    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            # Ativar chaves estrangeiras
            self.cursor.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            self.conn = None
            self.cursor = None
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def execute_query(self, query, params=()):
        if not self.conn:
            self._connect()
            if not self.conn:
                return None
        
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao executar a query: {e}")
            self.conn.rollback()
            return False
    
    def _fetch_one(self, query, params=()):
        if not self.conn:
            self._connect()
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erro ao buscar um registro: {e}")
            return None
        
    def _fetch_all(self, query, params=()):
        if not self.conn:
            self._connect()
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar registros: {e}")
            return None

    


    # Métodos para usuários
    def cadastrar_usuario(self, nome, email, senha):
        try: 
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            query = 'INSERT INTO usuario (nome, email, senha_hash) VALUES (?, ?, ?)'

            if self.execute_query(query, (nome, email, senha_hash)):
                print(f"Usuário '{nome}' cadastrado com sucesso.")
                return True
            else:
                return False

        except sqlite3.IntegrityError:
            print(f"Erro: E-mail '{email}' já cadastrado.")
            return False
        
        except Exception as e:
            print(f"Erro ao cadastrar usuário: {e}")
            return False
        
    def login_usuario(self, email, senha):
        query = 'SELECT id, senha_hash FROM usuario WHERE email = ?'
        resultado = self._fetch_one(query, (email,))
        
        if not resultado:
            print(f"Erro: Não foi possível localizar o e-mail '{email}'.")
            return None
        
        usuario_id = resultado['id']
        senha_hash = resultado['senha_hash']

        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
            print(f"Usuário '{email}' logado com sucesso.")
            return usuario_id
        else:
            print("Erro: Senha incorreta.")
            return None
    
    def resetar_senha(self, email, nova_senha):
        query = 'SELECT id FROM usuario WHERE email = ?'
        resultado = self._fetch_one(query, (email,))

        if not resultado:
            print(f"Erro: Não foi possível localizar o e-mail '{email}'.")
            return False
        
        usuario_id = resultado['id']
        senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        query_update = 'UPDATE usuario SET senha_hash = ? WHERE id = ?'
        return self.execute_query(query_update, (senha_hash, usuario_id))

    def buscar_usuario(self, usuario_id):
        query = 'SELECT id, nome, email FROM usuario WHERE id = ?'
        return self._fetch_one(query, (usuario_id,))
    
    def atualizar_usuario(self, usuario_id, nome=None, email=None, senha=None):
        updates = []
        params = []
        
        if nome:
            updates.append("nome = ?")
            params.append(nome)
        if email:
            updates.append("email = ?")
            params.append(email)
        if senha:
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            updates.append("senha_hash = ?")
            params.append(senha_hash)
        
        if not updates:
            print("Nenhum dado para atualizar.")
            return False
        
        query = f"UPDATE usuario SET {', '.join(updates)} WHERE id = ?"
        params.append(usuario_id)

        if self.execute_query(query, tuple(params)):
            print(f"Usuário '{usuario_id}' atualizado com sucesso.")
            return True 
        return False
    
    def listar_usuarios(self):
        query = 'SELECT id, nome, email FROM usuario ORDER BY nome'
        return self._fetch_all(query)
    
    

    def remover_usuario(self, user_id):
        query = 'DELETE FROM usuario WHERE id = ?'
        return self.execute_query(query, (user_id,))
    


    # Métodos para materiais
    def adicionar_material(self, material):
        try: 
            query_material = '''
            INSERT INTO material_bibliografico (usuario_id, autor, titulo, ano, categoria)
            VALUES (?, ?, ?, ?, ?)'''

            categoria = type(material).__name__.lower()
            
            if not self.execute_query(query_material, 
                                    (material.usuario_id, material.autor, 
                                     material.titulo, material.ano, categoria)):
                raise Exception("Erro ao adicionar material bibliográfico.")
            
            material_id = self.cursor.lastrowid

            if isinstance(material, Livro):
                query_especifico = '''
                INSERT INTO livro (id, genero, movimento, editora)
                VALUES (?, ?, ?, ?)'''
                params_especifico = (material_id, material.genero, 
                                    material.movimento, material.editora)

            elif isinstance(material, Apostila):
                query_especifico = '''
                INSERT INTO apostila (id, turma, disciplina)
                VALUES (?, ?, ?)'''
                params_especifico = (material_id, material.turma, material.disciplina)

            elif isinstance(material, Ebook):
                query_especifico = '''
                INSERT INTO ebook (id, genero, movimento, url)
                VALUES (?, ?, ?, ?)'''
                params_especifico = (material_id, material.genero, 
                                    material.movimento, material.url)

            elif isinstance(material, Revista):
                query_especifico = '''
                INSERT INTO revista (id, editora)
                VALUES (?, ?)'''
                params_especifico = (material_id, material.editora)
                
            elif isinstance(material, Resenha):
                query_especifico = '''
                INSERT INTO resenha_material (id)
                VALUES (?)'''
                params_especifico = (material_id,)
                
            elif isinstance(material, Trabalho):
                query_especifico = '''
                INSERT INTO trabalho (id)
                VALUES (?)'''
                params_especifico = (material_id,)
            
            else:
                raise ValueError("Tipo de material não reconhecido.")

            if self.execute_query(query_especifico, params_especifico):
                print(f"Material '{material.titulo}' adicionado com sucesso.")
                return material_id
            else:
                self.execute_query("DELETE FROM material_bibliografico WHERE id = ?", (material_id,))
                raise Exception("Erro ao adicionar material específico.")
            
        except Exception as e:
            print(f"Erro ao adicionar o material: {e}")
            return None

    def listar_acervo(self, tipo=None):
        query = """
        SELECT 
            mb.id, mb.autor, mb.titulo, mb.ano, mb.categoria,
            l.genero AS livro_genero, l.movimento AS livro_movimento, l.editora AS livro_editora,
            a.turma AS apostila_turma, a.disciplina AS apostila_disciplina,
            e.genero AS ebook_genero, e.movimento AS ebook_movimento, e.url AS ebook_url,
            r.editora AS revista_editora
        FROM material_bibliografico mb
        LEFT JOIN livro l ON mb.id = l.id
        LEFT JOIN apostila a ON mb.id = a.id
        LEFT JOIN ebook e ON mb.id = e.id
        LEFT JOIN revista r ON mb.id = r.id
        LEFT JOIN resenha_material rm ON mb.id = rm.id
        LEFT JOIN trabalho t ON mb.id = t.id
        """
        params = ()
        if tipo:
            query += " WHERE mb.categoria = ?"
            params = (tipo,)
            
        materiais_db = self._fetch_all(query, params)
        
        acervo = []
        for row in materiais_db:
            material_info = dict(row)
            nota_media = self.calcular_nota_media_material(material_info['id'])
            material_info['nota_media'] = nota_media if nota_media is not None else 0.0
            acervo.append(material_info)
        return acervo

    def listar_acervo_com_status(self):
        acervo = self.listar_acervo()
        for material in acervo:
            material['status'] = self.verificar_status_material(material['id'])
        return acervo
    
    def verificar_status_material(self, material_id):
        query_emprestimo = "SELECT COUNT(*) FROM emprestimo WHERE material_id = ? AND data_devolucao_real IS NULL"
        emprestado = self._fetch_one(query_emprestimo, (material_id,))['COUNT(*)'] > 0
        
        if emprestado:
            return "Emprestado"
            
        query_reserva = "SELECT COUNT(*) FROM reserva WHERE material_id = ? AND status_reserva = 'pendente'"
        reservado = self._fetch_one(query_reserva, (material_id,))['COUNT(*)'] > 0

        if reservado:
            return "Reservado"

        return "Disponível"


    def buscar_material_por_id(self, material_id):
        query = """
        SELECT 
            mb.id, mb.autor, mb.titulo, mb.ano, mb.categoria,
            l.genero AS livro_genero, l.movimento AS livro_movimento, l.editora AS livro_editora,
            a.turma AS apostila_turma, a.disciplina AS apostila_disciplina,
            e.genero AS ebook_genero, e.movimento AS ebook_movimento, e.url AS ebook_url,
            r.editora AS revista_editora
        FROM material_bibliografico mb
        LEFT JOIN livro l ON mb.id = l.id
        LEFT JOIN apostila a ON mb.id = a.id
        LEFT JOIN ebook e ON mb.id = e.id
        LEFT JOIN revista r ON mb.id = r.id
        LEFT JOIN resenha_material rm ON mb.id = rm.id
        LEFT JOIN trabalho t ON mb.id = t.id
        WHERE mb.id = ?
        """
        material_db = self._fetch_one(query, (material_id,))
        if material_db:
            material_info = dict(material_db)
            nota_media = self.calcular_nota_media_material(material_id)
            material_info['nota_media'] = nota_media if nota_media is not None else 0.0
            return material_info
        return None
    
    def buscar_materiais_titulo(self, titulo_parcial):
        query = """
        SELECT 
            mb.id, mb.autor, mb.titulo, mb.ano, mb.categoria
        FROM material_bibliografico mb
        WHERE mb.titulo LIKE ?
        """
        return self._fetch_all(query, (f'%{titulo_parcial}%',))
    
    def remover_material(self, material_id):
        try:
            query = "DELETE FROM material_bibliografico WHERE id = ?"
            if self.execute_query(query, (material_id,)):
                print(f"Material com ID {material_id} removido com sucesso.")
                return True
            else:
                print(f"Erro ao remover o material com ID {material_id}.")
                return False
        except sqlite3.Error as e:
            print(f"Erro ao remover o material: {e}")
            return False
        


    # Métodos para amizades
    def adicionar_amigo(self, usuario_id1, usuario_id2):
        if usuario_id1 == usuario_id2:
            print("Erro: Um usuário não pode ser amigo de si mesmo.")
            return False
        
        query_check = """
        SELECT 1 FROM amizade
        WHERE (usuario_id1 = ? AND usuario_id2 = ?) OR (usuario_id1 = ? AND usuario_id2 = ?)
        """
        
        if self._fetch_one(query_check, (usuario_id1, usuario_id2, usuario_id2, usuario_id1)):
            print("Erro: Amizade já existe.")
            return False    
        
        query = 'INSERT INTO amizade (usuario_id1, usuario_id2, data_amizade) VALUES (?, ?, ?)'
        data_amizade = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.execute_query(query, (usuario_id1, usuario_id2, data_amizade)):
            print(f"Amizade entre {usuario_id1} e {usuario_id2} estabelecida.")
            return True
        return False
       
    def remover_amigo(self, usuario_id1, usuario_id2):
        query = """
        DELETE FROM amizade 
        WHERE (usuario_id1 = ? AND usuario_id2 = ?) OR (usuario_id1 = ? AND usuario_id2 = ?)
        """
        if self.execute_query(query, (usuario_id1, usuario_id2, usuario_id2, usuario_id1)):
            print(f"Amizade entre {usuario_id1} e {usuario_id2} removida.")
            return True
        return False
    
    def listar_amigos(self, usuario_id):
        query = """
        SELECT u.id, u.nome, u.email
        FROM usuario u
        JOIN amizade a ON (u.id = a.usuario_id1 OR u.id = a.usuario_id2)
        WHERE (a.usuario_id1 = ? OR a.usuario_id2 = ?) AND u.id != ?
        """
        return self._fetch_all(query, (usuario_id, usuario_id, usuario_id))

    # Métodos para empréstimos
    def registrar_emprestimo(self, usuario_id, material_id, data_devolucao_prevista):
        data_emprestimo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
        INSERT INTO emprestimo (usuario_id, material_id, data_emprestimo, data_devolucao_prevista) 
        VALUES (?, ?, ?, ?)
        """
        if self.execute_query(query, (usuario_id, material_id, data_emprestimo, data_devolucao_prevista)):
            print(f"Empréstimo do material {material_id} para o usuário {usuario_id} registrado.")
            return True
        return False
    
    def registrar_devolucao(self, emprestimo_id):
        data_devolucao_real = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = 'UPDATE emprestimo SET data_devolucao_real = ? WHERE id = ?'
        if self.execute_query(query, (data_devolucao_real, emprestimo_id)):
            print(f"Devolução do empréstimo {emprestimo_id} registrada.")
            return True
        return False
    
    def buscar_emprestimo_aberto(self, usuario_id, material_id):
        query = "SELECT id FROM emprestimo WHERE usuario_id = ? AND material_id = ? AND data_devolucao_real IS NULL"
        return self._fetch_one(query, (usuario_id, material_id))

    def buscar_emprestimo_aberto_material(self, material_id):
        query = "SELECT id, usuario_id FROM emprestimo WHERE material_id = ? AND data_devolucao_real IS NULL"
        return self._fetch_one(query, (material_id,))

    def listar_emprestimos_usuario(self, usuario_id):
        query = """
        SELECT e.id, e.material_id, mb.titulo, e.data_emprestimo, 
               e.data_devolucao_prevista, e.data_devolucao_real
        FROM emprestimo e
        JOIN material_bibliografico mb ON e.material_id = mb.id
        WHERE e.usuario_id = ?
        ORDER BY e.data_emprestimo DESC 
        """
        return self._fetch_all(query, (usuario_id,))
    


    # Métodos para ebooks
    def registrar_acesso_ebook(self, usuario_id, ebook_id, duracao_acesso=None):
        data_acesso = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
        INSERT INTO acesso_ebook (usuario_id, ebook_id, data_acesso, duracao_acesso) 
        VALUES (?, ?, ?, ?)
        """
        if self.execute_query(query, (usuario_id, ebook_id, data_acesso, duracao_acesso)):
            print(f"Acesso ao ebook {ebook_id} pelo usuário {usuario_id} registrado.")
            return True
        return False
    
    def listar_acessos_ebook_usuario(self, usuario_id):
        query = """
        SELECT ae.ebook_id, mb.titulo, ae.data_acesso, ae.duracao_acesso
        FROM acesso_ebook ae
        JOIN ebook e ON ae.ebook_id = e.id
        JOIN material_bibliografico mb ON e.id = mb.id
        WHERE ae.usuario_id = ?
        ORDER BY ae.data_acesso DESC
        """
        return self._fetch_all(query, (usuario_id,))
    


    # Métodos para favoritos
    def adicionar_favorito(self, usuario_id, material_id):
        data_favorito = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
        INSERT INTO favorita (usuario_id, material_id, data_favorito) 
        VALUES (?, ?, ?)
        """
        try:
            if self.execute_query(query, (usuario_id, material_id, data_favorito)):
                print(f"Material {material_id} adicionado aos favoritos do usuário {usuario_id}.")
                return True
            return False
        except sqlite3.IntegrityError:
            print(f"Material {material_id} já está nos favoritos do usuário {usuario_id}.")
            return False
    
    def remover_favorito(self, usuario_id, material_id):
        query = 'DELETE FROM favorita WHERE usuario_id = ? AND material_id = ?'
        if self.execute_query(query, (usuario_id, material_id)):
            print(f"Material {material_id} removido dos favoritos do usuário {usuario_id}.")
            return True
        return False
    
    def listar_favoritos_usuario(self, usuario_id):
        query = """
        SELECT f.material_id, mb.titulo, mb.autor, f.data_favorito
        FROM favorita f
        JOIN material_bibliografico mb ON f.material_id = mb.id
        WHERE f.usuario_id = ?
        ORDER BY f.data_favorito DESC
        """
        return self._fetch_all(query, (usuario_id,))
    


    # Métodos para resenhas
    def escrever_resenha(self, usuario_id, material_id, texto_resenha):
        data_resenha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
        INSERT INTO resenha (usuario_id, material_id, texto_resenha, data_resenha) 
        VALUES (?, ?, ?, ?)
        """
        try:
            if self.execute_query(query, (usuario_id, material_id, texto_resenha, data_resenha)):
                print(f"Resenha para o material {material_id} pelo usuário {usuario_id} adicionada.")
                return True
            return False
        except sqlite3.IntegrityError:
            print(f"Usuário {usuario_id} já possui uma resenha para o material {material_id}.")
            return False
        
    def editar_resenha(self, usuario_id, material_id, novo_texto):
        query = """
        UPDATE resenha SET texto_resenha = ?, data_resenha = ? 
        WHERE usuario_id = ? AND material_id = ?
        """
        data_resenha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.execute_query(query, (novo_texto, data_resenha, usuario_id, material_id)):
            print(f"Resenha para o material {material_id} pelo usuário {usuario_id} atualizada.")
            return True
        return False
    
    def remover_resenha(self, usuario_id, material_id):
        query = 'DELETE FROM resenha WHERE usuario_id = ? AND material_id = ?'
        if self.execute_query(query, (usuario_id, material_id)):
            print(f"Resenha para o material {material_id} pelo usuário {usuario_id} removida.")
            return True
        return False
    
    def listar_resenhas_material(self, material_id):
        query = """
        SELECT r.usuario_id, u.nome, r.texto_resenha, r.data_resenha
        FROM resenha r
        JOIN usuario u ON r.usuario_id = u.id
        WHERE r.material_id = ?
        ORDER BY r.data_resenha DESC
        """
        return self._fetch_all(query, (material_id,))
    
    def listar_resenhas_usuario(self, usuario_id):
        query = """
        SELECT r.material_id, mb.titulo, r.texto_resenha, r.data_resenha
        FROM resenha r
        JOIN material_bibliografico mb ON r.material_id = mb.id
        WHERE r.usuario_id = ?
        ORDER BY r.data_resenha DESC
        """
        return self._fetch_all(query, (usuario_id,))
    


    # Métodos para avaliações
    def avaliar_material(self, usuario_id, material_id, nota):
        if not (0 <= nota <= 5):
            print("Erro: A nota deve estar entre 0 e 5.")
            return False
            
        data_avaliacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
        INSERT INTO avaliacao (usuario_id, material_id, nota, data_avaliacao) 
        VALUES (?, ?, ?, ?)
        """
        try:
            if self.execute_query(query, (usuario_id, material_id, nota, data_avaliacao)):
                print(f"Material {material_id} avaliado com nota {nota} pelo usuário {usuario_id}.")
                return True
            return False
        except sqlite3.IntegrityError:
            print(f"Usuário {usuario_id} já avaliou o material {material_id}.")
            return False
        
    def atualizar_avaliacao(self, usuario_id, material_id, nova_nota):
        if not (0 <= nova_nota <= 5):
            print("Erro: Nota deve estar entre 0 e 5.")
            return False
            
        query = """
        UPDATE avaliacao SET nota = ?, data_avaliacao = ? 
        WHERE usuario_id = ? AND material_id = ?
        """
        data_avaliacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.execute_query(query, (nova_nota, data_avaliacao, usuario_id, material_id)):
            print(f"Avaliação do material {material_id} pelo usuário {usuario_id} atualizada para {nova_nota}.")
            return True
        return False

    def remover_avaliacao(self, usuario_id, material_id):
        query = 'DELETE FROM avaliacao WHERE usuario_id = ? AND material_id = ?'
        if self.execute_query(query, (usuario_id, material_id)):
            print(f"Avaliação do material {material_id} pelo usuário {usuario_id} removida.")
            return True
        return False

    def calcular_nota_media_material(self, material_id):
        query = 'SELECT AVG(nota) as nota_media FROM avaliacao WHERE material_id = ?'
        resultado = self._fetch_one(query, (material_id,))
        if resultado and resultado['nota_media'] is not None:
            return round(resultado['nota_media'], 2)
        
        return None

    # Métodos para reservas
    def fazer_reserva(self, usuario_id, material_id):
        data_reserva = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'pendente'
        query = """
        INSERT INTO reserva (usuario_id, material_id, status_reserva, data_reserva) 
        VALUES (?, ?, ?, ?)
        """
        try:
            if self.execute_query(query, (usuario_id, material_id, status, data_reserva)):
                print(f"Reserva do material {material_id} pelo usuário {usuario_id} registrada.")
                return True
            return False
        except sqlite3.IntegrityError:
            print(f"Erro: Usuário {usuario_id} já possui uma reserva para o material {material_id}.")
            return False
    
    def cancelar_reserva(self, reserva_id):
        query = 'DELETE FROM reserva WHERE id = ?'
        if self.execute_query(query, (reserva_id,)):
            print(f"Reserva com ID {reserva_id} cancelada.")
            return True
        return False

    def listar_reservas_usuario(self, usuario_id):
        query = """
        SELECT r.id, r.material_id, mb.titulo, r.data_reserva, r.status_reserva
        FROM reserva r
        JOIN material_bibliografico mb ON r.material_id = mb.id
        WHERE r.usuario_id = ?
        ORDER BY r.data_reserva DESC
        """
        return self._fetch_all(query, (usuario_id,))
    
    def recomendar_por_genero(self, usuario_id, limit=5):
        #recomenda materiais baseados nos gêneros/categorias que o usuário mais interagiu.
        # 1. Encontrar os gêneros/categorias mais acessados/avaliados pelo usuário
        query_top_categorias = """
        SELECT mb.categoria, COUNT(*) as count
        FROM (
            SELECT material_id FROM emprestimo WHERE usuario_id = ?
            UNION ALL
            SELECT ebook_id AS material_id FROM acesso_ebook WHERE usuario_id = ?
            UNION ALL
            SELECT material_id FROM favorita WHERE usuario_id = ?
            UNION ALL
            SELECT material_id FROM avaliacao WHERE usuario_id = ?
        ) AS user_interactions
        JOIN material_bibliografico mb ON user_interactions.material_id = mb.id
        WHERE mb.categoria IS NOT NULL
        GROUP BY mb.categoria
        ORDER BY count DESC
        LIMIT 3
        """
        top_categorias = self._fetch_all(query_top_categorias, (usuario_id, usuario_id, usuario_id, usuario_id))
        
        if not top_categorias:
            print("Nenhuma categoria de interesse encontrada para recomendação.")
            return []
        categorias_interessadas = [row['categoria'] for row in top_categorias]
        
        # 2. Buscar materiais nessas categorias que o usuário ainda não interagiu
        query_recomendacao = f"""
        SELECT mb.id, mb.titulo, mb.autor, mb.categoria
        FROM material_bibliografico mb
        WHERE mb.categoria IN ({','.join(['?' for _ in categorias_interessadas])})
        AND mb.id NOT IN (
            SELECT material_id FROM emprestimo WHERE usuario_id = ?
            UNION
            SELECT ebook_id AS material_id FROM acesso_ebook WHERE usuario_id = ?
            UNION
            SELECT material_id FROM favorita WHERE usuario_id = ?
            UNION
            SELECT material_id FROM avaliacao WHERE usuario_id = ?
             )
        LIMIT ?
        """
        params = tuple(categorias_interessadas) + (usuario_id, usuario_id, usuario_id, usuario_id, limit)
        return self._fetch_all(query_recomendacao, params)
    
  
    def atualizar_nome_usuario(self, user_id, novo_nome):

        if not isinstance(user_id, int):
            print("Erro: ID do usuário deve ser um número inteiro.")
            return False

        query = 'UPDATE usuario SET nome = ? WHERE id = ?'
        try:
            with self.conn:
                self.cursor.execute(query, (novo_nome, user_id))
                print(f"Nome do usuário com ID {user_id} atualizado para '{novo_nome}'.")
                return True
        except sqlite3.Error as e:
            print(f"Erro ao executar a query: {e}")
            return False
    
    

def __del__(self):
        self.close()