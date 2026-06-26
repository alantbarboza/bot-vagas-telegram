from logging import warning

def texto(elemento):
    if not elemento:
        return ""

    try:
        return (elemento.text_content() or "").strip()

    except Exception as e:
        warning(f"Utils/playwright | Erro ao obter texto: {e}")
        return ""

def atributo(elemento, nome):
    if not elemento:
        return None

    try:
        return elemento.get_attribute(nome)

    except Exception as e:
        warning(f"Utils/playwright | Erro ao obter atributo '{nome}': {e}")
        return None

def elemento(elemento, seletor, todos=False):
    if not elemento:
        return [] if todos else None

    try:
        if todos:
            return elemento.query_selector_all(seletor)

        return elemento.query_selector(seletor)

    except Exception as e:
        warning(f"Utils/playwright | Erro ao localizar '{seletor}': {e}")
        return [] if todos else None