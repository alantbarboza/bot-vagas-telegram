from datetime import datetime
from logging import info, warning, error
from vagas.filtros import MAX_PAGINAS

def extrair_linkedin(page, termos_busca):
    info("Extraindo vagas do LinkedIn.")
    vagas = []

    for termo in termos_busca:

        for pagina in range(MAX_PAGINAS):

            start = pagina * 25

            try:
                url = (
                    "https://www.linkedin.com/jobs/search/"
                    f"?keywords={termo.replace(' ', '%20')}"
                    "&location=Brazil"
                    f"&start={start}"
                )

                page.goto(url, timeout=30000,  wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                cards = page.query_selector_all(
                    'a[href*="/jobs/view/"]'
                )

                if not cards:
                    break

                #for v in cards:
                for i, v in enumerate(cards):
                    try:
                        info(f"CARD {i+1}/{len(cards)} - início")
                        #info(f"CARD {v} - início")

                        info(f"CARD {v} - lendo título")
                        #titulo = v.inner_text().strip()
                        titulo = (v.text_content() or "").strip()

                        info(f"CARD {v} - lendo link")
                        link = v.get_attribute("href")

                        if not link:
                            info(f"CARD {v} - sem link")
                            continue

                        link = link.split("?")[0]

                        info(f"CARD {v} - buscando parent")
                        parent = v.evaluate_handle(
                            'el => el.closest("li, .job-search-card")'
                        ).as_element()

                        empresa = ""
                        local = ""
                        data = None

                        if parent:
                            info(f"CARD {v} - buscando empresa")
                            empresa_el = parent.query_selector(
                                ".base-search-card__subtitle a"
                            )

                            if empresa_el:
                                info(f"CARD {v} - lendo empresa")
                                #empresa = empresa_el.inner_text().strip()
                                empresa = (empresa_el.text_content() or "").strip()

                            info(f"CARD {v} - buscando local")
                            local_el = parent.query_selector(
                                ".job-search-card__location, [class*='location']"
                            )

                            if local_el:
                                info(f"CARD {v} - lendo local")
                                #local = local_el.inner_text().strip()
                                local = (local_el.text_content() or "").strip()

                            info(f"CARD {v} - buscando data")
                            data_el = parent.query_selector("time")

                            if data_el:
                                data_iso = data_el.get_attribute("datetime")

                                if data_iso:
                                    data = datetime.strptime(
                                        data_iso,
                                        "%Y-%m-%d"
                                    )

                        info(f"CARD {v} - adicionando vaga")

                        vagas.append({
                            "title": titulo,
                            "company": empresa,
                            "location": local,
                            "link": link,
                            "source": "LinkedIn",
                            "posted_date": (
                                data.strftime("%Y-%m-%d")
                                if data else None
                            )
                        })

                        info(f"CARD {v} - concluído")

                    except Exception as e:
                        warning(f"Erro ao processar vaga, {e}")
                        continue

            except Exception as e:
                error(f"Erro ao acessar o site Linkedin: {e}")
                continue

    return vagas
