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

                page.goto(url, timeout=45000,  wait_until="networkidle")
                page.wait_for_selector('a[href*="/jobs/view/"]', timeout=15000)

                cards = elemento(page, 'a[href*="/jobs/view/"]', todos=True)
                total_cards = cards.count()

                if total_cards == 0:
                    info(f"LinkedIn | TERMO='{termo}' |  PAGINA={pagina + 1} |  SEM RESULTADOS")
                    break

                info(f"LinkedIn | TERMO='{termo}' | PAGINA={pagina + 1} | VAGAS={total_cards}")

                vagas_capturadas = 0

                for i in range(total_cards):
                    try:
                        v = cards.nth(i)
                        
                        if v.count() == 0:
                            continue

                        titulo = texto(v)

                        link = atributo(v, "href")

                        if not link:
                            continue

                        link = link.split("?")[0]

                        parent = v.locator("xpath=ancestor::li[1]")

                        if not parent.count():
                            continue

                        data = None

                        empresa = texto(elemento(parent, ".base-search-card__subtitle a"))

                        local = texto(elemento(parent, ".job-search-card__location, [class*='location']"))

                        data_iso = atributo(elemento(parent, "time"), "datetime")

                        if data_iso:
                            data = datetime.strptime(data_iso, "%Y-%m-%d")

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

                info(f"LinkedIn | TERMO='{termo}' | PAGINA={pagina + 1} | CAPTURADAS={vagas_capturadas}/{total_cards}")
            
            except Exception as e:
                warning(f"Erro ao acessar LinkedIn | TERMO='{termo}' | PAGINA={pagina + 1} | START={start} | ERRO={e}")
    ##################################################
                try:
                    warning("=" * 80)
                    warning(f"SITE: LINKEDIN")
                    warning(f"URL: {page.url}")
                    warning(f"TÍTULO: {page.title()}")
                    warning("HTML (primeiros 5000 caracteres):")
                    warning(page.content()[:5000])
                    warning("=" * 80)
                except Exception as erro_debug:
                    warning(f"Erro ao coletar informações da página: {erro_debug} | {type(erro_debug).__name__} | {erro_debug}")
    ##################################################
                continue

    return vagas
