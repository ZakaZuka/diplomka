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

            // Изменено на GET запрос для nonce
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
        // Изменено на GET с параметром в URL
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
        const response = await fetch('/users/login/', {
            method: 'POST',
            credentials: 'include',  // Важно: отправляем куки
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address: walletAddress, signature })
        });

        const data = await response.json();
        console.log('Login response:', data);  // Отладочный вывод

        if (data.success) {
            // Перенаправляем после успешного сохранения куки
            window.location.href = data.redirect || '/users/profile/';
        } else {
            throw new Error(data.error || 'Auth failed');
        }
    },

    _getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
};