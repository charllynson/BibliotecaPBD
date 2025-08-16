from datetime import datetime, timedelta
from Biblioteca import Biblioteca
from MaterialBibliografico import Livro, Apostila, Ebook, Revista, Resenha, Trabalho
from dados import criar_tabelas

def testar_sistema():
   
    criar_tabelas()
    # Criar instância da biblioteca
    biblioteca = Biblioteca()

    # Testar cadastro de usuários
    print("\n=== TESTANDO CADASTRO DE USUÁRIOS ===")
    biblioteca.cadastrar_usuario("João Silva", "joao@email.com", "senha123")
    biblioteca.cadastrar_usuario("Maria Souza", "maria@email.com", "abc123")
    biblioteca.cadastrar_usuario("Pedro Rocha", "pedro@email.com", "123456")
    
    # Tentar cadastrar com email duplicado (deve falhar)
    id_joao = biblioteca.login_usuario("joao@email.com", "senha123")
    id_maria = biblioteca.login_usuario("maria@email.com", "abc123")
    id_pedro = biblioteca.login_usuario("pedro@email.com","123456")


    print("\n--- TESTANDO ADIÇÃO E BUSCA DE MATERIAIS ---")
    livro1 = Livro(3, "J.R.R. Tolkien", "O Hobbit", 1937, "fantasia", "literatura fantástica", "HarperCollins")
    ebook1 = Ebook(1, "George Orwell", "1984", 1949, "ficção", "ficção distópica", "https://exemplo.com/1984")
    revista1 = Revista(2, "Editora Abril", "Revista Superinteressante", 2023, "científica", "Editora Abril")
    
    id_livro1 = biblioteca.adicionar_material(livro1)
    id_ebook1 = biblioteca.adicionar_material(ebook1)
    id_revista1 = biblioteca.adicionar_material(revista1)

    print("\n--- LISTANDO ACERVO COMPLETO ---")
    acervo = biblioteca.listar_acervo()
    for material in acervo:
        print(f"ID: {material['id']}, Título: {material['titulo']}, Categoria: {material['categoria']}")

    print("\n--- BUSCANDO MATERIAIS POR TÍTULO ---")
    materiais_buscados = biblioteca.buscar_materiais_titulo("o Hobbit")
    for material in materiais_buscados:
        print(f"ID: {material['id']}, Título: {material['titulo']}")

    usuarios = biblioteca.listar_usuarios()
    print("\n--- LISTANDO USUÁRIOS ---")
    for usuario in usuarios:
        print(f"ID: {usuario['id']}, Nome: {usuario['nome']}, Email: {usuario['email']}")
        
    # === TESTES DE AMIZADE ===
    print("\n--- TESTANDO RELAÇÕES DE AMIZADE ---")
    biblioteca.adicionar_amigo(id_joao, id_maria)
    biblioteca.adicionar_amigo(id_joao, id_pedro)
    
    print(f"\nAmigos de João (ID: {id_joao}):")
    amigos_joao = biblioteca.listar_amigos(id_joao)
    for amigo in amigos_joao:
        print(f" - {amigo['nome']} (Email: {amigo['email']})")

    # === TESTES DE AVALIAÇÃO E RESENHA ===
    print("\n--- TESTANDO AVALIAÇÕES E RESENHAS ---")
    biblioteca.avaliar_material(id_joao, id_livro1, 4.5)
    biblioteca.avaliar_material(id_maria, id_livro1, 5.0)
    
    nota_media = biblioteca.calcular_nota_media_material(id_livro1)
    print(f"\nNota média de '{livro1.titulo}': {nota_media}")
    
    biblioteca.escrever_resenha(id_joao, id_livro1, "Uma aventura épica e divertida, um clássico da fantasia.")
    biblioteca.escrever_resenha(id_maria, id_livro1, "Absolutamente fantástico! Uma leitura obrigatória.")
    
    print(f"\nResenhas para '{livro1.titulo}':")
    resenhas = biblioteca.listar_resenhas_material(id_livro1)
    for resenha in resenhas:
        print(f" - Por {resenha['nome']}: '{resenha['texto_resenha']}'")
        
    # === TESTES DE EMPRÉSTIMOS E RESERVAS ===
    print("\n--- TESTANDO EMPRÉSTIMOS E RESERVAS ---")
    data_devolucao_prevista = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')
    biblioteca.registrar_emprestimo(id_joao, id_livro1, data_devolucao_prevista)
    biblioteca.fazer_reserva(id_pedro, id_livro1)
    
    print(f"\nEmpréstimos de João (ID: {id_joao}):")
    emprestimos = biblioteca.listar_emprestimos_usuario(id_joao)
    for emp in emprestimos:
        print(f" - Material ID: {emp['material_id']}, Título: {emp['titulo']}, Data Empréstimo: {emp['data_emprestimo']}")
    
    # === TESTES DE RECOMENDAÇÃO ===
    print("\n--- TESTANDO RECOMENDAÇÕES ---")
    print(f"\nRecomendações para João (ID: {id_joao}):")
    recomendacoes_joao = biblioteca.recomendar_por_genero(id_joao)
    if recomendacoes_joao:
        for rec in recomendacoes_joao:
            print(f" - Título: {rec['titulo']}, Autor: {rec['autor']}, Categoria: {rec['categoria']}")
    else:
        print("Nenhuma recomendação disponível.")
        
    

  
    print("\n=== TESTES CONCLUÍDOS ===")

if __name__ == "__main__":
    testar_sistema()
