function copyToClipboard(elementId) {
    const copyText = document.getElementById(elementId);
    copyText.select();
    document.execCommand("copy");
    alert("Адрес скопирован: " + copyText.value);
}

async function loadTokenInfo() {
    if (typeof window.ethereum !== 'undefined') {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            const web3 = new Web3(window.ethereum);
            const balance = await web3.eth.getBalance(accounts[0]);
            const balanceEth = web3.utils.fromWei(balance, 'ether');

            document.getElementById('tokenInfo').innerHTML = `
                        <p><strong>Баланс ETH:</strong> ${parseFloat(balanceEth).toFixed(4)}</p>
                        <p class="text-muted">Другие токены будут отображаться здесь</p>
                    `;
        } catch (error) {
            console.error("Ошибка при загрузке информации:", error);
            document.getElementById('tokenInfo').innerHTML = `
                        <p class="text-danger">Ошибка при загрузке данных</p>
                    `;
        }
    } else {
        document.getElementById('tokenInfo').innerHTML = `
                    <p class="text-warning">MetaMask не обнаружен</p>
                `;
    }
}

window.addEventListener('load', () => {
    if (typeof window.ethereum !== 'undefined') {
        loadTokenInfo();
    }
});