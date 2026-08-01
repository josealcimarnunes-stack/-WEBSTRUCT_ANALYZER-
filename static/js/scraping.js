document.addEventListener('DOMContentLoaded', () => {
    const btnIniciar = document.getElementById('btn-iniciar');
    const btnMapear = document.getElementById('btn-mapear');
    const inputSeletor = document.getElementById('input-seletor');
    const statusContainer = document.getElementById('status-container');
    const statusTexto = document.getElementById('status-texto');
    const statusBarra = document.getElementById('status-barra');
    const cardAlvo = document.getElementById('card-resultado-alvo');
    const containerTabela = document.getElementById('container-tabela-elementos');
    const tabelaCorpo = document.getElementById('tabela-elementos-corpo');

    function atualizarStatus(etapa, texto, porcentagem) {
        if (!statusContainer) return;
        statusContainer.style.display = 'block';
        statusTexto.innerText = `[Etapa ${etapa}/3] ${texto}`;
        statusBarra.style.width = `${porcentagem}%`;
    }

    function ocultarStatus() {
        if (statusContainer) statusContainer.style.display = 'none';
    }

    // 🌐 INICIAR SESSÃO (Mantém janela visível)
    if (btnIniciar) {
        btnIniciar.addEventListener('click', async () => {
            const url = document.getElementById('input-url').value;
            if (!url) return alert('Por favor, informe a URL do site!');

            btnIniciar.disabled = true;
            btnMapear.disabled = true;

            atualizarStatus(1, 'Abrindo navegador e conectando à página...', 30);
            
            try {
                const resp = await fetch('/iniciar_sessao', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                const data = await resp.json();

                if (!resp.ok || data.erro) throw new Error(data.erro || 'Falha ao iniciar sessão');

                atualizarStatus(3, 'Sessão aberta! Janela pronta para inspeção.', 100);
                
                // Habilita botão de mapeamento
                btnMapear.disabled = false;
                if (inputSeletor) inputSeletor.focus();

                setTimeout(ocultarStatus, 2000);
            } catch (err) {
                alert('❌ Erro ao abrir sessão: ' + err.message);
                ocultarStatus();
            } finally {
                btnIniciar.disabled = false;
            }
        });
    }

    // 🔍 MAPEAR ELEMENTO (Destaca na tela, mapeia e minimiza)
    if (btnMapear) {
        btnMapear.addEventListener('click', async () => {
            const seletor = document.getElementById('input-seletor').value.trim();

            atualizarStatus(1, `Varrendo estrutura pelo termo '${seletor || 'Completo (body)'}'...`, 30);
            if (cardAlvo) cardAlvo.style.display = 'none';
            if (containerTabela) containerTabela.style.display = 'none';

            try {
                atualizarStatus(2, 'Inspecionando nós, classes e seletores no DOM...', 65);

                const resp = await fetch('/mapear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ seletor_alvo: seletor })
                });
                const data = await resp.json();

                if (!resp.ok || data.erro) throw new Error(data.erro || 'Erro no mapeamento');

                if (!data.elementos || data.elementos.length === 0) {
                    atualizarStatus(3, 'Nenhum elemento retornado.', 100);
                    alert('⚠️ Nenhum elemento foi encontrado com essa entrada!');
                    setTimeout(ocultarStatus, 2500);
                    return;
                }

                atualizarStatus(3, 'Mapeamento concluído! Janela minimizada em background.', 90);

                // Preenche destaque do primeiro elemento
                const primeiro = data.elementos[0];
                const tagEl = document.getElementById('alvo-tag');
                const textoEl = document.getElementById('alvo-texto');
                const cssEl = document.getElementById('alvo-css');
                const xpathEl = document.getElementById('alvo-xpath');

                if (tagEl) tagEl.innerText = primeiro.tag_name;
                if (textoEl) textoEl.innerText = primeiro.text || '(Sem texto visível)';
                if (cssEl) cssEl.innerText = primeiro.css_selector;
                if (xpathEl) xpathEl.innerText = primeiro.xpath || '-';
                if (cardAlvo) cardAlvo.style.display = 'block';

                // Preenche tabela detalhada
                if (tabelaCorpo) {
                    tabelaCorpo.innerHTML = '';
                    data.elementos.forEach((el) => {
                        const tr = document.createElement('tr');
                        const cssEscapado = encodeURIComponent(el.css_selector);
                        tr.innerHTML = `
                            <td>${el.posicao}</td>
                            <td><span class="badge bg-primary">Nível ${el.profundidade}</span></td>
                            <td><span class="badge bg-secondary">${el.tag_name}</span></td>
                            <td><small class="text-muted">Pai: &lt;${el.pai}&gt;</small></td>
                            <td>${el.id || '-'}</td>
                            <td>${el.text}</td>
                            <td><button class="btn btn-sm btn-outline-info" onclick="navigator.clipboard.writeText(decodeURIComponent('${cssEscapado}'))">Copiar CSS</button></td>
                        `;
                        tabelaCorpo.appendChild(tr);
                    });
                }

                if (containerTabela) containerTabela.style.display = 'block';
                containerTabela.scrollIntoView({ behavior: 'smooth' });

                atualizarStatus(3, `Concluído! ${data.total} elementos mapeados com sucesso.`, 100);
                setTimeout(ocultarStatus, 2500);

            } catch (err) {
                alert('❌ Erro no mapeamento: ' + err.message);
                ocultarStatus();
            }
        });
    }
});