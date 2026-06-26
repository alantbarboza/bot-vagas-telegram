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
                page.wait_for_timeout(3000)

                cards = elemento( page, ".js_rowCard[data-href]", todos=True )   

                if not cards:
                    info(f"InfoJobs | TERMO='{termo}' |  PAGINA={pagina} |  SEM RESULTADOS")
                    break

                info(f"InfoJobs | TERMO='{termo}' | PAGINA={pagina} | VAGAS={len(cards)}")

                vagas_capturadas = 0

                for v in cards:
                    try:
                        link = atributo(v, "data-href")

                        if (link and not link.startswith("http")):
                            link = "https://www.infojobs.com.br" + link

                        titulo_el = elemento(v, ".js_vacancyTitle")
                        titulo = texto(titulo_el) if titulo_el else "" 

                        empresa = ""
                        empresa_els = elemento( v, "a.text-body.text-decoration-none", todos=True )

                        for el in empresa_els:
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

                        for el in local_els:
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

                        if descricao_els:
                            descricao = texto(descricao_els[-1])

                        data = ""
                        data_el = elemento(v, "div.text-medium.small.text-nowrap")

                        if data_el:
                            data = texto(data_el)

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

                info(f"InfoJobs | TERMO='{termo}' | PAGINA={pagina} | CAPTURADAS={vagas_capturadas}/{len(cards)}")

            except Exception as e:
                warning(f"Erro ao acessar InfoJobs | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
                continue

    return vagas
