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

                page.goto(url, timeout=45000,  wait_until="networkidle")
                page.wait_for_selector(".vaga-card", timeout=15000)

                cards = elemento(page, ".vaga-card", todos=True)
                total_cards = cards.count()

                if total_cards == 0:
                    info(f"Nerdin | TERMO='{termo}' |  PAGINA={pagina} |  SEM RESULTADOS")
                    break

                info(f"Nerdin | TERMO='{termo}' | PAGINA={pagina} | VAGAS={total_cards}")

                vagas_capturadas = 0

                for i in range(total_cards):
                    try:
                        v = cards.nth(i)

                        if v.count() == 0:
                            continue
                        
                        nova_vaga = elemento(v, ".vaga-nova-badge")
                        if not nova_vaga:
                            continue

                        titulo = texto(elemento(v, ".vaga-titulo"))

                        link = atributo(elemento(v, ".btn-ver-vaga"), "href")

                        if link and not link.startswith("http"):
                            link = "https://www.nerdin.com.br/" + link

                        empresa = texto(elemento(v, ".vaga-empresa"))

                        local = texto(elemento(v, ".vaga-local"))

                        hashtags_el = elemento( v, ".hashtag", todos=True )
                        hashtags = []

                        for j in range(hashtags_el.count()):
                            h = hashtags_el.nth(j)
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

                info(f"Nerdin | TERMO='{termo}' | PAGINA={pagina} | CAPTURADAS={vagas_capturadas}/{total_cards}")

            except Exception as e:
                warning(f"Erro ao acessar Nerdin | TERMO='{termo}' | PAGINA={pagina} | ERRO={e}")
    ##################################################
                try:
                    warning("=" * 80)
                    warning(f"SITE: NERDIN")
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
