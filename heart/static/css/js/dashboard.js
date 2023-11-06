/* globals Chart:false, feather:false */

(function () {
  'use strict';

  feather.replace({ 'aria-hidden': 'true' });

  // Function to update the chart data
  function updateChartData() {
    // Make an AJAX request to fetch user and therapist data
    // Replace the URL with the actual endpoint to retrieve the data
    fetch('/get_user_therapist_data')
      .then((response) => response.json())
      .then((data) => {
        // Update the chart with the retrieved data
        const chart = myChart;
        chart.data.datasets[0].data = data.userData;
        chart.data.datasets[1].data = data.therapistData;
        chart.update();
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
      });
  }

  // Create the initial chart with dummy data
  var initialData = {
    userData: [100, 150, 200, 180, 220, 250, 200],
    therapistData: [10, 15, 20, 18, 25, 30, 20],
  };

  var chartData = {
    labels: [
      'Sunday',
      'Monday',
      'Tuesday',
      'Wednesday',
      'Thursday',
      'Friday',
      'Saturday',
    ],
    datasets: [
      {
        label: 'Users',
        data: initialData.userData,
        backgroundColor: 'transparent',
        borderColor: '#007bff',
        borderWidth: 2,
        pointBackgroundColor: '#007bff',
      },
      {
        label: 'Therapists',
        data: initialData.therapistData,
        backgroundColor: 'transparent',
        borderColor: '#28a745',
        borderWidth: 2,
        pointBackgroundColor: '#28a745',
      },
    ],
  };

  var ctx = document.getElementById('userTherapistChart').getContext('2d');

  var myChart = new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
      scales: {
        yAxes: [
          {
            ticks: {
              beginAtZero: true,
            },
          },
        ],
      },
    },
  });

  // Update the chart data with the initial data
  updateChartData();

  // Update the chart data periodically (e.g., every minute)
  setInterval(updateChartData, 60000);
})();



