async function connectMetaMask() {
    if (typeof window.ethereum === 'undefined') {
        alert("Установите MetaMask!");
        return;
    }

    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
    const address = accounts[0];

    const response = await fetch('/users/nonce/?address=' + address);
    const { nonce } = await response.json();

    const msg = `Авторизация: ${nonce}`;
    const from = address;
    const sign = await ethereum.request({
        method: "personal_sign",
        params: [msg, from],
    });

    const loginRes = await fetch('/users/profile/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ address, signature: sign }),
    });

    if (loginRes.ok) {
        location.reload();
    } else {
        alert("Ошибка входа");
    }
}

// Вспомогательная функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let c of cookies) {
            const cookie = c.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
