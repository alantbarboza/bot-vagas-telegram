def criar_navegador_humano(playwright):

    browser = playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
    )

    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        ),
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
        color_scheme="light"
    )

    page = context.new_page()

    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)

    page.set_extra_http_headers({
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Upgrade-Insecure-Requests": "1"
    })

    page.set_default_timeout(10000)
    page.set_default_navigation_timeout(10000)

    page.mouse.move(500, 300)

    return browser, page