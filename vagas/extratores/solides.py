from datetime import datetime
from logging import info, warning
from vagas.filtros import MAX_PAGINAS
from utils.playwright import texto, atributo, elemento


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

                cards = elemento( page, '[data-cy="list-vacancies"] li', todos=True )

                if not cards:
                    info(f"Solides | TERMO='{termo}' |  PAGINA={pagina} |  SEM RESULTADOS")
                    break

                info(f"Solides | TERMO='{termo}' | PAGINA={pagina} | VAGAS={len(cards)}")

                vagas_capturadas = 0

                for v in cards:
                    try:
                        titulo_el = elemento(v, "h2 a")
                        if not titulo_el:
                            continue

                        titulo = (
                            atributo(titulo_el, "title")
                            or texto(titulo_el)
                        )

                        link = atributo(titulo_el, "href")
                        if link and not link.startswith("http"):
                            link = "https://vagas.solides.com.br" + link

                        empresa_el = elemento(v, '[data-cy="vacancy-company-name"]')
                        empresa = texto(empresa_el) if empresa_el else ""

                        local_el = elemento(v, 'p:has(span[data-icon="location_on"])')
                        local = texto(local_el) if local_el else ""

                        data_el = elemento(v, "time")
                        data = None
                        if data_el:
                            data_iso = atributo(data_el, "datetime")
                            if data_iso:
                                data = datetime.strptime(data_iso, "%Y-%m-%d")

                        hashtags_el = elemento( v, "div.flex.flex-wrap.gap-2 div", todos=True )
                        hashtags = []

                        for h in hashtags_el:
                            valor = texto(h)

                            if valor:
                                hashtags.append(valor.lower())

                        hashtags = " ".join(hashtags)

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
                        warning(f"Erro ao processar vaga Solides | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
                        continue

                info(f"Solides | TERMO='{termo}' | PAGINA={pagina} | CAPTURADAS={vagas_capturadas}/{len(cards)}")

            except Exception as e:
                warning(f"Erro ao acessar Solides | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
                continue

    return vagas
