/**********************************************************************************************************************/

let colors = ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(75, 192, 192, 0.2)'];

/**********************************************************************************************************************/

let percentageCanvas = document.getElementById('percentageChart').getContext('2d');

const percentageInventory = new Chart(percentageCanvas, {
    type: 'doughnut',
    data: {
        labels: categories,
        datasets: [{
            label: '%',
            data: percentages,
            backgroundColor: colors,
            borderColor: colors.map(color => color.replace('0.2', '1')),
            borderWidth: 1,
        }],
        options: {
            responsive: true,
            maintainAspectRatio: false,
        }
    }
})
/**********************************************************************************************************************/

let inventoryPerCategoryCanvas = document.getElementById('inventoryChart').getContext('2d');

const inventoryPerCategory = new Chart(inventoryPerCategoryCanvas, {
    type: 'bar',
    data: {
        labels: categories,
        datasets: [{
            label: 'Cantidad por categoría',
            data: quantities,
            backgroundColor: colors,
            borderColor: colors.map(color => color.replace('0.2', '1')),
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

/**********************************************************************************************************************/
let stockVersusCanvas = document.getElementById('stockVersusChart').getContext('2d');

const data = {
    labels: [],
    datasets: [
        {
            label: '',
            data: [],
            borderColor: 'rgba(255, 99, 132, 0.2)',
            backgroundColor: 'rgba(255, 99, 132, 1)',
            yAxisID: 'y',
        },
        {
            label: '',
            data: [],
            borderColor: 'rgba(54, 162, 235, 0.2)',
            backgroundColor: 'rgba(54, 162, 235, 1)',
            yAxisID: 'y',
        }
    ]
};

let stockVersus = new Chart(stockVersusCanvas, {
    type: 'line',
    data: data,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        stacked: false,
        scales: {
            y: {
                type: 'linear',
                display: true,
                position: 'left',
                beginAtZero: true,
            },
            y1: {
                type: 'linear',
                display: false,
                position: 'right',

                // grid line settings
                grid: {
                    drawOnChartArea: false, // only want the grid lines for one axis to show up
                },
            },
        }
    },
})

/**********************************************************************************************************************/

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**********************************************************************************************************************/

function GetStockData(index) {
    let csrftoken = getCookie('csrftoken');
    let month = document.getElementById("monthSelectStock" + index);
    let year = document.getElementById("yearSelectStock" + index);
    $.ajax({
        type: "POST",
        url: getStockMonthURL,
        data: {
            "month": month.options[month.selectedIndex].value,
            "year": year.options[year.selectedIndex].value,
            'csrfmiddlewaretoken': csrftoken,
            "productid": 1,
        },
        success: function (response) {
            //update the current data with the new response
            if (index === 1) {
                stockVersus.data.datasets[0].data = JSON.parse(response.data)
                stockVersus.data.datasets[0].label = month.options[month.selectedIndex].text + " " + year.options[year.selectedIndex].text
            } else {
                stockVersus.data.datasets[1].data = JSON.parse(response.data)
                stockVersus.data.datasets[1].label = month.options[month.selectedIndex].text + " " + year.options[year.selectedIndex].text
            }
            stockVersus.data.labels = response.labels.split(',')
            stockVersus.update();
        },
        error: function (error) {
            console.error('Error al enviar los datos de los productos. Inténtalo de nuevo más tarde.');
        }
    });
}

/**********************************************************************************************************************/

document.addEventListener('DOMContentLoaded', function () {
    let today = new Date();
    let currentMonth = today.getMonth() + 1; // Añadimos 1 porque los meses en JavaScript son base 0
    let currentYear = today.getFullYear();

    // Establecer los valores seleccionados por defecto
    document.getElementById('monthSelectStock1').value = currentMonth;
    document.getElementById('monthSelectStock2').value = currentMonth - 1;
    document.getElementById('yearSelectStock1').value = currentYear;
    document.getElementById('yearSelectStock2').value = currentYear;
    GetStockData(1);
    GetStockData(2);
});

/**********************************************************************************************************************/
