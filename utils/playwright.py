from logging import warning

def elemento(page, seletor, todos=False):
    if not page:
        return None

    try:
        loc = page.locator(seletor)

        if todos:
            return loc
        
        return loc.first

    except Exception as e:
        warning(f"Utils/playwright | Erro ao localizar '{seletor}': {e}")
        return None

def texto(el):
    if el is None:
        return ""

    try:
        return (el.text_content(timeout=5000) or "").strip()
    
    except Exception as e:
        warning(f"Utils/playwright | Erro ao obter texto: {e}")
        return ""
    
def atributo(el, nome):
    if el is None:
        return None

    try:
        return el.get_attribute(nome, timeout=5000)
    
    except Exception as e:
        warning(f"Utils/playwright | Erro ao obter atributo '{nome}': {e}")
        return None