document.getElementById('start-conversation').addEventListener('click', function() {
    const loadingDiv = document.getElementById('loading');
    loadingDiv.style.display = 'block';

    fetch('/start_conversation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ topic: "Default Topic", message_count: 5 })
    })
    .then(response => response.json())
    .then(data => {
        loadingDiv.style.display = 'none';

        const conversationDiv = document.getElementById('conversation');
        conversationDiv.innerHTML = ''; // Clear previous content

        data.conversation.forEach((msg, index) => {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message');
            messageElement.classList.add(index % 2 === 0 ? 'assistant-1' : 'assistant-2');

            const icon = document.createElement('img');
            icon.classList.add('assistant-icon');
            icon.src = index % 2 === 0 ? '/static/master_chief_icon.png' : '/static/cortana_icon.png';
            messageElement.appendChild(icon);

            const textElement = document.createElement('span');
            textElement.textContent = msg;
            messageElement.appendChild(textElement);

            conversationDiv.appendChild(messageElement);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        loadingDiv.style.display = 'none';
    });
});
