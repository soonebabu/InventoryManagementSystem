// chart.js

document.addEventListener("DOMContentLoaded", function() {
    console.log("Rendering dayWiseChart for MOCIT");
    console.log("day_wise_data:", dayWiseData);
    console.log("monthly_data:", monthlyData);

    // Include your Chart.js code here for dayWiseChart
    var dayWiseData = dayWiseData;  // Replace with the actual data variable
    createDayWiseChart(dayWiseData);
});

function createDayWiseChart(dayWiseData) {
    // Your Chart.js code for dayWiseChart
    var ctx = document.getElementById('dayWiseChart').getContext('2d');
    var dayWiseChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dayWiseData.map(item => moment(item.date).format('YYYY-MM-DD')),
            datasets: [{
                label: 'Items Assigned Day Wise',
                data: dayWiseData.map(item => item.count),
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        displayFormats: {
                            day: 'YYYY-MM-DD'
                        }
                    }
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
