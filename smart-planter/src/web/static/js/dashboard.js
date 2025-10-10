// チャート初期化
function initializeChart() {
    const ctx = document.getElementById('sensorChart');
    if (!ctx) return;
    
    sensorChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: '温度 (°C)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                },
                {
                    label: '湿度 (%)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.1
                },
                {
                    label: '土壌水分',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

// チャートデータ更新
function updateChart(data) {
    if (!sensorChart) return;
    
    const now = new Date().toLocaleTimeString();
    
    // データを追加
    sensorChart.data.labels.push(now);
    sensorChart.data.datasets[0].data.push(data.temperature);
    sensorChart.data.datasets[1].data.push(data.humidity);
    sensorChart.data.datasets[2].data.push(data.soil_moisture);
    
    // 最大20個のデータポイントを保持
    if (sensorChart.data.labels.length > 20) {
        sensorChart.data.labels.shift();
        sensorChart.data.datasets.forEach(dataset => {
            dataset.data.shift();
        });
    }
    
    sensorChart.update();
}

// ダッシュボード初期化
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();
    
    // チャート更新をメインのデータ更新に統合
    const originalUpdateSensorDisplay = window.updateSensorDisplay;
    window.updateSensorDisplay = function(data) {
        originalUpdateSensorDisplay(data);
        updateChart(data);
    };
});