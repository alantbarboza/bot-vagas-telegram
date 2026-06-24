from datetime import datetime
from logging import info, warning
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
                    info(f"Solides | TERMO='{termo}' |  PAGINA={pagina + 1} |  SEM RESULTADOS")
                    break

                info(f"Solides | TERMO='{termo}' | PAGINA={pagina + 1} | VAGAS={len(cards)}")

                vagas_capturadas = 0

                for v in cards:
                    try:
                        titulo_el = v.query_selector("h2 a")
                        if not titulo_el:
                            continue

                        titulo = (titulo_el.get_attribute("title") or (titulo_el.text_content() or "").strip())

                        link = titulo_el.get_attribute("href")
                        if link and not link.startswith("http"):
                            link = "https://vagas.solides.com.br" + link

                        empresa_el = v.query_selector('[data-cy="vacancy-company-name"]')
                        empresa = (empresa_el.text_content() or "").strip() if empresa_el else ""

                        local_el = v.query_selector('p:has(span[data-icon="location_on"])')
                        local = (local_el.text_content() or "").strip() if local_el else ""

                        data_el = v.query_selector("time")
                        data = None
                        if data_el:
                            data_iso = data_el.get_attribute("datetime")
                            if data_iso:
                                data = datetime.strptime(data_iso, "%Y-%m-%d")

                        hashtags_el = v.query_selector_all("div.flex.flex-wrap.gap-2 div")
                        hashtags = " ".join([
                            ((h.text_content() or "").strip().lower())
                            for h in hashtags_el if (h.text_content() or "").strip()
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

                        vagas_capturadas += 1
                    except Exception as e:
                        warning(f"Erro ao processar vaga Solides | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                        continue

                info(f"Solides | TERMO='{termo}' | PAGINA={pagina + 1} | CAPTURADAS={vagas_capturadas}/{len(cards)}")

            except Exception as e:
                warning(f"Erro ao acessar Solides | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                continue

    return vagas
