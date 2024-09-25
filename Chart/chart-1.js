const ctx = document.getElementById('chart-1').getContext('2d');
const chart_1 = new Chart(ctx, 
    {
        type:'line',
        data :{
            // give the x values here
            labels :["jan", "Feb", "Mar", "Apr", "May", "June"],
            datasets:[
                { 
                    //give the y values here
                    label : 'Sales',
                    data:[10,9,8,12,13,6,5],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth : 5
                }
            ]
        },
        options:{
            responsive : true,
            scales:{
                x:{
                    title : {
                        display: true,
                        text : "Month"
                    }
                },
                y:{
                    beginAtZero: true,
                    title: {
                        display : true,
                        text: "Sales in penny"
                    }
                }
            }
        }
    }
)

