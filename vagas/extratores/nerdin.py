from logging import info, warning
from vagas.filtros import MAX_PAGINAS
from utils.playwright import texto, atributo, elemento


def extrair_nerdin(page, termos_busca):
    info("Extraindo vagas do Nerdin.")
    vagas = []

    for termo in termos_busca:
        for pagina in range(1, MAX_PAGINAS + 1):
            try:
                url = f"https://www.nerdin.com.br/vagas.php?busca={termo.replace(' ', '+')}&pagina={pagina}&filtro_home_office=1"

                page.goto(url, timeout=30000,  wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                cards = elemento( page, ".vaga-card", todos=True )

                if not cards:
                    info(f"Nerdin | TERMO='{termo}' |  PAGINA={pagina} |  SEM RESULTADOS")
                    break

                info(f"Nerdin | TERMO='{termo}' | PAGINA={pagina} | VAGAS={len(cards)}")

                vagas_capturadas = 0

                for v in cards:
                    try:
                        nova_vaga = elemento(v, ".vaga-nova-badge")
                        if not nova_vaga:
                            continue

                        titulo_el = elemento(v, ".vaga-titulo")
                        titulo = texto(titulo_el) if titulo_el else ""

                        link_el = elemento(v, ".btn-ver-vaga")
                        link = atributo(link_el, "href") if link_el else None

                        if link and not link.startswith("http"):
                            link = "https://www.nerdin.com.br/" + link

                        empresa_el = elemento(v, ".vaga-empresa")
                        empresa = texto(empresa_el) if empresa_el else ""

                        local_el = elemento(v, ".vaga-local")
                        local = texto(local_el) if local_el else ""

                        hashtags_el = elemento( v, ".hashtag", todos=True )
                        hashtags = []

                        for h in hashtags_el:
                            valor = texto(h)

                            if valor:
                                hashtags.append(valor.replace("#", ""))

                        hashtags = " ".join(hashtags)

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
                        warning(f"Erro ao processar vaga Nerdin | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
                        continue

                info(f"Nerdin | TERMO='{termo}' | PAGINA={pagina} | CAPTURADAS={vagas_capturadas}/{len(cards)}")

            except Exception as e:
                warning(f"Erro ao acessar Nerdin | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
                continue

    return vagas
