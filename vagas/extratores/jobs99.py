from logging import info, warning
from vagas.filtros import MAX_PAGINAS
from utils.playwright import texto, atributo, elemento


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
                page.wait_for_selector("a[href*='/jobs/']", timeout=10000)

                cards = elemento(page, "a[href*='/jobs/']", todos=True)
                total_cards = cards.count()

                if total_cards == 0:
                    info(f"99Jobs | TERMO='{termo}' |  PAGINA={pagina} |  SEM RESULTADOS")
                    break

                info(f"99Jobs | TERMO='{termo}' | PAGINA={pagina} | VAGAS={total_cards}")

                vagas_capturadas = 0

                for i in range(total_cards):
                    try:
                        v = cards.nth(i)
                        
                        if v.count() == 0:
                            continue

                        link = atributo(v, "href")

                        if link and not link.startswith("http"):
                            link = "https://99jobs.com" + link

                        titulo = texto(elemento(v, "h1"))

                        empresa = texto(elemento(v, ".opportunity-company-infos h2"))

                        local = texto(elemento(v, ".opportunity-address p"))

                        tags_el = elemento( v, ".opportunity-labels .opportunity-label", todos=True )
                        tags = []

                        for j in range(tags_el.count()):
                            tag = tags_el.nth(j)
                            valor = texto(tag)

                            if valor:
                                tags.append(valor.lower())

                        tags = " ".join(tags)

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
                        warning(f"Erro ao processar vaga 99jobs | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
                        continue

                info(f"99jobs | TERMO='{termo}' | PAGINA={pagina} | CAPTURADAS={vagas_capturadas}/{total_cards}")

            except Exception as e:
                warning(f"Erro ao acessar 99Jobs | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
                continue

    return vagas
