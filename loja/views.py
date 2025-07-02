from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import *
import uuid
import re
from .utils import filtrar_produtos, preco_minimo_maximo, ordenar_produtos, enviar_email_compra, exportar_csv
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime
from .api_mercadopago import criar_pagamento

# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')

def loja(request, filtro=None):
    produtos = Produto.objects.filter(ativo=True)
    produtos = filtrar_produtos(produtos, filtro)

    if request.method == "POST":
        dados = request.POST.dict()
        produtos = produtos.filter(preco__gte=dados.get("preco_minimo"), preco__lte=dados.get("preco_maximo"))
        if "categoria" in dados:
            produtos = produtos.filter(categoria__slug= dados.get("categoria"))
        if "tipo" in dados:
            produtos = produtos.filter(tipo__slug= dados.get("tipo"))

    ids_categorias = produtos.values_list("categoria", flat=True).distinct()
    categorias = Categoria.objects.filter(id__in=ids_categorias)
    minimo, maximo = preco_minimo_maximo(produtos)
    
    ordem = request.GET.get("ordem", "menor-preco")
    produtos = ordenar_produtos(produtos, ordem)
    context = {"produtos": produtos, "minimo": minimo, "maximo": maximo,
               "categorias": categorias}
    return render(request, 'loja.html', context)

def ver_produto(request, id_produto):
    produto = Produto.objects.get(id=id_produto)
    itens_estoque = ItemEstoque.objects.filter(produto=produto)
    if len(itens_estoque) > 0:
        tem_estoque = True
    else:
        tem_estoque = False
    context = {"produto": produto, "itens_estoque" : itens_estoque, "tem_estoque" : tem_estoque}
    return render(request,"ver_produto.html", context)

def adicionar_carrinho(request, id_produto):
    if request.method == "POST" and id_produto:
        resposta = redirect('carrinho')
        
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
            else:
                id_sessao = str(uuid.uuid4())
                resposta.set_cookie(key='id_sessao', value=id_sessao, max_age=60*60*24*7)
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        
        # Obter o pedido ou criar um novo
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)

        # Obter o item de estoque relacionado ao produto
        item_estoque = ItemEstoque.objects.filter(produto_id=id_produto)

        # Verificar se o produto tem estoque disponível
        if item_estoque.exists():
            # Suponhamos que o produto tenha várias entradas de estoque, podemos pegar o primeiro
            item_estoque = item_estoque.first()
            estoque_disponivel = item_estoque.quantidade  # Aqui você pode ajustar conforme o modelo real de estoque

            item_pedido, criado = ItensPedido.objects.get_or_create(item_estoque=item_estoque, pedido=pedido)

            # Verificar se a quantidade do item no carrinho não excede o estoque disponível
            if item_pedido.quantidade < estoque_disponivel:
                item_pedido.quantidade += 1
                item_pedido.save()
            else:
                # Se a quantidade exceder o estoque, adicionar uma mensagem de erro
                messages.error(request, f"Não há estoque suficiente para adicionar {item_estoque.produto.nome} ao seu carrinho.")
        else:
            # Se não houver estoque, adicionar uma mensagem de erro
            messages.error(request, f"O produto {item_estoque.produto.nome} está fora de estoque.")
        
        return resposta
    else:
        return redirect('loja')
    
def remover_carrinho(request, id_produto):
    if request.method == "POST" and id_produto:
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
             if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao = id_sessao)
             else:
                 return redirect('loja')
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
        item_estoque = ItemEstoque.objects.get(produto_id=id_produto,)
        item_pedido, criado = ItensPedido.objects.get_or_create(item_estoque=item_estoque, pedido=pedido)
        item_pedido.quantidade -= 1
        item_pedido.save()
        if item_pedido.quantidade <=0:
            item_pedido.delete()
        return redirect('carrinho')
    else:
        return redirect('loja')
    

