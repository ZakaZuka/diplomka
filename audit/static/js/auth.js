const MetaMaskAuth = {
    async connect() {
        try {
            if (typeof window.ethereum === 'undefined') {
                throw new Error('MetaMask не установлен!');
            }

            const accounts = await window.ethereum.request({ 
                method: 'eth_requestAccounts' 
            });
            const walletAddress = accounts[0];

            const nonceResponse = await this._fetchNonce(walletAddress);
            const nonce = nonceResponse.nonce;

            const signature = await this._getSignature(nonce, walletAddress);
            const loginResult = await this._login(walletAddress, signature);

            if (loginResult.success) {
                window.location.href = '/users/profile/';
            } else {
                throw new Error('Ошибка авторизации на сервере');
            }
        } catch (error) {
            console.error('MetaMask Auth Error:', error);
            alert(`Ошибка: ${error.message}`);
        }
    },

    async _fetchNonce(walletAddress) {
        const response = await fetch(`/users/nonce/?address=${walletAddress}`);
        if (!response.ok) throw new Error('Ошибка при получении nonce');
        return await response.json();
    },

    async _getSignature(nonce, walletAddress) {
        try {
            return await window.ethereum.request({
                method: 'personal_sign',
                params: [nonce, walletAddress]
            });
        } catch (error) {
            throw new Error('Пользователь отклонил подпись');
        }
    },

    async _login(walletAddress, signature) {
        const csrfToken = this._getCSRFToken();
        const response = await fetch('/users/login/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ 
                address: walletAddress,  // Изменено на address вместо wallet_address
                signature: signature 
            })
        });
        
        if (!response.ok) throw new Error('Ошибка при авторизации');
        return await response.json();
    },

    _getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
};