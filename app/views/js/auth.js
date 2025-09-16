// URL base do seu backend Flask
const API_BASE = 'http://127.0.0.1:5000/api';

// Referências da UI já existentes no seu script original
const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

// Alternância de painéis (mantido)
if (signUpButton) {
  signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
  });
}
if (signInButton) {
  signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
  });
}

// --------- Funções que chamam o backend ---------
async function apiRegister(email, password) {
  const resp = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password })
  });
  return resp.json();
}

async function apiLogin(email, password) {
  const resp = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password })
  });
  return resp.json();
}

// --------- Intercepta os submits dos formulários ---------
const formRegister = document.getElementById('formRegister');
if (formRegister) {
  formRegister.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Coleta valores do cadastro
    const email = formRegister.querySelector('input[name="email"]').value.trim();
    const password = formRegister.querySelector('input[name="senha"]').value;

    if (!email || !password) {
      alert('Informe email e senha.');
      return;
    }

    try {
      const result = await apiRegister(email, password);
      if (result && result.message) {
        alert(result.message);
        // Opcional: após cadastrar, ir para o painel de login
        container.classList.remove("right-panel-active");
      } else if (result && result.error) {
        alert(`Erro: ${result.error}`);
      } else {
        alert('Erro inesperado no cadastro.');
      }
    } catch (err) {
      alert('Falha de rede ao cadastrar.');
    }
  });
}

const formLogin = document.getElementById('formLogin');
if (formLogin) {
  formLogin.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Coleta valores do login
    const email = formLogin.querySelector('input[name="email"]').value.trim();
    const password = formLogin.querySelector('input[name="senha"]').value;

    if (!email || !password) {
      alert('Informe email e senha.');
      return;
    }

    try {
      const result = await apiLogin(email, password);
      if (result && result.message) {
        alert(`Bem-vindo: ${result.email || email}`);
        // Ex.: redirecionar após login
        // window.location.href = '/';
      } else if (result && result.error) {
        alert(`Erro: ${result.error}`);
      } else {
        alert('Erro inesperado no login.');
      }
    } catch (err) {
      alert('Falha de rede ao logar.');
    }
  });
}