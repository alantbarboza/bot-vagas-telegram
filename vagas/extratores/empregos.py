from base64 import b64encode
from json import dumps
from logging import info, warning
from vagas.filtros import MAX_PAGINAS, PERIODO_DIAS
from utils.playwright import texto, atributo, elemento

def extrair_empregos(page, termos_busca):
    info("Extraindo vagas do Empregos.com.br.")
    vagas = []

    for termo in termos_busca:
        for pagina in range(MAX_PAGINAS):

            payload = {
                "keyword": [termo],
                "filters": [
                    {
                        "facetItem": 19,
                        "rangeStart": PERIODO_DIAS,
                        "description": "Últimos dias"
                    },
                    {
                        "facetItem": 17,
                        "description": "Híbrido"
                    },
                    {
                        "facetItem": 17,
                        "description": "Remoto"
                    }
                ],
                "page": pagina,
                "size": 10,
                "order": 0,
                "distance": 40
            }

            query = b64encode(
                dumps(payload).encode()
            ).decode()

            url = f"https://www.empregos.com.br/vagas/{termo.replace(' ', '-')}?q={query}"

            try:
                page.goto(url, timeout=30000,  wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                cards = elemento( page, "#job-card", todos=True )

                if not cards:
                    info(f"Empregos | TERMO='{termo}' |  PAGINA={pagina + 1} |  SEM RESULTADOS")
                    break

                info(f"Empregos | TERMO='{termo}' | PAGINA={pagina + 1} | VAGAS={len(cards)}")

                vagas_capturadas = 0

                for v in cards:
                    try:
                        titulo_el = elemento(v, "h2 span")
                        titulo = texto(titulo_el) if titulo_el else ""

                        empresa_el = elemento(v, "h3 a")
                        empresa = texto(empresa_el) if empresa_el else ""

                        local_el = elemento(v, 'h3[title]')
                        local = texto(local_el) if local_el else ""

                        link_el = elemento(v, 'a[href*="/vaga/"]')
                        link = atributo(link_el, "href") if link_el else None

                        if (link and not link.startswith("http")):
                            link = "https://www.empregos.com.br" + link

                        descricao_el = elemento(v, ".line-clamp-5, .line-clamp-3")
                        descricao = texto(descricao_el) if descricao_el else ""

                        data_texto = ""

                        infos = elemento( v, "div.flex.gap-1.items-center", todos=True )

                        for item in infos:
                            texto_item = texto(item)

                            if "Publicada há" in texto_item:
                                data_texto = texto_item
                                break

                        vagas.append({
                            "title": titulo,
                            "extra": " descrição: " + descricao,
                            "company": empresa,
                            "location": local,
                            "link": link,
                            "source": "Empregos",
                            "posted_date": data_texto
                        })

                        vagas_capturadas += 1
                    except Exception as e:
                        warning(f"Erro ao processar vaga Empregos | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                        continue

                info(f"Empregos | TERMO='{termo}' | PAGINA={pagina + 1} | CAPTURADAS={vagas_capturadas}/{len(cards)}")

            except Exception as e:
                warning(f"Erro ao acessar Empregos | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                continue

    return vagas
