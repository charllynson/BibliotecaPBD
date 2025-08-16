class MaterialBibliografico:
    def __init__(self, usuario_id, autor, titulo, ano): # Removido 'nota' do construtor base
        self.autor = autor
        self.titulo = titulo
        self.ano = ano
        self.usuario_id = usuario_id

class Livro(MaterialBibliografico):
    def __init__(self, usuario_id, autor, titulo, ano, genero, movimento, editora):
        super().__init__(usuario_id, autor, titulo, ano)
        self.genero = genero
        self.movimento = movimento
        self.editora = editora

class Apostila(MaterialBibliografico):
    def __init__(self, usuario_id, autor, titulo, ano, turma, disciplina):
        super().__init__(usuario_id, autor, titulo, ano)
        self.turma = turma
        self.disciplina = disciplina

class Ebook(MaterialBibliografico):
    def __init__(self, usuario_id, autor, titulo, ano, genero, movimento, url):
        super().__init__(usuario_id, autor, titulo, ano)
        self.genero = genero
        self.movimento = movimento
        self.url = url

class Trabalho(MaterialBibliografico):
    def __init__(self, usuario_id, autor, titulo, ano):
        super().__init__(usuario_id, autor, titulo, ano)

class Revista(MaterialBibliografico):
    def __init__(self, usuario_id, autor, titulo, ano, editora):
        super().__init__(usuario_id, autor, titulo, ano)
        self.editora = editora

# Resenha e MaterialBibliografico são conceitos diferentes.
# A classe Resenha aqui parece ser um tipo de material, mas no DB é uma interação.
# Vou manter a classe Resenha como um tipo de material para consistência com o uso atual,
# mas é importante notar a distinção com a tabela 'resenha' de interações.
class Resenha(MaterialBibliografico):
    def __init__(self, usuario_id, autor, titulo, ano):
        super().__init__(usuario_id, autor, titulo, ano)

              
        