from logging import info, warning, error
from vagas.filtros import MAX_PAGINAS

def extrair_99jobs(page, termos_busca):
    info("Extraindo vagas do 99Jobs.")

    vagas = []

    for termo in termos_busca:
        for pagina in range(1, MAX_PAGINAS + 1):

            try:
                url = (
                    f"https://99jobs.com/opportunities/filtered_search?utf8=%E2%9C%93"
                    f"&search%5Bterm%5D={termo.replace(' ', '+')}"
                    "&search%5Bacting_mode%5D%5B%5D=remote"
                    "&search%5Bacting_mode%5D%5B%5D=hybrid"
                    f"&page={pagina}"
                )

                page.goto(url, timeout=30000,  wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                cards = page.query_selector_all("a[href*='/jobs/']")

                if not cards:
                    break

                for card in cards:
                    try:
                        link = card.get_attribute("href")

                        if link and not link.startswith("http"):
                            link = "https://99jobs.com" + link

                        titulo_el = card.query_selector("h1")
                        titulo = titulo_el.inner_text().strip() if titulo_el else ""

                        empresa_el = card.query_selector(".opportunity-company-infos h2")
                        empresa = empresa_el.inner_text().strip() if empresa_el else ""

                        local_el = card.query_selector(".opportunity-address p")
                        local = local_el.inner_text().strip() if local_el else ""

                        tags_el = card.query_selector_all(".opportunity-labels .opportunity-label")
                        tags = " ".join([
                            tag.inner_text().strip().lower()
                            for tag in tags_el
                            if tag.inner_text().strip()
                        ])

                        local = (f"{local} {tags}")
                        
                        vagas.append({
                            "title": titulo,
                            "extra": " tags: " + tags,
                            "company": empresa,
                            "location": local,
                            "link": link,
                            "source": "99jobs",
                            "posted_date": "O site não informa a data de publicação."
                        })

                    except Exception as e:
                        warning(f"Erro ao processar vaga: {e}")
                        continue

            except Exception as e:
                error(f"Erro ao acessar o site 99Jobs: {e}")
                continue

    return vagas
