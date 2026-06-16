from datetime import datetime
from logging import info, warning, error
from vagas.filtros import MAX_PAGINAS

def extrair_solides(page, termos_busca):
    info("Extraindo vagas do Solides.")
    vagas = []

    for termo in termos_busca:
        termo_url = termo.replace(" ", "-")

        for pagina in range(1, MAX_PAGINAS + 1):

            url = (
                f"https://vagas.solides.com.br/vagas/todos/"
                f"{termo_url}"
                f"?jobsType=remoto%2Chibrido"
                f"&seniorities=junior"
                f"&page={pagina}"
            )

            try:
                page.goto(url, timeout=30000,  wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                cards = page.query_selector_all('[data-cy="list-vacancies"] li')

                if not cards:
                    break

                for v in cards:
                    try:
                        titulo_el = v.query_selector("h2 a")
                        if not titulo_el:
                            continue

                        titulo = titulo_el.get_attribute("title") or titulo_el.inner_text().strip()

                        link = titulo_el.get_attribute("href")
                        if link and not link.startswith("http"):
                            link = "https://vagas.solides.com.br" + link

                        empresa_el = v.query_selector('[data-cy="vacancy-company-name"]')
                        empresa = empresa_el.inner_text().strip() if empresa_el else ""

                        local_el = v.query_selector('p:has(span[data-icon="location_on"])')
                        local = local_el.inner_text().strip() if local_el else ""

                        data_el = v.query_selector("time")
                        data = None
                        if data_el:
                            data_iso = data_el.get_attribute("datetime")
                            if data_iso:
                                data = datetime.strptime(data_iso, "%Y-%m-%d")

                        hashtags_el = v.query_selector_all("div.flex.flex-wrap.gap-2 div")
                        hashtags = " ".join([
                            h.inner_text().strip().lower()
                            for h in hashtags_el if h.inner_text()
                        ])

                        vagas.append({
                            "title": titulo,
                            "extra": " hashtags: " + hashtags,
                            "company": empresa,
                            "location": local,
                            "link": link,
                            "source": "Solides",
                            "posted_date": data.strftime("%Y-%m-%d") if data else None,
                        })

                    except Exception as e:
                        warning(f"Erro ao processar vaga, {e}")
                        continue

            except Exception as e:
                error(f"Erro ao acessar o site Solides: {e}")
                continue

    return vagas
