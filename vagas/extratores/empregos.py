from base64 import b64encode
from json import dumps
from logging import info, warning, error
from vagas.filtros import MAX_PAGINAS, PERIODO_DIAS

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

                cards = page.query_selector_all("#job-card")

                if not cards:
                    break

                for v in cards:
                    try:
                        titulo_el = v.query_selector("h2 span")
                        titulo = titulo_el.inner_text().strip() if titulo_el else ""

                        empresa_el = v.query_selector("h3 a")
                        empresa = empresa_el.inner_text().strip() if empresa_el else ""

                        local_el = v.query_selector('h3[title]')
                        local = local_el.inner_text().strip() if local_el else ""

                        link_el = v.query_selector('a[href*="/vaga/"]')
                        link = link_el.get_attribute("href") if link_el else None

                        if (link and not link.startswith("http")):
                            link = "https://www.empregos.com.br" + link

                        descricao_el = v.query_selector(".line-clamp-5, .line-clamp-3")
                        descricao = descricao_el.inner_text().strip() if descricao_el else ""

                        data_texto = ""

                        infos = v.query_selector_all( "div.flex.gap-1.items-center" )

                        for item in infos:
                            texto = item.inner_text().strip()

                            if "Publicada há" in texto:
                                data_texto = texto
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

                    except Exception as e:
                        warning(f"Erro ao processar vaga, {e}")
                        continue

            except Exception as e:
                error(f"Erro ao acessar o site Empregos: {e}")
                continue

    return vagas
