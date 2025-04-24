async function connectMetaMask() {
    if (typeof window.ethereum !== 'undefined') {
        const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
        const address = accounts[0];

        const response = await fetch(`/auth/nonce/${address}/`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Ошибка получения nonce');
        }

        const nonce = data.nonce;
        // Далее подпись и отправка на сервер
    } else {
        alert('MetaMask не установлен!');
    }
}
