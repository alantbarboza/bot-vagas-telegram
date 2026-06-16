from logging import info, warning, error
from vagas.filtros import MAX_PAGINAS

def extrair_nerdin(page, termos_busca):
    info("Extraindo vagas do Nerdin.")
    vagas = []

    for termo in termos_busca:
        for pagina in range(1, MAX_PAGINAS + 1):
            try:
                url = f"https://www.nerdin.com.br/vagas.php?busca={termo.replace(' ', '+')}&pagina={pagina}&filtro_home_office=1"

                page.goto(url, timeout=30000,  wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                cards = page.query_selector_all(".vaga-card")

                if not cards:
                    break

                for v in cards:
                    try:
                        nova_vaga = v.query_selector(".vaga-nova-badge")
                        if not nova_vaga:
                            continue

                        titulo_el = v.query_selector(".vaga-titulo")
                        titulo = titulo_el.inner_text().strip() if titulo_el else ""

                        link_el = v.query_selector(".btn-ver-vaga")
                        link = link_el.get_attribute("href") if link_el else None

                        if link and not link.startswith("http"):
                            link = "https://www.nerdin.com.br/" + link

                        empresa_el = v.query_selector(".vaga-empresa")
                        empresa = empresa_el.inner_text().strip() if empresa_el else ""

                        local_el = v.query_selector(".vaga-local")
                        local = local_el.inner_text().strip() if local_el else ""

                        hashtags_el = v.query_selector_all(".hashtag")
                        hashtags = " ".join([
                            h.inner_text().strip().replace("#", "") for h in hashtags_el
                        ])

                        vagas.append({
                            "title": titulo,
                            "extra": " hashtags: " + hashtags,
                            "company": empresa,
                            "location": local,
                            "link": link,
                            "source": "Nerdin",
                            "posted_date": "Últimas 48h",
                        })

                    except Exception as e:
                        warning(f"Erro ao processar vaga, {e}")
                        continue

            except Exception as e:
                error(f"Erro ao acessar o site Nerdin: {e}")
                continue

    return vagas
