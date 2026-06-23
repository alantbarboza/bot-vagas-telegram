from playwright.sync_api import sync_playwright
from logging import info
from vagas.filtros import validar_periodo, remover_duplicadas
from utils.navegador import criar_navegador_humano

from vagas.extratores.linkedin import extrair_linkedin
from vagas.extratores.nerdin import extrair_nerdin
from vagas.extratores.solides import extrair_solides
from vagas.extratores.empregos import extrair_empregos
from vagas.extratores.infojobs import extrair_infojobs
from vagas.extratores.jobs99 import extrair_99jobs

def buscar_vagas(termos_busca):
    with sync_playwright() as p:
        browser, page = criar_navegador_humano(p)
        vagas = []

        vagas += extrair_linkedin(page, termos_busca)
        #vagas += extrair_nerdin(page, termos_busca)
        #vagas += extrair_solides(page, termos_busca)
        #vagas += extrair_empregos(page, termos_busca)
        #vagas += extrair_infojobs(page, termos_busca)
        #vagas += extrair_99jobs(page, termos_busca)

        browser.close()

    info("Busca de vagas concluída. Validando conteúdo e removendo duplicadas...")
    vagas = remover_duplicadas(vagas)
    vagas = validar_periodo(vagas)

    return vagas
