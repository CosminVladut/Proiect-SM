const updateUI = (data) => {
    if (data.temp !== undefined) document.getElementById("temp").textContent = data.temp;
    if (data.humidity !== undefined) document.getElementById("humidity").textContent = data.humidity;
    if (data.fire_detected !== undefined) document.getElementById("fire").textContent = data.fire_detected ? "Yes" : "No";
    if (data.intruder_detected !== undefined) document.getElementById("intruder").textContent = data.intruder_detected ? "Yes" : "No";
    if (data.timestamp !== undefined) document.getElementById("timestamp").textContent = new Date(data.timestamp).toLocaleTimeString();
};

setInterval(() => {
    fetch('/status')
        .then(res => res.json())
        .then(updateUI)
        .catch(console.error);
}, 500);

document.getElementById('settings-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {};
    
    data.manual_motor_start = e.target.manual_motor_start.checked;
    for (let [key, value] of formData.entries()) 
    {
        if (key === 'manual_motor_start') continue;  
	if (!isNaN(value)) 
	{
            data[key] = Number(value);
        } 
	else 
	{
            data[key] = value;
        }
    }

    fetch('/set', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(res => res.json()).then(console.log).catch(console.error);
});

