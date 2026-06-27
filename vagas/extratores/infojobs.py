from logging import info, warning
from re import search, sub, IGNORECASE
from vagas.filtros import MAX_PAGINAS, PERIODO_DIAS
from utils.playwright import texto, atributo, elemento


def extrair_infojobs(page, termos_busca):
    info("Extraindo vagas do InfoJobs.")

    vagas = []

    for termo in termos_busca:

        termo_url = (
            termo.replace(" ", "-")
            .replace("júnior", "junior")
        )

        for pagina in range(1, MAX_PAGINAS + 1):
            url = (
                f"https://www.infojobs.com.br/"
                f"vagas-de-emprego-{termo_url}.aspx"
                f"?idw=2,3&Page={pagina}"
                f"&Antiguedad={PERIODO_DIAS}"
            )
            
            try:
                page.goto(url, timeout=30000,  wait_until="domcontentloaded")
                page.wait_for_selector(".js_rowCard[data-href]", timeout=10000)

                cards = elemento( page, ".js_rowCard[data-href]", todos=True )
                total_cards = cards.count()   

                if total_cards == 0:
                    info(f"InfoJobs | TERMO='{termo}' |  PAGINA={pagina} |  SEM RESULTADOS")
                    break

                info(f"InfoJobs | TERMO='{termo}' | PAGINA={pagina} | VAGAS={total_cards}")

                vagas_capturadas = 0

                for i in range(total_cards):
                    try:
                        v = cards.nth(i)
                        
                        if v.count() == 0:
                            continue
                    
                        link = atributo(v, "data-href")

                        if (link and not link.startswith("http")):
                            link = "https://www.infojobs.com.br" + link

                        titulo = texto(elemento(v, ".js_vacancyTitle"))

                        empresa = ""
                        empresa_els = elemento( v, "a.text-body.text-decoration-none", todos=True )

                        for j in range(empresa_els.count()):
                            el = empresa_els.nth(j)
                            texto_el = texto(el)

                            if (texto_el and texto_el.lower() != titulo.lower()):
                                empresa = (
                                    texto_el
                                    .replace("\n", " ")
                                    .strip()
                                )

                                empresa = sub(
                                    r"\s+SAIBA O QUE ISSO SIGNIFICA.*",
                                    "",
                                    empresa,
                                    flags=IGNORECASE
                                ).strip()

                                break

                        local = ""
                        local_els = elemento( v, "div.mb-8", todos=True )

                        for j in range(local_els.count()):
                            el = local_els.nth(j)
                            texto_el = texto(el)

                            if search(r"[A-Za-zÀ-ÿ\s]+ - [A-Z]{2}", texto_el):
                                local = (
                                    texto_el
                                    .split(",")[0]
                                    .strip()
                                )
                                break

                        descricao = ""
                        descricao_els = elemento( v, "div.text-medium", todos=True )

                        if descricao_els.count():
                            descricao = texto(descricao_els.nth(descricao_els.count() - 1))

                        data = texto(elemento(v, "div.text-medium.small.text-nowrap"))

                        vagas.append({
                            "title": titulo,
                            "extra": " descrição: " + descricao,
                            "company": empresa,
                            "location": local,
                            "link": link,
                            "source": "InfoJobs",
                            "posted_date": data
                        })

                        vagas_capturadas += 1
                    except Exception as e:
                        warning(f"Erro ao processar vaga InfoJobs | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
                        continue

                info(f"InfoJobs | TERMO='{termo}' | PAGINA={pagina} | CAPTURADAS={vagas_capturadas}/{total_cards}")

            except Exception as e:
                warning(f"Erro ao acessar InfoJobs | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
                continue

    return vagas