def carrinho(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        else:
            context = {"cliente_existente": False, "itens_pedido": None, "pedido": None}
            return render(request, 'carrinho.html', context)
    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
    itens_pedido = ItensPedido.objects.filter(pedido=pedido)
    context = {"itens_pedido": itens_pedido, "pedido": pedido, "cliente_existente": True}
    return render(request, 'carrinho.html', context)

def checkout(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        else:
            return redirect('loja')
    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
    enderecos = Endereco.objects.filter(cliente=cliente)
    context = {"pedido": pedido, "enderecos": enderecos, "erro": None}
    return render(request, 'checkout.html', context)

def finalizar_pedido(request, id_pedido):
    if request.method == "POST":
        erro = None
        dados = request.POST.dict()

        # --- Toda a sua lógica de validação de endereço, email, etc. continua aqui ---
        # (O código abaixo é uma réplica do seu, mantido para contexto)
        total = float(dados.get("total", "0").replace(",", "."))
        pedido = Pedido.objects.get(id=id_pedido)

        if total != float(pedido.preco_total):
            erro = "preco"

        if not "endereco" in dados:
            erro = "endereco"
        else:
            id_endereco = dados.get("endereco")
            try:
                endereco = Endereco.objects.get(id=id_endereco)
                pedido.endereco = endereco
            except Endereco.DoesNotExist:
                erro = "endereco"

        if not request.user.is_authenticated:
            email = dados.get("email")
            try:
                validate_email(email)
            except ValidationError:
                erro = "email"
            if not erro:
                clientes = Cliente.objects.filter(email=email)
                if clientes:
                    pedido.cliente = clientes[0]
                else:
                    pedido.cliente.email = email
                    pedido.cliente.save()
        
        codigo_transacao = f"{pedido.id}-{datetime.now().timestamp()}"
        pedido.codigo_transacao = codigo_transacao
        pedido.save()
        
        if erro:
            enderecos = Endereco.objects.filter(cliente=pedido.cliente)
            context = {"erro": erro, "pedido": pedido, "enderecos": enderecos}
            messages.error(request, f"Erro de validação: {erro}. Por favor, corrija e tente novamente.")
            return render(request, "checkout.html", context)
        # --- Fim da lógica de validação ---

        # --- Início da chamada para a API (parte corrigida) ---
        try:
            itens_pedido = ItensPedido.objects.filter(pedido=pedido)
            link_pagamento, id_pagamento = criar_pagamento(itens_pedido, request)

            if id_pagamento and link_pagamento:
                # Sucesso! O ID foi retornado.
                Pagamento.objects.create(id_pagamento=id_pagamento, pedido=pedido)
                return redirect(link_pagamento)
            else:
                # Falha! O ID não foi retornado. A causa do erro foi impressa no console.
                messages.error(request, "Não foi possível iniciar o processo de pagamento. Por favor, tente novamente ou contate o suporte.")
                return redirect("checkout")

        except Exception as e:
            # Captura exceções mais genéricas que podem ocorrer na view
            print(f"❌ Erro crítico na view finalizar_pedido: {e}")
            messages.error(request, "Ocorreu um erro inesperado ao tentar processar seu pagamento. Tente novamente mais tarde.")
            return redirect("checkout")

    return redirect("loja")

def finalizar_pagamento(request):
    dados = request.GET.dict()
    status = dados.get("status")
    id_pagamento = dados.get("preference_id")
    if status == "approved":
        pagamento = Pagamento.objects.get(id_pagamento=id_pagamento)
        pagamento.aprovado = True
        pedido = pagamento.pedido
        pedido.finalizado = True
        pedido.data_finalizacao = datetime.now()
        pedido.save()
        pagamento.save()
        enviar_email_compra(pedido)
        return redirect("meus_pedidos")    
    else:
        return redirect("checkout")
    
def adicionar_endereco(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
            else:
                return redirect('loja')

        # Obtendo os dados do formulário
        dados = request.POST.dict()

        # Verificando se o campo 'numero' está vazio e atribuindo "S/N" se necessário
        numero = dados.get("numero") if dados.get("numero") else " S/N"

        # Criando o objeto Endereco
        endereco = Endereco.objects.create(
            cliente=cliente,
            rua=dados.get("rua"),
            numero=numero,  # Usando o valor de 'numero', que já está com "S/N" se vazio
            complemento=dados.get("complemento"),
            cep=dados.get("cep"),
            cidade=dados.get("cidade"),
            estado=dados.get("estado")
        )
        endereco.save()
        return redirect("checkout")
    else:
        context = {}
        return render(request, "adicionar_endereco.html", context)


@login_required
def minha_conta(request):
    erro = None
    alterado = False

    if request.method == "POST":
        if "senha_atual" in request.POST:
            # Alteração de senha
            senha_atual = request.POST.get("senha_atual")
            nova_senha = request.POST.get("nova_senha")
            nova_senha_confirmacao = request.POST.get("nova_senha_confirmacao")

            # Valida a senha atual
            if not request.user.check_password(senha_atual):
                erro = "senha_incorreta"

            # Valida a nova senha
            elif not validar_senha(nova_senha):
                erro = "senha_invalida"

            # Confirma a nova senha
            elif nova_senha != nova_senha_confirmacao:
                erro = "senhas_diferentes"

            else:
                # Atualiza a senha
                request.user.set_password(nova_senha)
                request.user.save()

                # Atualiza a sessão para evitar logout
                update_session_auth_hash(request, request.user)

                alterado = True

        else:
            # Alterações nos dados pessoais
            nome = request.POST.get("nome")
            email = request.POST.get("email")
            telefone = request.POST.get("telefone")

            # Validação do e-mail
            try:
                validate_email(email)
            except ValidationError:
                erro = "email_invalido"

            # Atualiza os dados se não houver erros
            if not erro:
                cliente = request.user.cliente
                request.user.email = email
                cliente.nome = nome
                cliente.telefone = telefone
                request.user.save()
                cliente.save()
                alterado = True

    context = {"erro": erro, "alterado": alterado}
    return render(request, "usuario/minha_conta.html", context)

@login_required
def meus_pedidos(request):
    cliente = request.user.cliente
    pedidos = Pedido.objects.filter(finalizado=True, cliente=cliente).order_by("-data_finalizacao")
    context = {"pedidos": pedidos}
    return render(request, "usuario/meus_pedidos.html", context)

def fazer_login(request):
    erro = False
    if request.user.is_authenticated:
        return redirect('loja')
    if request.method == "POST":
        dados = request.POST.dict()
        if "email" in dados and "senha" in dados:
            email = dados.get("email")
            senha = dados.get("senha")
            usuario = authenticate(request, username=email, password=senha)
            if usuario:
                login(request, usuario)
                return redirect("loja")
            else:
                erro = True
        else:
            erro = True
    context = {"erro": erro}
    return render(request, 'usuario/login.html', context)

def criar_conta(request):
    erro = None
    if request.user.is_authenticated:
        return redirect("loja")
    if request.method == "POST":
        dados = request.POST.dict()
        if "email" in dados and "senha" in dados and "confirmar_senha" in dados and "nome" in dados:
            # Captura os dados do formulário
            nome = dados.get("nome")
            email = dados.get("email")
            senha = dados.get("senha")
            confirmar_senha = dados.get("confirmar_senha")

            # Valida o e-mail
            try:
                validate_email(email)
            except ValidationError:
                erro = "email_invalido"

            # Valida a senha
            if not erro and not validar_senha(senha):
                erro = "senha_invalida"

            # Verifica se as senhas coincidem
            if not erro and senha != confirmar_senha:
                erro = "senhas_diferentes"

            if not erro:
                # Cria o usuário
                usuario, criado = User.objects.get_or_create(username=email, email=email)
                if not criado:
                    erro = "usuario_existente"
                else:
                    usuario.set_password(senha)
                    usuario.save()

                    # Faz o login
                    usuario = authenticate(request, username=email, password=senha)
                    login(request, usuario)

                    # Cria o cliente associado ao usuário
                    if request.COOKIES.get("id_sessao"):
                        id_sessao = request.COOKIES.get("id_sessao")
                        cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
                    else:
                        cliente, criado = Cliente.objects.get_or_create(email=email)
                    cliente.usuario = usuario
                    cliente.email = email
                    cliente.nome = nome  # Associa o nome ao cliente
                    cliente.save()
                    return redirect("loja")
        else:
            erro = "preenchimento"
    context = {"erro": erro}
    return render(request, "usuario/criar_conta.html", context)

def validar_senha(senha):
    regex = r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}|:"<>?]).{8,}$'
    return re.match(regex, senha)


@login_required
def fazer_logout(request):
    logout(request)
    return redirect('fazer_login')

@login_required
def gerenciar_loja(request):
    if request.user.groups.filter(name="equipe").exists():
        pedidos_finalizados = Pedido.objects.filter(finalizado=True)
        qtde_pedidos = len(pedidos_finalizados)
        faturamento = sum(pedido.preco_total for pedido in pedidos_finalizados)
        qtde_produtos = sum(pedido.quantidade_total for pedido in pedidos_finalizados)
        context = {"qtde_pedidos": qtde_pedidos, "qtde_produtos": qtde_produtos, "faturamento": faturamento}
        return render(request, "interno/gerenciar_loja.html", context=context)
    else:
        redirect('loja')

@login_required
def exportar_relatorio(request, relatorio):
    if request.user.groups.filter(name="equipe").exists():
        if relatorio == "pedido":
            informacoes = Pedido.objects.filter(finalizado=True)
        elif relatorio == "cliente":
            informacoes = Cliente.objects.all()
        elif relatorio == "endereco":
            informacoes = Endereco.objects.all()
        return exportar_csv(informacoes)
    else:
        return redirect('gerenciar_loja')

def faq(request):
    return render(request, 'faq.html')

def sobre(request):
    return render(request, 'sobre.html')

@login_required  # Garante que apenas usuários autenticados possam avaliar
def avaliar_produto(request):
    # Filtra produtos comprados pelo usuário em pedidos finalizados
    pedidos_usuario = Pedido.objects.filter(cliente=request.user.cliente, finalizado=True)
    produtos_comprados = Produto.objects.filter(
        id__in=[item.item_estoque.produto.id for pedido in pedidos_usuario for item in pedido.itens]
    )

    if request.method == 'POST':
        produto_id = request.POST.get('produto')
        comentario = request.POST.get('avaliacao')

        # Verifica se o produto selecionado está na lista de produtos comprados
        produto = get_object_or_404(produtos_comprados, id=produto_id)

        # Cria uma nova avaliação no banco de dados
        Avaliacao.objects.create(usuario=request.user, produto=produto.nome, comentario=comentario)

        return redirect('listar_avaliacoes')  # Redireciona para a página de confirmação

    return render(request, 'avaliacao.html', {'produtos': produtos_comprados})

def listar_avaliacoes(request):
    # Pega todas as avaliações do banco de dados
    avaliacoes = Avaliacao.objects.all()
    return render(request, 'listar_avaliacoes.html', {'avaliacoes': avaliacoes})

