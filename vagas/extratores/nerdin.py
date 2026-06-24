from logging import info, warning
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
                    info(f"Nerdin | TERMO='{termo}' |  PAGINA={pagina + 1} |  SEM RESULTADOS")
                    break

                info(f"Nerdin | TERMO='{termo}' | PAGINA={pagina + 1} | VAGAS={len(cards)}")

                vagas_capturadas = 0

                for v in cards:
                    try:
                        nova_vaga = v.query_selector(".vaga-nova-badge")
                        if not nova_vaga:
                            continue

                        titulo_el = v.query_selector(".vaga-titulo")
                        titulo = (titulo_el.text_content() or "").strip() if titulo_el else ""

                        link_el = v.query_selector(".btn-ver-vaga")
                        link = link_el.get_attribute("href") if link_el else None

                        if link and not link.startswith("http"):
                            link = "https://www.nerdin.com.br/" + link

                        empresa_el = v.query_selector(".vaga-empresa")
                        empresa = (empresa_el.text_content() or "").strip() if empresa_el else ""

                        local_el = v.query_selector(".vaga-local")
                        local = (local_el.text_content() or "").strip() if local_el else ""

                        hashtags_el = v.query_selector_all(".hashtag")
                        hashtags = " ".join([
                            ((h.text_content() or "").strip().replace("#", "")) for h in hashtags_el
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

                        vagas_capturadas += 1
                    except Exception as e:
                        warning(f"Erro ao processar vaga Nerdin | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                        continue

                info(f"Nerdin | TERMO='{termo}' | PAGINA={pagina + 1} | CAPTURADAS={vagas_capturadas}/{len(cards)}")

            except Exception as e:
                warning(f"Erro ao acessar Nerdin | TERMO='{termo}' | PAGINA={pagina + 1} | ERRO={e}")
                continue

    return vagas
