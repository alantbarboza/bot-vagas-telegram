from playwright.sync_api import sync_playwright
from logging import info, warning
from vagas.filtros import validar_periodo, remover_duplicadas
from utils.navegador import criar_navegador, criar_pagina
from vagas.extratores.linkedin import extrair_linkedin
from vagas.extratores.nerdin import extrair_nerdin
from vagas.extratores.solides import extrair_solides
from vagas.extratores.empregos import extrair_empregos
from vagas.extratores.infojobs import extrair_infojobs
from vagas.extratores.jobs99 import extrair_99jobs

def buscar_vagas(termos_busca):
    with sync_playwright() as p:
        browser, context = criar_navegador(p)
        vagas = []

        extratores = [
            ("LinkedIn", extrair_linkedin),
            ("Nerdin", extrair_nerdin),
            ("Solides", extrair_solides),
            ("Empregos", extrair_empregos),
            ("InfoJobs", extrair_infojobs),
            ("99Jobs", extrair_99jobs),
        ]

        try:
            for site, extrator in extratores:
                page = None

                try:
                    page = criar_pagina(context)

                    page.goto("about:blank")
                    
                    vagas += extrator(page, termos_busca)

                except Exception as e:
                    warning(f"Erro fatal {site}: {e}")

                finally:
                    if page and not page.is_closed():
                       page.close()

        finally:
            context.close()
            browser.close()

    info("Busca de vagas concluída. Validando conteúdo e removendo duplicadas...")
    vagas = remover_duplicadas(vagas)
    vagas = validar_periodo(vagas)

    return vagas
