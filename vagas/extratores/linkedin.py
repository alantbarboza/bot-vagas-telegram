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

                for v in cards:
                    try:
                        titulo = v.inner_text().strip()

                        link = v.get_attribute("href")

                        if not link:
                            continue

                        link = link.split("?")[0]

                        parent = v.evaluate_handle(
                            'el => el.closest("li, .job-search-card")'
                        ).as_element()

                        empresa = ""
                        local = ""
                        data = None

                        if parent:
                            empresa_el = parent.query_selector(
                                ".base-search-card__subtitle a"
                            )

                            if empresa_el:
                                empresa = empresa_el.inner_text().strip()

                            local_el = parent.query_selector(
                                ".job-search-card__location, [class*='location']"
                            )

                            if local_el:
                                local = local_el.inner_text().strip()

                            data_el = parent.query_selector("time")

                            if data_el:
                                data_iso = data_el.get_attribute("datetime")

                                if data_iso:
                                    data = datetime.strptime(
                                        data_iso,
                                        "%Y-%m-%d"
                                    )

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

                    except Exception as e:
                        warning(f"Erro ao processar vaga, {e}")
                        continue

            except Exception as e:
                error(f"Erro ao acessar o site Linkedin: {e}")
                continue

    return vagas
