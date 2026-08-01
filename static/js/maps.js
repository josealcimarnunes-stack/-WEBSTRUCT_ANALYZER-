async function abrirModalSeletores() {
    const modal = new bootstrap.Modal(document.getElementById('modalSeletores'));
    modal.show();

    const res = await fetch('/seletores/listar');
    const seletores = await res.json();

    const tbody = document.querySelector('#tabelaSeletoresSalvos tbody');
    tbody.innerHTML = '';

    seletores.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${s.nome}</td>
            <td>${s.url}</td>
            <td><code>${s.seletor}</code></td>
            <td>${s.ultimo_status ? '🟢 Ativo' : '🔴 Quebrado'}</td>
            <td><button class="btn btn-sm btn-primary" onclick="testarSeletor(${s.id}, '${s.url}', '${s.seletor}')">Verificar</button></td>
        `;
        tbody.appendChild(tr);
    });
}

async function testarSeletor(id, url, seletor) {
    const res = await fetch('/seletores/verificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, url, seletor })
    });
    const data = await res.json();
    alert(data.valido ? "🟢 Seletor ativo e encontrado!" : "🔴 Seletor não encontrado.");
    abrirModalSeletores();
}