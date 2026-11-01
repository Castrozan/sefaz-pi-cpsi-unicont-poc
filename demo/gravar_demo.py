from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

BASE_URL = "http://127.0.0.1:8000"
VIEWPORT = {"width": 1600, "height": 900}


def pause(page: Page, seconds: float) -> None:
    page.wait_for_timeout(int(seconds * 1000))


def show_caption(page: Page, text: str) -> None:
    page.evaluate(
        """text => {
            let box = document.getElementById('legenda-demo');
            if (!box) {
                box = document.createElement('div');
                box.id = 'legenda-demo';
                box.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);max-width:1180px;'
                  + 'background:rgba(16,30,38,.94);color:#fff;font:500 25px/1.35 Plex,sans-serif;padding:14px 26px;'
                  + 'border-radius:8px;z-index:9999;text-align:center';
                document.body.appendChild(box);
            }
            box.textContent = text;
        }""",
        text,
    )


def narrate(page: Page, text: str, seconds: float) -> None:
    show_caption(page, text)
    pause(page, seconds)


def scroll_to(page: Page, selector: str) -> None:
    page.locator(selector).first.evaluate("element => element.scrollIntoView({behavior: 'smooth', block: 'start'})")
    pause(page, 1.2)


def record(process_number: str, clean_process_number: str, output_directory: Path) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(
            viewport=VIEWPORT, record_video_dir=str(output_directory), record_video_size=VIEWPORT
        )
        page = context.new_page()

        page.goto(BASE_URL)
        narrate(
            page,
            "Os 56 Núcleos de Controle Interno analisaram 6.735 processos em abril de 2026, a 163,5 minutos cada.",
            8,
        )
        narrate(page, "Esta prova de conceito usa só dados sintéticos, criados para a demonstração.", 7)
        narrate(page, "A fila chega ordenada por risco e valor, para o analista começar pelo que mais importa.", 8)
        scroll_to(page, ".alertas")
        narrate(page, "O sistema aponta a mesma nota fiscal em processos diferentes, antes de pagar duas vezes.", 7)
        page.select_option("select[name=risco]", "alto")
        page.click(".filtros button")
        narrate(page, "Filtros por núcleo, risco e situação organizam o trabalho entre os núcleos.", 6)

        page.goto(f"{BASE_URL}/processo?numero={process_number}")
        narrate(page, "Antes da leitura, o analista já tem um resumo do processo e o alerta de risco.", 9)
        scroll_to(page, ".criterios")
        narrate(
            page,
            "Cada critério do checklist traz situação, fundamento e o trecho do documento que sustenta a conclusão.",
            10,
        )
        page.locator("tr.nao_conforme .citacao").first.click()
        page.wait_for_selector("#citacao")
        page.locator("#citacao").scroll_into_view_if_needed()
        narrate(
            page,
            "Um clique leva ao documento, com o trecho citado destacado. Citação que não confere com o texto é descartada.",
            10,
        )
        page.go_back()
        scroll_to(page, ".decisao")
        narrate(page, "O sistema redige o parecer preliminar. O analista lê, edita e decide.", 8)
        page.fill("textarea[name=parecer]", page.input_value("textarea[name=parecer]") + "\n\nRevisado pelo analista.")
        page.fill("input[name=analista]", "Analista de Demonstração")
        page.fill("input[name=justificativa]", "Apontamentos confirmados; devolver à unidade para saneamento.")
        pause(page, 2)
        narrate(page, "Se devolver, nada é enviado. O envio ao SINCIN+ só existe depois da aprovação humana.", 7)
        page.click("button[value=devolver]")
        page.wait_for_load_state()
        narrate(page, "A decisão fica registrada com o nome do analista.", 5)

        page.goto(f"{BASE_URL}/processo?numero={clean_process_number}")
        scroll_to(page, ".decisao")
        page.fill("input[name=analista]", "Analista de Demonstração")
        narrate(page, "Em um processo sem apontamentos, o analista aprova.", 5)
        page.click("button[value=aprovar]")
        page.wait_for_selector(".sucesso")
        narrate(
            page,
            "O parecer aprovado segue para a interface do SINCIN+, aqui simulada até a entrega das APIs no Marco P1.",
            8,
        )

        page.goto(f"{BASE_URL}/auditoria?numero={process_number}")
        narrate(page, "Toda análise gera um registro auditável: documentos, critérios, resultado, modelo e versão.", 8)
        narrate(page, "A cadeia de hashes revela a alteração de entradas já registradas.", 6)

        page.goto(f"{BASE_URL}/busca")
        page.fill("input[name=texto]", "ressalva")
        page.select_option("select[name=tipo]", "atesto")
        page.click(".filtros button")
        page.wait_for_selector(".contagem")
        narrate(page, "A busca encontra qualquer documento por tipo, campo ou palavra-chave, em milissegundos.", 8)
        page.goto(f"{BASE_URL}/busca?tipo=contrato&minimo=500000")
        narrate(page, "Também por campo extraído: aqui, contratos acima de R$ 500 mil.", 7)

        page.goto(f"{BASE_URL}/painel")
        narrate(page, "O painel mostra as inconsistências mais frequentes e os núcleos que pedem atenção.", 8)

        page.goto(f"{BASE_URL}/avaliacao")
        narrate(page, "A avaliação mede as barras do edital, com um ciclo de 500 processos sintéticos.", 8)
        scroll_to(page, "section:nth-of-type(2)")
        narrate(
            page,
            "As falhas aparecem por critério. O gabarito é sintético; o desempenho real só virá com dados da Fase 1.",
            10,
        )
        narrate(
            page, "Integração real, regras oficiais da UNICONT e medição com analistas ficam para as fases do CPSI.", 8
        )
        context.close()
        browser.close()


if __name__ == "__main__":
    record(sys.argv[1], sys.argv[2], Path(sys.argv[3]))
