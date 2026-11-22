// Funções compartilhadas pelas páginas da interface.

async function api(caminho, opcoes = {}) {
  const resposta = await fetch(caminho, {
    headers: { "Content-Type": "application/json" },
    ...opcoes,
  });

  if (resposta.status === 204) return null;

  const corpo = await resposta.json().catch(() => null);
  if (!resposta.ok) {
    throw new Error(traduzirErro(corpo, resposta.status));
  }
  return corpo;
}

// Converte o "detail" do FastAPI (texto ou lista de erros de validação) em mensagem legível.
function traduzirErro(corpo, status) {
  if (!corpo || !corpo.detail) return `Erro ${status}`;
  if (typeof corpo.detail === "string") return corpo.detail;
  return corpo.detail
    .map((e) => `${e.loc[e.loc.length - 1]}: ${e.msg}`)
    .join("; ");
}

function mostrarMensagem(texto, tipo = "sucesso") {
  const caixa = document.querySelector("[data-testid='mensagem']");
  caixa.textContent = texto;
  caixa.className = `mensagem ${tipo}`;
  caixa.hidden = false;
}

// Mensagem enviada por outra página via ?msg=... (ex.: após cadastrar um produto).
function mostrarMensagemDaUrl() {
  const params = new URLSearchParams(window.location.search);
  const msg = params.get("msg");
  if (msg) mostrarMensagem(msg, "sucesso");
}

function formatarPreco(valor) {
  return Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function marcarLinkAtivo() {
  const atual = window.location.pathname.replace(/index\.html$/, "");
  document.querySelectorAll(".sidebar nav a").forEach((link) => {
    const destino = new URL(link.href).pathname.replace(/index\.html$/, "");
    if (destino === atual) link.classList.add("ativo");
  });
}

document.addEventListener("DOMContentLoaded", marcarLinkAtivo);
