from logging import info, warning
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
                    info(f"99Jobs | TERMO='{termo}' |  PAGINA={pagina + 1} |  SEM RESULTADOS")
                    break

                info(f"99Jobs | TERMO='{termo}' | PAGINA={pagina + 1} | VAGAS={len(cards)}")

                vagas_capturadas = 0

                for v in cards:
                    try:
                        link = v.get_attribute("href")

                        if link and not link.startswith("http"):
                            link = "https://99jobs.com" + link

                        titulo_el = v.query_selector("h1")
                        titulo = (titulo_el.text_content() or "").strip() if titulo_el else ""

                        empresa_el = v.query_selector(".opportunity-company-infos h2")
                        empresa = (empresa_el.text_content() or "").strip() if empresa_el else ""

                        local_el = v.query_selector(".opportunity-address p")
                        local = (local_el.text_content() or "").strip() if local_el else ""

                        tags_el = v.query_selector_all(".opportunity-labels .opportunity-label")
                        tags = " ".join([
                            ((tag.text_content() or "").strip().lower())
                            for tag in tags_el
                            if (tag.text_content() or "").strip()
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

                        vagas_capturadas += 1
                    except Exception as e:
                        warning(f"Erro ao processar vaga 99jobs | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                        continue

                info(f"99jobs | TERMO='{termo}' | PAGINA={pagina + 1} | CAPTURADAS={vagas_capturadas}/{len(cards)}")

            except Exception as e:
                warning(f"Erro ao acessar 99Jobs | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                continue

    return vagas
