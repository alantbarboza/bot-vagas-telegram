from logging import info, warning, error
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
                    break

                for card in cards:
                    try:
                        link = card.get_attribute("data-href")

                        if (link and not link.startswith("http")):
                            link = "https://www.infojobs.com.br" + link

                        titulo_el = card.query_selector(".js_vacancyTitle")
                        titulo = titulo_el.inner_text().strip() if titulo_el else ""   

                        empresa = ""
                        empresa_els = card.query_selector_all("a.text-body.text-decoration-none")

                        for el in empresa_els:
                            texto = (el.inner_text().strip())

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
                        local_els = card.query_selector_all(
                            "div.mb-8"
                        )

                        for el in local_els:
                            texto = (
                                el.inner_text()
                                .strip()
                            )

                            if search(r"[A-Za-zÀ-ÿ\s]+ - [A-Z]{2}", texto):
                                local = (
                                    texto
                                    .split(",")[0]
                                    .strip()
                                )
                                break

                        descricao = ""
                        descricao_els = card.query_selector_all(
                            "div.text-medium"
                        )

                        if descricao_els:
                            descricao = (
                                descricao_els[-1]
                                .inner_text()
                                .strip()
                            )

                        data = ""
                        data_el = card.query_selector(
                            "div.text-medium.small.text-nowrap"
                        )

                        if data_el:
                            data = (
                                data_el.inner_text()
                                .strip()
                            )

                        vagas.append({
                            "title": titulo,
                            "extra": " descrição: " + descricao,
                            "company": empresa,
                            "location": local,
                            "link": link,
                            "source": "InfoJobs",
                            "posted_date": data
                        })

                    except Exception as e:
                        warning(f"Erro ao processar vaga, {e}")
                        continue

            except Exception as e:
                error(f"Erro ao acessar o site InfoJobs:  {e}")
                continue

    return vagas
