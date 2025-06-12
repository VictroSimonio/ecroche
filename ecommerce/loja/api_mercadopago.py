import mercadopago
from django.urls import reverse

public_key = "APP_USR-ae8f0eba-6182-4432-ae6d-0e3e74f4c269"
token = "APP_USR-6601297058736038-060413-340f4f30d5489f63a79677fc0d4db34e-2475616095"

def criar_pagamento(itens_pedido, link):
    # Configure as credenciais
    sdk = mercadopago.SDK(token)
    # Crie um item na preferência

    # itens que ele está comprando no formato de dicionário
    itens = []
    for item in itens_pedido:
        quantidade = int(item.quantidade)
        nome_produto = item.item_estoque.produto.nome
        preco_unitario = float(item.item_estoque.produto.preco)
        itens.append({
            "title": nome_produto,
            "quantity": quantidade,
            "unit_price": preco_unitario,
        })


    # valor total
    preference_data = {
        "items": itens,
        "back_urls": {
            "success": link,
            "pending": link,
            "failure": link,
        },
    }
    resposta = sdk.preference().create(preference_data)
    link_pagamento = resposta["response"]["init_point"]
    id_pagamento = resposta["response"]["id"]
    return link_pagamento, id_pagamento