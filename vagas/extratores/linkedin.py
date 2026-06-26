from datetime import datetime
from logging import info, warning
from vagas.filtros import MAX_PAGINAS
from utils.playwright import texto, atributo, elemento


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

                page.goto(url, timeout=45000,  wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                cards = elemento( page, 'a[href*="/jobs/view/"]', todos=True )

                if not cards:
                    info(f"LinkedIn | TERMO='{termo}' |  PAGINA={pagina + 1} |  SEM RESULTADOS")
                    break

                info(f"LinkedIn | TERMO='{termo}' | PAGINA={pagina + 1} | VAGAS={len(cards)}")

                vagas_capturadas = 0

                for v in cards:
                    try:                      
                        titulo = texto(v)

                        link = atributo(v, "href")

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
                            empresa_el = elemento( parent, ".base-search-card__subtitle a" )

                            if empresa_el:
                                empresa = texto(empresa_el)

                            local_el = elemento( parent, ".job-search-card__location, [class*='location']" )

                            if local_el:
                                local = texto(local_el)

                            data_el = elemento(parent, "time")

                            if data_el:
                                data_iso = atributo(data_el, "datetime")

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

                        vagas_capturadas += 1
                    except Exception as e:
                        warning(f"Erro ao processar vaga LinkedIn | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                        continue

                info(f"LinkedIn | TERMO='{termo}' | PAGINA={pagina + 1} | CAPTURADAS={vagas_capturadas}/{len(cards)}")
            
            except Exception as e:
                warning(f"Erro ao acessar LinkedIn | TERMO='{termo}' | PAGINA={pagina + 1} | START={start} | ERRO={e}")
                continue

    return vagas
