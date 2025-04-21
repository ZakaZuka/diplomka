function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function connectMetaMask() {
    if (!window.ethereum) {
        alert('Пожалуйста, установите MetaMask!');
        return;
    }

    try {
        const accounts = await window.ethereum.request({ 
            method: 'eth_requestAccounts' 
        });
        const address = accounts[0];
        
        // Получаем nonce с сервера (теперь правильный URL)
        const nonceResponse = await fetch(`/users/auth/nonce/?address=${address}`);
        if (!nonceResponse.ok) {
            throw new Error('Ошибка получения nonce');
        }
        const { nonce } = await nonceResponse.json();
        
        const message = `Аутентификация: ${nonce}`;
        const signature = await window.ethereum.request({
            method: 'personal_sign',
            params: [message, address],
        });

        const authResponse = await fetch('/users/auth/metamask/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ address, signature, message }),
        });

        if (authResponse.ok) {
            window.location.reload();
        } else {
            throw new Error('Ошибка аутентификации');
        }
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// Вешаем обработчик на кнопку
document.getElementById('metamask-login').addEventListener('click', connectMetaMask);