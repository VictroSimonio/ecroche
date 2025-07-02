from .models import Pedido, ItensPedido, Cliente, Categoria, Tipo

def carrinho(request):
    quantidade_produtos_carrinho = 0
    
    if request.user.is_authenticated:
        try:
            # Tenta acessar o cliente associado ao usuário
            cliente = request.user.cliente  # Se você definiu related_name='cliente'
            # OU use isto se o campo no model for 'usuario':
            # cliente = request.user.usuario
        except Cliente.DoesNotExist:
            # Se não existir, cria um novo cliente para o usuário
            cliente = Cliente.objects.create(usuario=request.user, email=request.user.email)
    else:
        # Lógica para usuários não autenticados (com cookie de sessão)
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        else:
            return {'quantidade_produtos_carrinho': quantidade_produtos_carrinho}

    # Obtém ou cria o pedido não finalizado
    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
    
    # Calcula a quantidade de itens no carrinho
    itens_pedido = ItensPedido.objects.filter(pedido=pedido)
    quantidade_produtos_carrinho = sum(item.quantidade for item in itens_pedido)
    
    return {"quantidade_produtos_carrinho": quantidade_produtos_carrinho}

def categoria_tipos(request):
    categorias_navegacao = Categoria.objects.all()
    tipos_navegacao = Tipo.objects.all()
    return {
        'categorias_navegacao': categorias_navegacao,
        'tipos_navegacao': tipos_navegacao
    }

def faz_parte_equipe(request):
    equipe = False
    if request.user.is_authenticated:
        equipe = request.user.groups.filter(name="equipe").exists()
    return {"equipe": equipe}