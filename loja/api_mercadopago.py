import mercadopago
from django.urls import reverse
import json

# Seu token de acesso
token = "APP_USR-6392394118929682-070121-26d0cb70220f843a310ed326648e4b47-2475616095"

def criar_pagamento(itens_pedido, request):
    try:
        print("--- INICIANDO CRIAÇÃO DE PAGAMENTO ---")
        sdk = mercadopago.SDK(token)

        itens = []
        for item in itens_pedido:
            # Garantir que os tipos de dados estão corretos
            quantidade = int(item.quantidade)
            nome_produto = str(item.item_estoque.produto.nome)
            # A API exige um preço com no máximo 2 casas decimais
            preco_unitario = round(float(item.item_estoque.produto.preco), 2)

            # A API rejeita itens com quantidade 0 ou negativa
            if quantidade <= 0:
                print(f"AVISO: Item '{nome_produto}' ignorado por ter quantidade zero ou negativa.")
                continue

            itens.append({
                "title": nome_produto,
                "quantity": quantidade,
                "unit_price": preco_unitario,
                "currency_id": "BRL",  # É uma boa prática sempre definir a moeda
            })

        # A API falhará se a lista de itens estiver vazia
        if not itens:
            print("ERRO CRÍTICO: A lista de itens para pagamento está vazia. O pagamento não pode ser criado.")
            return None, None

        # Gerar o link de retorno absoluto
        link_retorno = request.build_absolute_uri(reverse("finalizar_pagamento"))

        preference_data = {
            "items": itens,
            "back_urls": {
                "success": link_retorno,
                "pending": link_retorno,
                "failure": link_retorno,
            },
            # "auto_return": "approved", # <-- ALTERAÇÃO FEITA AQUI!
        }

        print("\n--- DADOS ENVIADOS PARA A API ---")
        # Usamos json.dumps para formatar a saída e facilitar a leitura
        print(json.dumps(preference_data, indent=4))

        # Cria a preferência e obtém a resposta
        resposta = sdk.preference().create(preference_data)

        print("\n--- RESPOSTA COMPLETA DA API ---")
        print(json.dumps(resposta, indent=4))

        # Verificação robusta da resposta
        if resposta.get("status") == 201 and resposta.get("response"):
            link_pagamento = resposta["response"].get("init_point")
            id_pagamento = resposta["response"].get("id")
            
            if link_pagamento and id_pagamento:
                print("\n✅ Preferência criada com sucesso!")
                return link_pagamento, id_pagamento
            else:
                print("\n❌ ERRO: A API retornou status 201, mas 'init_point' ou 'id' estão ausentes na resposta.")
                return None, None
        else:
            print(f"\n❌ ERRO: A API do Mercado Pago não retornou status 201. Status recebido: {resposta.get('status')}")
            return None, None

    except Exception as e:
        print(f"\n❌ EXCEÇÃO INESPERADA na função criar_pagamento: {e}")
        return None, None