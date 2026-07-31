let dadosMapeados = [];
let ultimosResultados = [];
let totalElementos = 0;
let urlParaMapear = '';
let elementosCompletos = [];

// VARIÁVEIS PARA COMPARAÇÃO MANUAL
let mapasSelecionados = [];
let mapasDisponiveis = [];

function mostrarToast(mensagem, tipo = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = mensagem;
    toast.className = 'toast toast-' + tipo;
    toast.style.display = 'block';
    setTimeout(function() { toast.style.display = 'none'; }, 4000);
}

// ============================================
// MOSTRA INFORMAÇÕES DA URL DIGITADA
// ============================================
async function mostrarInfoUrl() {
    const url = document.getElementById('urlInput').value.trim();
    const infoDiv = document.getElementById('urlInfo');
    const conteudo = document.getElementById('urlInfoConteudo');
    
    if (!url) {
        infoDiv.style.display = 'none';
        return;
    }
    
    try {
        const params = new URLSearchParams();
        params.append('url', url);
        
        const response = await fetch('/verificar_mapa?' + params.toString(), {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.existe) {
            conteudo.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span style="color: #3fb950;">💡</span>
                    <span style="color: #8b949e; font-size: 13px;">
                        Existe <strong style="color: #e6edf3;">${data.total_mapas || 1}</strong> mapa(s) salvo(s) para esta URL
                    </span>
                    <span style="color: #484f58;">|</span>
                    <span style="color: #8b949e; font-size: 13px;">
                        Último: <strong style="color: #58a6ff;">${data.data}</strong>
                    </span>
                    <span style="color: #484f58;">|</span>
                    <span style="color: #8b949e; font-size: 13px;">
                        <strong style="color: #d29922;">${data.total_elementos}</strong> elementos
                    </span>
                </div>
            `;
            infoDiv.style.borderColor = '#3fb950';
            infoDiv.style.display = 'block';
        } else {
            conteudo.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span style="color: #d29922;">📭</span>
                    <span style="color: #8b949e; font-size: 13px;">
                        Nenhum mapa salvo para esta URL
                    </span>
                    <span style="color: #484f58;">|</span>
                    <span style="color: #8b949e; font-size: 13px;">
                        Clique em <strong style="color: #58a6ff;">"Map"</strong> para criar um novo
                    </span>
                </div>
            `;
            infoDiv.style.borderColor = '#d29922';
            infoDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Erro ao verificar URL:', error);
        infoDiv.style.display = 'none';
    }
}

// ============================================
// MAPEAR (COM FOTO RÁPIDA + 3 SEGUNDOS)
// ============================================
async function mapear() {
    console.log('🔥 Botão Map clicado!');
    const url = document.getElementById('urlInput').value.trim();
    console.log('📌 URL:', url);

    if (!url) {
        mostrarToast('Digite uma URL!', 'error');
        return;
    }
    urlParaMapear = url;

    const btn = document.getElementById('btnPrincipal');
    btn.innerHTML = '⏳ Mapeando...';
    btn.disabled = true;
    btn.style.opacity = '0.8';
    btn.style.cursor = 'wait';

    document.getElementById('urlInput').disabled = true;
    document.getElementById('urlInput').style.opacity = '0.6';

    try {
        const responsePreview = await fetch('/previa_rapida', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        const dataPreview = await responsePreview.json();

        const modalBody = document.getElementById('modalBodyConfirm');
        const confirmUrl = document.getElementById('confirmUrl');
        const previewDiv = document.getElementById('previaPagina');
        const previewImg = document.getElementById('screenshotPreview');

        confirmUrl.textContent = url;

        let fotoSrc = '';
        if (dataPreview && dataPreview.screenshot) {
            fotoSrc = 'data:image/png;base64,' + dataPreview.screenshot;
            if (previewImg) previewImg.src = fotoSrc;
            if (previewDiv) previewDiv.style.display = 'block';
        } else {
            if (previewDiv) previewDiv.style.display = 'none';
        }

        modalBody.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div style="background: #0d1117; padding: 12px; border-radius: 8px; border-left: 4px solid #58a6ff;">
                    <p style="color: #58a6ff; font-weight: 600; margin: 0;">📸 Prévia da página</p>
                    <p style="color: #8b949e; font-size: 13px; margin: 4px 0 0 0;">
                        Aguarde... verificando mapa salvo.
                    </p>
                </div>
                <div id="previaPagina" style="margin-top: 10px; text-align: center; display: ${fotoSrc ? 'block' : 'none'};">
                    <img id="screenshotPreview" src="${fotoSrc}" alt="Prévia da página" style="max-width: 100%; max-height: 300px; border-radius: 8px; border: 1px solid #30363d;">
                    <p style="color: #8b949e; font-size: 12px; margin-top: 4px;">📸 Prévia da página que será mapeada</p>
                </div>
                <div id="infoMapaSalvo" style="display: none; margin-top: 10px; padding: 12px; background: #0d1117; border-radius: 8px; border-left: 4px solid #3fb950;">
                    <p style="color: #3fb950; font-weight: 600; margin: 0;">✅ Mapa salvo encontrado!</p>
                    <p id="infoMapaSalvoDetalhes" style="color: #8b949e; margin: 4px 0 0 0; font-size: 13px;"></p>
                </div>
            </div>
        `;

        document.getElementById('confirmModal').style.display = 'flex';

        await new Promise(resolve => setTimeout(resolve, 3000));

        const params = new URLSearchParams();
        params.append('url', url);
        const responseCheck = await fetch('/verificar_mapa?' + params.toString(), {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        const dataCheck = await responseCheck.json();

        console.log('✅ dataCheck recebido:', dataCheck);

        const infoMapaSalvo = document.getElementById('infoMapaSalvo');
        const infoDetalhes = document.getElementById('infoMapaSalvoDetalhes');

        if (dataCheck.existe) {
            infoMapaSalvo.style.display = 'block';
            infoDetalhes.textContent = `📅 ${dataCheck.data} — 📊 ${dataCheck.total_elementos} elementos`;
        } else {
            infoMapaSalvo.style.display = 'none';
        }

    } catch (error) {
        console.error('❌ Erro ao preparar mapeamento:', error);
        mostrarToast('Erro ao carregar prévia da página', 'error');
        document.getElementById('confirmModal').style.display = 'flex';

        const btn = document.getElementById('btnPrincipal');
        btn.innerHTML = '🚀 Map';
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.style.cursor = 'pointer';
        document.getElementById('urlInput').disabled = false;
        document.getElementById('urlInput').style.opacity = '1';
    }
}

// ============================================
// CONFIRMAR MAPEAMENTO (COM PROGRESSO)
// ============================================
async function confirmarMapeamento(confirmado) {
    document.getElementById('confirmModal').style.display = 'none';

    if (!confirmado) {
        document.getElementById('statusMapeamento').innerHTML = '❌ Mapeamento cancelado!';
        document.getElementById('statusMapeamento').style.color = '#f85149';
        mostrarToast('Mapeamento cancelado!', 'error');
        
        document.getElementById('urlInput').disabled = false;
        document.getElementById('urlInput').style.opacity = '1';
        
        alternarBotao(true);
        dadosMapeados = [];
        elementosCompletos = [];
        totalElementos = 0;
        document.getElementById('urlInfo').style.display = 'none';
        document.getElementById('areaDecisao').style.display = 'none';
        document.getElementById('areaCarregarMapa').style.display = 'none';
        
        return;
    }

    const status = document.getElementById('statusMapeamento');
    const botao = document.getElementById('btnPrincipal');
    botao.disabled = true;
    botao.innerHTML = '⏳ Mapeando...';

    const progressoContainer = document.getElementById('progressoContainer');
    const sucessoContainer = document.getElementById('sucessoContainer');
    progressoContainer.style.display = 'block';
    sucessoContainer.style.display = 'none';

    const barra = document.getElementById('progressoBarra');
    const porcentagem = document.getElementById('progressoPorcentagem');
    const mensagem = document.getElementById('progressoMensagem');

    barra.style.width = '0%';
    porcentagem.textContent = '0%';
    mensagem.textContent = '⏳ Iniciando mapeamento...';

    try {
        const eventSource = new EventSource('/mapear_progresso?url=' + encodeURIComponent(urlParaMapear));
        
        let dadosFinal = [];

        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.status === 'progresso') {
                barra.style.width = data.percentual + '%';
                porcentagem.textContent = data.percentual + '%';
                mensagem.textContent = data.mensagem;
                
                document.getElementById('progressoAtual').textContent = data.atual;
                document.getElementById('progressoTotal').textContent = data.total;
                
            } else if (data.status === 'concluido') {
                barra.style.width = '100%';
                porcentagem.textContent = '100%';
                mensagem.textContent = '✅ Mapeamento concluído!';
                
                dadosFinal = data.dados;
                
                eventSource.close();
                
                dadosMapeados = dadosFinal;
                elementosCompletos = dadosMapeados;
                totalElementos = dadosMapeados.length;
                
                progressoContainer.style.display = 'none';
                sucessoContainer.style.display = 'block';
                document.getElementById('sucessoDetalhes').textContent = totalElementos + ' elementos encontrados';
                
                status.innerHTML = '✅ ' + totalElementos + ' elementos mapeados!';
                status.style.color = '#3fb950';
                mostrarToast('✅ ' + totalElementos + ' elementos mapeados com sucesso!', 'success');
                
                mostrarResultados(dadosMapeados);
                
                document.getElementById('areaReiniciar').style.display = 'block';
                document.getElementById('btnPrincipal').style.display = 'none';
                
                botao.disabled = false;
                botao.innerHTML = '🚀 Map';
            }
        };
        
        eventSource.onerror = function() {
            mostrarToast('❌ Erro na conexão com o servidor', 'error');
            eventSource.close();
            botao.disabled = false;
            botao.innerHTML = '🚀 Map';
            document.getElementById('urlInput').disabled = false;
            document.getElementById('urlInput').style.opacity = '1';
        };
        
    } catch (error) {
        status.innerHTML = '❌ Erro: ' + error.message;
        status.style.color = '#f85149';
        progressoContainer.style.display = 'none';
        mostrarToast('Erro: ' + error.message, 'error');
        botao.disabled = false;
        botao.innerHTML = '🚀 Map';
        document.getElementById('urlInput').disabled = false;
        document.getElementById('urlInput').style.opacity = '1';
    }
}

// ============================================
// CARREGAR MAPA DIRETO DO MODAL
// ============================================
async function carregarMapaSalvoDireto() {
    const url = document.getElementById('urlInput').value.trim();
    
    if (!url) {
        mostrarToast('❌ Digite uma URL primeiro!', 'error');
        return;
    }
    
    mostrarToast('📂 Carregando mapa do banco...', 'info');
    
    try {
        const params = new URLSearchParams();
        params.append('url', url);
        
        const response = await fetch('/carregar_mapa?' + params.toString(), {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            const textoErro = await response.text();
            console.error('Resposta de erro:', textoErro);
            throw new Error(`Erro ${response.status}: ${textoErro.substring(0, 100)}`);
        }
        
        const data = await response.json();
        
        if (data.sucesso) {
            if (!data.elementos || data.elementos.length === 0) {
                mostrarToast('⚠️ O mapa salvo está vazio!', 'warning');
                document.getElementById('statusMapeamento').innerHTML = '⚠️ Mapa vazio! Nenhum elemento encontrado.';
                document.getElementById('statusMapeamento').style.color = '#d29922';
                document.getElementById('confirmModal').style.display = 'none';
                return;
            }
            
            dadosMapeados = data.elementos;
            elementosCompletos = dadosMapeados;
            totalElementos = data.total;
            
            document.getElementById('statusMapeamento').innerHTML = '✅ Mapa carregado do banco! ' + data.total + ' elementos';
            document.getElementById('statusMapeamento').style.color = '#3fb950';
            
            mostrarResultados(dadosMapeados);
            mostrarToast('📂 Mapa carregado com sucesso!', 'success');
            
            document.getElementById('areaCarregarMapa').style.display = 'none';
            document.getElementById('confirmModal').style.display = 'none';

            alternarBotao(false);
            
        } else {
            mostrarToast('❌ ' + (data.erro || 'Erro ao carregar mapa'), 'error');
        }
    } catch (error) {
        console.error('Erro detalhado:', error);
        mostrarToast('❌ Erro ao carregar mapa: ' + error.message, 'error');
    }
}

function mapearNovo() {
    document.getElementById('areaCarregarMapa').style.display = 'none';
    document.getElementById('confirmModal').style.display = 'none';
    mapear();
}

// ============================================
// CONTROLE DO BOTÃO PRINCIPAL E REINICIAR
// ============================================
function alternarBotao(paraMap) {
    const btn = document.getElementById('btnPrincipal');
    const areaReiniciar = document.getElementById('areaReiniciar');
    const urlInput = document.getElementById('urlInput');
    
    if (!btn) return;
    
    if (paraMap) {
        btn.innerHTML = '🚀 Map';
        btn.onclick = function() { mapear(); };
        btn.style.display = 'inline-block';
        btn.disabled = false;
        
        if (areaReiniciar) {
            areaReiniciar.style.display = 'none';
        }
        
        if (urlInput) {
            urlInput.disabled = false;
            urlInput.style.opacity = '1';
        }
        
    } else {
        btn.style.display = 'none';
        btn.disabled = true;
        
        if (areaReiniciar) {
            areaReiniciar.style.display = 'block';
        }
        
        if (urlInput) {
            urlInput.disabled = true;
            urlInput.style.opacity = '0.6';
        }
    }
}

// ============================================
// FUNÇÃO DE REINICIAR O SISTEMA
// ============================================
function reiniciarSistema() {
    if (!confirm('🔄 Tem certeza que quer reiniciar? Os dados atuais serão perdidos!')) {
        return;
    }
    
    mostrarToast('🔄 Reiniciando sistema...', 'info');
    
    fetch('/reiniciar_sistema', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarToast('✅ Sistema reiniciado!', 'success');
            setTimeout(function() {
                location.reload();
            }, 1000);
        } else {
            mostrarToast('❌ Erro ao reiniciar: ' + data.erro, 'error');
        }
    })
    .catch(error => {
        mostrarToast('❌ Erro ao reiniciar: ' + error.message, 'error');
    });
}

function testarBotao() {
    const btn = document.getElementById('btnTesteLado');
    
    if (btn) {
        btn.style.background = 'linear-gradient(135deg, #f0883e, #f0a83e)';
        btn.textContent = '⏳ REINICIANDO...';
        btn.disabled = true;
    }
    
    mostrarToast('🔄 Reiniciando sistema...', 'info');
    
    fetch('/reiniciar_sistema', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarToast('✅ Sistema reiniciado!', 'success');
            setTimeout(function() {
                location.reload();
            }, 1000);
        } else {
            mostrarToast('❌ Erro ao reiniciar: ' + data.erro, 'error');
            if (btn) {
                btn.style.background = 'linear-gradient(135deg, #b91696, #f0883e)';
                btn.textContent = '🧪 TESTE';
                btn.disabled = false;
            }
        }
    })
    .catch(error => {
        mostrarToast('❌ Erro ao reiniciar: ' + error.message, 'error');
        if (btn) {
            btn.style.background = 'linear-gradient(135deg, #b91696, #f0883e)';
            btn.textContent = '🧪 TESTE';
            btn.disabled = false;
        }
    });
}

window.testarBotao = testarBotao;

// ============================================
// ⭐ FUNÇÃO PARA MAPEAR COM ESTRATÉGIAS ⭐
// ============================================
function mapearComEstrategias() {
    const url = document.getElementById('urlInput').value.trim();
    
    if (!url) {
        mostrarToast('❌ Digite uma URL!', 'error');
        return;
    }
    
    document.getElementById('confirmModal').style.display = 'none';
    
    mostrarToast('🧠 Testando estratégias anti-bot...', 'info');
    
    const status = document.getElementById('statusMapeamento');
    status.innerHTML = '🧠 Testando estratégias... Aguarde!';
    status.style.color = '#d29922';
    
    const btn = document.getElementById('btnPrincipal');
    btn.innerHTML = '⏳ Mapeando com estratégias...';
    btn.disabled = true;
    
    fetch('/mapear_com_estrategias', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            status.innerHTML = '✅ ' + data.mensagem;
            status.style.color = '#3fb950';
            mostrarToast('✅ ' + data.mensagem, 'success');
            
            // ⭐⭐⭐ RECARREGA A PÁGINA PARA MOSTRAR OS DADOS ⭐⭐⭐
            // O servidor salvou no cache, a página vai carregar com os dados
            setTimeout(() => location.reload(), 1500);
            
            btn.innerHTML = '🚀 Map';
            btn.disabled = false;
            
        } else {
            status.innerHTML = '❌ ' + data.erro;
            status.style.color = '#f85149';
            mostrarToast('❌ ' + data.erro, 'error');
            btn.innerHTML = '🚀 Map';
            btn.disabled = false;
        }
    })
    .catch(error => {
        status.innerHTML = '❌ Erro: ' + error.message;
        status.style.color = '#f85149';
        mostrarToast('❌ Erro: ' + error.message, 'error');
        btn.innerHTML = '🚀 Map';
        btn.disabled = false;
    });
}
// ============================================
// FILTRO E BUSCA
// ============================================
function filtrarElementos() {
    const input = document.getElementById('searchInput');
    if (!input) return;
    
    const termo = input.value.toLowerCase().trim();
    const status = document.getElementById('searchStatus');
    const btnClear = document.getElementById('btnClear');

    if (termo.length > 0) {
        if (btnClear) btnClear.style.display = 'inline-block';
    } else {
        if (btnClear) btnClear.style.display = 'none';
    }

    if (termo === '') {
        mostrarResultados(elementosCompletos);
        if (status) {
            status.innerHTML = '📌 ' + elementosCompletos.length + ' elementos no total';
            status.style.color = '#8b949e';
        }
        return;
    }

    const filtrados = elementosCompletos.filter(function(elem) {
        const campos = [
            elem.tag || '',
            elem.classe || '',
            elem.id || '',
            elem.texto || '',
            elem.link || '',
            elem.seletor_css || '',
            elem.xpath || ''
        ];
        const textoCompleto = campos.join(' ').toLowerCase();
        return textoCompleto.includes(termo);
    });

    if (filtrados.length > 0) {
        mostrarResultados(filtrados);
        if (status) {
            status.innerHTML = '🔍 ' + filtrados.length + ' elementos encontrados para "' + termo + '"';
            status.style.color = '#3fb950';
        }
    } else {
        const lista = document.getElementById('resultadosLista');
        if (lista) {
            lista.innerHTML = `
                <div class="sem-resultados">
                    <span class="sem-icon">🔍</span>
                    <p>Nenhum elemento encontrado para <strong>"${termo}"</strong></p>
                    <p class="sem-dica">Tente buscar por: tag (div), classe (.header), ID (#menu) ou texto ("dólar")</p>
                </div>
            `;
        }
        if (status) {
            status.innerHTML = '❌ Nenhum resultado para "' + termo + '"';
            status.style.color = '#f85149';
        }
    }
}

function limparBusca() {
    const input = document.getElementById('searchInput');
    if (input) {
        input.value = '';
    }
    const btnClear = document.getElementById('btnClear');
    if (btnClear) btnClear.style.display = 'none';
    filtrarElementos();
}

// ============================================
// RESULTADOS
// ============================================
function mostrarResultados(elementos) {
    if (elementos && elementos.length > 0 && 
        (elementos === dadosMapeados || elementos.length === dadosMapeados.length)) {
        elementosCompletos = elementos;
    }

    const estadoInicial = document.getElementById('estadoInicial');
    const lista = document.getElementById('resultadosLista');
    
    if (!elementos || elementos.length === 0) {
        if (estadoInicial) estadoInicial.style.display = 'flex';
        if (lista) lista.style.display = 'none';
        return;
    }
    
    if (estadoInicial) estadoInicial.style.display = 'none';
    if (lista) lista.style.display = 'block';
    
    const container = document.getElementById('resultadosContainer');
    let html = '<div class="lista-header">📌 ' + elementos.length + ' elementos</div><ul class="lista-elementos">';
    
    for (let i = 0; i < elementos.length; i++) {
        const elem = elementos[i];
        const texto = elem.texto ? elem.texto.slice(0, 60) : 'sem texto';
        const idx = elementosCompletos.indexOf(elem);
        const indexReal = idx >= 0 ? idx : 0;
        
        let classeDisplay = '';
        if (elem.classe && typeof elem.classe === 'string' && elem.classe.length > 0) {
            classeDisplay = '<span class="classe">.' + elem.classe.slice(0, 20) + '</span>';
        }
        
        html += `
            <li onclick="mostrarModal(${indexReal})">
                <span class="tag">${elem.tag || '?'}</span>
                ${classeDisplay}
                ${elem.id ? '<span class="id">#' + elem.id + '</span>' : ''}
                <span class="texto">"' + texto + '"</span>
                <span class="badge">🔍</span>
            </li>
        `;
    }
    html += '</ul>';
    
    container.innerHTML = `
        <div id="estadoInicial" class="estado-inicial" style="display:none;">
            <img src="/static/gif2.gif" alt="Mapeie um site" class="gif-placeholder">
            <h3>https://github.com/alcitech7-oss</h3>
            <p>Digite a URL acima e clique em <strong>"Map"</strong></p>
        </div>
        <div id="resultadosLista">${html}</div>
    `;
}

function mostrarModal(index) {
    const elemento = ultimosResultados[index] || dadosMapeados[index] || elementosCompletos[index];
    if (!elemento) return;

    const body = document.getElementById('modalBody');
    let html = `
        <div class="detalhe-item"><label>Tag</label><code>${elemento.tag || 'N/A'}</code></div>
        <div class="detalhe-item"><label>Classe</label><code>${typeof elemento.classe === 'string' ? elemento.classe : '(nenhuma)'}</code></div>
        <div class="detalhe-item"><label>ID</label><code>${elemento.id || '(nenhum)'}</code></div>
        <div class="detalhe-item">
            <label>Seletor CSS</label>
            <code>${elemento.seletor_css || 'N/A'}</code>
            <button class="btn-copiar" onclick="copiarSeletor('${elemento.seletor_css}', 'CSS')">📋 Copiar</button>
        </div>
        <div class="detalhe-item">
            <label>XPath</label>
            <code>${elemento.xpath || 'N/A'}</code>
            <button class="btn-copiar" onclick="copiarSeletor('${elemento.xpath}', 'XPath')">📋 Copiar</button>
        </div>
        <div class="detalhe-item">
            <label>Código Playwright</label>
            <code>${gerarCodigoPlaywright(elemento)}</code>
            <button class="btn-copiar" onclick="copiarSeletor('${gerarCodigoPlaywright(elemento)}', 'Playwright')">📋 Copiar</button>
        </div>
    `;
    if (elemento.texto) html += '<div class="detalhe-item"><label>Texto</label><code>' + elemento.texto + '</code></div>';
    if (elemento.link) html += '<div class="detalhe-item"><label>Link</label><code>' + elemento.link + '</code></div>';

    body.innerHTML = html;
    document.getElementById('elementoModal').style.display = 'flex';
}

function fecharModal() {
    document.getElementById('elementoModal').style.display = 'none';
}

// ============================================
// EXPORTAÇÃO
// ============================================
async function exportar(formato) {
    try {
        const response = await fetch('/exportar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ formato: formato })
        });

        if (!response.ok) {
            const erro = await response.json();
            throw new Error(erro.erro || 'Erro ao exportar');
        }

        const blob = await response.blob();

        if ('showSaveFilePicker' in window) {
            try {
                const extensoes = { 'excel': '.xlsx', 'json': '.json', 'csv': '.csv' };
                const handle = await window.showSaveFilePicker({
                    suggestedName: 'mapa_' + Date.now() + extensoes[formato],
                    types: [{
                        description: formato.toUpperCase() + ' file',
                        accept: { 'application/octet-stream': [extensoes[formato]] }
                    }]
                });

                const writable = await handle.createWritable();
                await writable.write(blob);
                await writable.close();

                mostrarToast('✅ ' + formato.toUpperCase() + ' salvo com sucesso!', 'success');
                return;
            } catch (err) {
                if (err.name === 'AbortError' || err.name === 'SecurityError') {
                    mostrarToast('⏹️ Salvamento cancelado', 'info');
                    return;
                }
                console.warn('Fallback para download automático:', err);
            }
        }

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'mapa_' + Date.now() + '.' + (formato === 'excel' ? 'xlsx' : formato);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        mostrarToast('📥 ' + formato.toUpperCase() + ' baixado!', 'success');

    } catch (error) {
        mostrarToast('❌ Erro: ' + error.message, 'error');
        console.error(error);
    }
}

// ============================================
// FUNÇÕES DO BANCO DE DADOS
// ============================================
function mostrarBancoResultados(html, cor) {
    var container = document.getElementById('bancoResultados');
    var conteudo = document.getElementById('bancoConteudo');
    if (!container || !conteudo) return;
    container.style.display = 'block';
    if (cor) {
        container.style.borderColor = cor;
    }
    conteudo.innerHTML = html;
}

async function salvarMapa() {
    if (!dadosMapeados || dadosMapeados.length === 0) {
        mostrarToast('❌ Mapeie um site primeiro!', 'error');
        return;
    }
    
    mostrarToast('💾 Salvando mapa no banco...', 'info');
    
    try {
        var response = await fetch('/salvar_mapa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ descricao: 'Mapa salvo manualmente' })
        });
        
        var data = await response.json();
        
        if (data.sucesso) {
            mostrarBancoResultados(`
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 28px;">✅</span>
                    <div>
                        <strong style="color: #3fb950;">Mapa salvo com sucesso!</strong>
                        <p style="color: #8b949e; margin: 4px 0 0 0; font-size: 13px;">
                            ID: ${data.id} | ${data.total} elementos salvos
                        </p>
                    </div>
                </div>
            `, '#3fb950');
            mostrarToast('✅ Mapa salvo com sucesso!', 'success');
        } else {
            mostrarToast('❌ ' + data.erro, 'error');
        }
    } catch (error) {
        mostrarToast('❌ Erro ao salvar: ' + error.message, 'error');
    }
}

async function listarMapas() {
    try {
        var response = await fetch('/listar_mapas', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        var data = await response.json();
        
        if (data.mapas && data.mapas.length > 0) {
            var html = `
                <div style="margin-bottom: 12px;">
                    <strong style="color: #e6edf3;">📋 Histórico de Mapas (${data.total})</strong>
                </div>
                <div style="max-height: 300px; overflow-y: auto;">
            `;
            
            for (var i = 0; i < data.mapas.length; i++) {
                var m = data.mapas[i];
                html += `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0d1117; border-radius: 6px; margin-bottom: 4px; border-left: 3px solid #58a6ff;">
                        <div>
                            <span style="color: #e6edf3; font-weight: 600;">#${m.id}</span>
                            <span style="color: #8b949e; font-size: 13px; margin-left: 10px;">${m.url}</span>
                        </div>
                        <div>
                            <span style="color: #58a6ff; font-size: 13px;">${m.total_elementos} elementos</span>
                            <span style="color: #8b949e; font-size: 12px; margin-left: 10px;">${m.data_mapeamento}</span>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            mostrarBancoResultados(html, '#58a6ff');
        } else {
            mostrarBancoResultados(`
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 28px;">📭</span>
                    <div>
                        <strong style="color: #8b949e;">Nenhum mapa salvo ainda</strong>
                        <p style="color: #8b949e; margin: 4px 0 0 0; font-size: 13px;">
                            Mapeie um site e clique em "Salvar no Banco" para começar.
                        </p>
                    </div>
                </div>
            `, '#8b949e');
        }
    } catch (error) {
        mostrarToast('❌ Erro ao listar: ' + error.message, 'error');
    }
}

// ============================================
// COMPARAÇÃO MANUAL
// ============================================
function abrirCompararManualModal() {
    document.getElementById('compararManualModal').style.display = 'flex';
    document.getElementById('compManualResultado').style.display = 'none';
    document.getElementById('btnCompararManual').disabled = true;
    mapasSelecionados = [];
    mapasDisponiveis = [];
    
    const urlAtual = document.getElementById('urlInput').value.trim();
    if (urlAtual) {
        document.getElementById('compManualUrl').value = urlAtual;
        buscarMapasParaComparar();
    }
}

function fecharCompararManualModal() {
    document.getElementById('compararManualModal').style.display = 'none';
}

async function buscarMapasParaComparar() {
    const url = document.getElementById('compManualUrl').value.trim();
    if (!url) {
        mostrarToast('❌ Digite uma URL!', 'error');
        return;
    }
    
    mostrarToast('📂 Buscando mapas...', 'info');
    
    try {
        const response = await fetch('/listar_mapas?url=' + encodeURIComponent(url));
        const data = await response.json();
        
        const lista = document.getElementById('compManualLista');
        mapasDisponiveis = data.mapas || [];
        
        if (mapasDisponiveis.length === 0) {
            lista.innerHTML = `<p style="color: #8b949e; text-align: center; padding: 20px 0;">📭 Nenhum mapa encontrado para esta URL</p>`;
            return;
        }
        
        let html = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; padding: 4px 8px;">
                <span style="color: #8b949e; font-size: 13px; font-weight: 600;">${mapasDisponiveis.length} mapas encontrados</span>
                <span style="color: #8b949e; font-size: 13px;">${mapasSelecionados.length} selecionados</span>
            </div>
        `;
        
        mapasDisponiveis.forEach(function(mapa, index) {
            const selecionado = mapasSelecionados.some(m => m.id === mapa.id);
            html += `
                <div onclick="toggleSelecaoMapa(${index})" style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: ${selecionado ? '#1c2333' : '#0d1117'}; border-radius: 4px; margin-bottom: 2px; cursor: pointer; border-left: 3px solid ${selecionado ? '#3fb950' : '#30363d'};">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="color: ${selecionado ? '#3fb950' : '#8b949e'}; font-size: 18px;">${selecionado ? '☑️' : '☐'}</span>
                        <span style="color: #e6edf3; font-size: 13px;">${mapa.data_mapeamento}</span>
                    </div>
                    <span style="color: #8b949e; font-size: 13px;">${mapa.total_elementos} elementos</span>
                </div>
            `;
        });
        
        lista.innerHTML = html;
        atualizarBotaoCompararManual();
        
    } catch (error) {
        mostrarToast('❌ Erro ao buscar mapas: ' + error.message, 'error');
    }
}

function toggleSelecaoMapa(index) {
    const mapa = mapasDisponiveis[index];
    const idx = mapasSelecionados.findIndex(m => m.id === mapa.id);
    
    if (idx === -1) {
        mapasSelecionados.push(mapa);
    } else {
        mapasSelecionados.splice(idx, 1);
    }
    
    buscarMapasParaComparar();
}

function atualizarBotaoCompararManual() {
    const btn = document.getElementById('btnCompararManual');
    if (mapasSelecionados.length >= 2) {
        btn.disabled = false;
        btn.innerHTML = '🔍 COMPARAR ' + mapasSelecionados.length + ' MAPAS';
        btn.style.opacity = '1';
    } else {
        btn.disabled = true;
        btn.innerHTML = '🔍 COMPARAR (selecione pelo menos 2)';
        btn.style.opacity = '0.6';
    }
}

async function executarComparacaoManual() {
    if (mapasSelecionados.length < 2) {
        mostrarToast('❌ Selecione pelo menos 2 mapas!', 'error');
        return;
    }
    
    mostrarToast('📊 Carregando mapas selecionados...', 'info');
    
    try {
        const mapasCarregados = [];
        for (const mapaInfo of mapasSelecionados) {
            const response = await fetch('/carregar_mapa_por_id?id=' + mapaInfo.id);
            const data = await response.json();
            if (data.sucesso) {
                mapasCarregados.push({
                    id: mapaInfo.id,
                    data: mapaInfo.data_mapeamento,
                    elementos: data.elementos,
                    total: data.total
                });
            }
        }
        
        if (mapasCarregados.length < 2) {
            mostrarToast('❌ Não foi possível carregar os mapas', 'error');
            return;
        }
        
        const resultado = compararMultiplosMapas(mapasCarregados);
        
        const resultadoDiv = document.getElementById('compManualResultado');
        const conteudo = document.getElementById('compManualResultadoConteudo');
        resultadoDiv.style.display = 'block';
        
        let html = `
            <div style="margin-bottom: 10px;">
                <strong style="color: #e6edf3;">📊 Comparando ${mapasCarregados.length} mapas</strong>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 10px;">
                <div style="background: #0d1117; padding: 8px; border-radius: 6px; text-align: center;">
                    <span style="color: #3fb950; font-size: 18px; font-weight: 700;">${resultado.total_iguais}</span>
                    <p style="color: #8b949e; font-size: 11px; margin: 0;">Iguais</p>
                </div>
                <div style="background: #0d1117; padding: 8px; border-radius: 6px; text-align: center;">
                    <span style="color: #d29922; font-size: 18px; font-weight: 700;">${resultado.total_mudancas}</span>
                    <p style="color: #8b949e; font-size: 11px; margin: 0;">Mudaram</p>
                </div>
                <div style="background: #0d1117; padding: 8px; border-radius: 6px; text-align: center;">
                    <span style="color: #f85149; font-size: 18px; font-weight: 700;">${resultado.total_sumidos}</span>
                    <p style="color: #8b949e; font-size: 11px; margin: 0;">Sumiram</p>
                </div>
                <div style="background: #0d1117; padding: 8px; border-radius: 6px; text-align: center;">
                    <span style="color: #58a6ff; font-size: 18px; font-weight: 700;">${resultado.total_novos}</span>
                    <p style="color: #8b949e; font-size: 11px; margin: 0;">Novos</p>
                </div>
            </div>
            <div style="max-height: 150px; overflow-y: auto; padding: 8px; background: #0d1117; border-radius: 6px;">
                <p style="color: #8b949e; font-size: 12px; margin: 0 0 4px 0;">📋 Mapas analisados:</p>
                ${mapasCarregados.map(function(m) {
                    return `<p style="color: #8b949e; font-size: 12px; margin: 2px 0;">📅 ${m.data} - ${m.total} elementos</p>`;
                }).join('')}
            </div>
        `;
        
        conteudo.innerHTML = html;
        mostrarToast('📊 Comparação concluída!', 'success');
        
    } catch (error) {
        mostrarToast('❌ Erro: ' + error.message, 'error');
    }
}

function compararMultiplosMapas(mapas) {
    if (mapas.length < 2) {
        return { total_iguais: 0, total_mudancas: 0, total_sumidos: 0, total_novos: 0 };
    }
    
    const referencia = mapas[0].elementos;
    const mapaRef = {};
    referencia.forEach(function(elem) {
        mapaRef[elem.posicao] = elem;
    });
    
    const acumulador = {
        iguais: [],
        mudaram: [],
        sumiram: [],
        novos: []
    };
    
    for (let i = 1; i < mapas.length; i++) {
        const mapaAtual = mapas[i].elementos;
        const mapaAtualObj = {};
        mapaAtual.forEach(function(elem) {
            mapaAtualObj[elem.posicao] = elem;
        });
        
        for (const pos in mapaRef) {
            if (pos in mapaAtualObj) {
                const elemRef = mapaRef[pos];
                const elemAtual = mapaAtualObj[pos];
                if (elemRef.seletor_css !== elemAtual.seletor_css || 
                    elemRef.xpath !== elemAtual.xpath || 
                    elemRef.texto !== elemAtual.texto) {
                    if (!acumulador.mudaram.includes(pos)) {
                        acumulador.mudaram.push(pos);
                    }
                } else {
                    if (!acumulador.iguais.includes(pos)) {
                        acumulador.iguais.push(pos);
                    }
                }
            } else {
                if (!acumulador.sumiram.includes(pos)) {
                    acumulador.sumiram.push(pos);
                }
            }
        }
        
        for (const pos in mapaAtualObj) {
            if (!(pos in mapaRef)) {
                if (!acumulador.novos.includes(pos)) {
                    acumulador.novos.push(pos);
                }
            }
        }
    }
    
    acumulador.iguais = [...new Set(acumulador.iguais)];
    acumulador.mudaram = [...new Set(acumulador.mudaram)];
    acumulador.sumiram = [...new Set(acumulador.sumiram)];
    acumulador.novos = [...new Set(acumulador.novos)];
    
    return {
        total_iguais: acumulador.iguais.length,
        total_mudancas: acumulador.mudaram.length,
        total_sumidos: acumulador.sumiram.length,
        total_novos: acumulador.novos.length
    };
}

// ============================================
// INICIALIZAÇÃO
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('urlInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') mapear();
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            fecharModal();
            fecharCompararManualModal();
        }
    });
    
    var modal = document.getElementById('elementoModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) fecharModal();
        });
    }
    
    var confirmModal = document.getElementById('confirmModal');
    if (confirmModal) {
        confirmModal.addEventListener('click', function(e) {
            if (e.target === this) {
                document.getElementById('confirmModal').style.display = 'none';
                mostrarToast('Mapeamento cancelado', 'error');
            }
        });
    }
    
    var compModal = document.getElementById('compararManualModal');
    if (compModal) {
        compModal.addEventListener('click', function(e) {
            if (e.target === this) fecharCompararManualModal();
        });
    }
    
    document.getElementById('urlInput').addEventListener('input', function() {
        mostrarInfoUrl();
    });
    
    mostrarEstadoInicial();
    console.log('✅ Struct Analyzer PRO carregado!');
});

function mostrarEstadoInicial() {
    const container = document.getElementById('resultadosContainer');
    const estadoInicial = document.getElementById('estadoInicial');
    const lista = document.getElementById('resultadosLista');
    
    if (estadoInicial) {
        estadoInicial.style.display = 'flex';
        if (lista) lista.style.display = 'none';
        return;
    }
    
    container.innerHTML = `
        <div id="estadoInicial" class="estado-inicial">
            <img src="/static/gif2.gif" alt="Mapeie um site" class="gif-placeholder">
            <h3>https://github.com/alcitech7-oss</h3>
            <p>Digite a URL acima e clique em <strong>"Map"</strong></p>
        </div>
        <div id="resultadosLista" style="display: none;"></div>
    `;
}

// ============================================
// SISTEMA DE DETECÇÃO DE ERROS
// ============================================
function capturarErros() {
    window.onerror = function(mensagem, url, linha, coluna, erro) {
        console.error('🚨 ERRO CAPTURADO:', mensagem, erro);
        mostrarToast('❌ Erro: ' + mensagem, 'error');
        document.getElementById('statusMapeamento').innerHTML = '❌ Erro: ' + mensagem;
        document.getElementById('statusMapeamento').style.color = '#f85149';
        return true;
    };

    window.addEventListener('unhandledrejection', function(event) {
        console.error('🚨 PROMESSA REJEITADA:', event.reason);
        mostrarToast('❌ Erro: ' + event.reason, 'error');
        document.getElementById('statusMapeamento').innerHTML = '❌ Erro: ' + event.reason;
        document.getElementById('statusMapeamento').style.color = '#f85149';
    });

    const fetchOriginal = window.fetch;
    window.fetch = function(...args) {
        return fetchOriginal.apply(this, args).catch(function(erro) {
            console.error('🚨 ERRO NO FETCH:', erro);
            mostrarToast('❌ Erro na requisição: ' + erro.message, 'error');
            document.getElementById('statusMapeamento').innerHTML = '❌ Erro: ' + erro.message;
            document.getElementById('statusMapeamento').style.color = '#f85149';
            throw erro;
        });
    };

    console.log('✅ Sistema de detecção de erros ativado!');
}

function testarErro() {
    try {
        throw new Error('🧪 Erro de teste forçado!');
    } catch (erro) {
        console.error('🧪 Teste de erro:', erro);
        mostrarToast('🧪 Teste: ' + erro.message, 'error');
        document.getElementById('statusMapeamento').innerHTML = '🧪 Teste: ' + erro.message;
        document.getElementById('statusMapeamento').style.color = '#f85149';
    }
}

function gerarCodigoPlaywright(elemento) {
    if (!elemento) return '// Elemento não encontrado';
    const seletor = elemento.seletor_css || elemento.xpath || '';
    return `await page.locator('${seletor}').click();`;
}

function copiarSeletor(texto, tipo) {
    if (!texto || texto === 'N/A') {
        mostrarToast('❌ Nada para copiar', 'error');
        return;
    }
    navigator.clipboard.writeText(texto).then(() => {
        mostrarToast(`✅ ${tipo} copiado!`, 'success');
    }).catch(() => {
        mostrarToast('❌ Erro ao copiar', 'error');
    });
}
// ⭐ FUNÇÃO PARA VERIFICAR MODO ANÔNIMO ⭐
function verificarModo() {
    fetch('/verificar_modo')
        .then(response => response.json())
        .then(data => {
            if (data.anonimo) {
                mostrarAvisoAnonimo();
            }
        })
        .catch(error => console.error('Erro ao verificar modo:', error));
}

// ⭐ FUNÇÃO PARA MOSTRAR AVISO DE MODO ANÔNIMO ⭐
function mostrarAvisoAnonimo() {
    const aviso = document.createElement('div');
    aviso.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 99999;
        background: #0d1117;
        border: 2px solid #f0883e;
        border-radius: 16px;
        padding: 30px 40px;
        max-width: 500px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.8);
        text-align: center;
        animation: fadeIn 0.5s ease;
    `;
    
    aviso.innerHTML = `
        <div style="font-size: 48px; margin-bottom: 12px;">⚠️</div>
        <h2 style="color: #f0883e; margin-bottom: 12px;">MODO ANÔNIMO DETECTADO!</h2>
        <p style="color: #8b949e; font-size: 14px; line-height: 1.6;">
            O sistema está rodando em <strong style="color: #f0883e;">modo anônimo</strong>.
            <br><br>
            A eficácia do mapeamento pode ser <strong style="color: #f85149;">REDUZIDA em até 70%</strong>!
        </p>
        <div style="background: #161b22; padding: 12px; border-radius: 8px; margin: 12px 0; text-align: left;">
            <p style="color: #8b949e; font-size: 13px; margin: 4px 0;">
                💡 <strong style="color: #58a6ff;">Para melhor eficiência:</strong>
            </p>
            <p style="color: #8b949e; font-size: 13px; margin: 4px 0;">
                1. Faça login no Chrome
            </p>
            <p style="color: #8b949e; font-size: 13px; margin: 4px 0;">
                2. Feche todas as janelas do Chrome
            </p>
            <p style="color: #8b949e; font-size: 13px; margin: 4px 0;">
                3. Execute a ferramenta novamente
            </p>
        </div>
        <div style="display: flex; gap: 10px; justify-content: center; margin-top: 16px;">
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: linear-gradient(135deg, #238636, #2ea043);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                cursor: pointer;
            ">
                ✅ Entendi
            </button>
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: #21262d;
                color: #8b949e;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                cursor: pointer;
            ">
                ❌ Ignorar
            </button>
        </div>
    `;
    
    document.body.appendChild(aviso);
}

// ⭐ CHAMA A VERIFICAÇÃO QUANDO O SISTEMA CARREGA ⭐
document.addEventListener('DOMContentLoaded', function() {
    // ... código existente ...
    verificarModo(); // ⭐ NOVO
});