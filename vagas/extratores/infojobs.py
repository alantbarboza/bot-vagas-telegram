from logging import info, warning
from re import search, sub, IGNORECASE
from vagas.filtros import MAX_PAGINAS, PERIODO_DIAS

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

                cards = page.query_selector_all(
                    ".js_rowCard[data-href]"
                )

                if not cards:
                    info(f"InfoJobs | TERMO='{termo}' |  PAGINA={pagina + 1} |  SEM RESULTADOS")
                    break

                info(f"InfoJobs | TERMO='{termo}' | PAGINA={pagina + 1} | VAGAS={len(cards)}")

                vagas_capturadas = 0

                for v in cards:
                    try:
                        link = v.get_attribute("data-href")

                        if (link and not link.startswith("http")):
                            link = "https://www.infojobs.com.br" + link

                        titulo_el = v.query_selector(".js_vacancyTitle")
                        titulo = (titulo_el.text_content() or "").strip() if titulo_el else "" 

                        empresa = ""
                        empresa_els = v.query_selector_all("a.text-body.text-decoration-none")

                        for el in empresa_els:
                            texto = ((el.text_content() or "").strip())

                            if (texto and texto.lower() != titulo.lower()):
                                empresa = (
                                    texto
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
                        local_els = v.query_selector_all(
                            "div.mb-8"
                        )

                        for el in local_els:
                            texto = ((el.text_content() or "").strip())

                            if search(r"[A-Za-zÀ-ÿ\s]+ - [A-Z]{2}", texto):
                                local = (
                                    texto
                                    .split(",")[0]
                                    .strip()
                                )
                                break

                        descricao = ""
                        descricao_els = v.query_selector_all(
                            "div.text-medium"
                        )

                        if descricao_els:
                            descricao = ((descricao_els[-1].text_content() or "").strip())

                        data = ""
                        data_el = v.query_selector(
                            "div.text-medium.small.text-nowrap"
                        )

                        if data_el:
                            data = ((data_el.text_content() or "").strip())

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
                        warning(f"Erro ao processar vaga InfoJobs | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                        continue

                info(f"InfoJobs | TERMO='{termo}' | PAGINA={pagina + 1} | CAPTURADAS={vagas_capturadas}/{len(cards)}")

            except Exception as e:
                warning(f"Erro ao acessar InfoJobs | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                continue

    return vagas
