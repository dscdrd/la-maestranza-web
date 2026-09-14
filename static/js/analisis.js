document.addEventListener("DOMContentLoaded", function () {

    cargarGraficoDemanda();
    cargarGraficoOcupacion();

});


async function cargarGraficoDemanda() {

    try {

        const respuesta =
            await fetch("/api/estadisticas/demanda-talleres");

        if (!respuesta.ok) {

            throw new Error(
                "No se pudieron obtener los datos"
            );

        }

        const datos = await respuesta.json();

        const talleres = datos.ranking_demanda;


        const nombres = talleres.map(
            taller => taller.taller
        );


        const reservas = talleres.map(
            taller => taller.reservas_activas
        );


        const canvas =
            document.getElementById("graficoDemanda");


        new Chart(canvas, {

            type: "bar",

            data: {

                labels: nombres,

                datasets: [

                    {
                        label: "Reservas activas",

                        data: reservas,

                        backgroundColor: "#8f0d0d",

                        borderColor: "#6f0909",

                        borderWidth: 1,

                        borderRadius: 5
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        },

                        title: {
                            display: true,
                            text: "Reservas"
                        }

                    },


                    x: {

                        ticks: {

                            autoSkip: false,

                            maxRotation: 45,

                            minRotation: 45

                        }

                    }

                }

            }

        });


    } catch (error) {

        console.error(
            "Error al cargar el gráfico:",
            error
        );

    }

}

async function cargarGraficoOcupacion() {

    try {

        const respuesta =
            await fetch("/api/estadisticas/ocupacion-talleres");

        if (!respuesta.ok) {

            throw new Error(
                "No se pudieron obtener los datos de ocupación"
            );

        }

        const datos = await respuesta.json();

        const talleres = datos.talleres;


        const nombres = talleres.map(
            taller => taller.taller
        );


        const ocupacion = talleres.map(
            taller => taller.porcentaje_ocupacion
        );


        const canvas =
            document.getElementById("graficoOcupacion");


        new Chart(canvas, {

            type: "bar",

            data: {

                labels: nombres,

                datasets: [

                    {
                        label: "Ocupación (%)",

                        data: ocupacion,

                        backgroundColor: "#8f0d0d",

                        borderColor: "#6f0909",

                        borderWidth: 1,

                        borderRadius: 5
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 100,

                        ticks: {

                            callback: function (valor) {
                                return valor + "%";
                            }

                        },

                        title: {
                            display: true,
                            text: "Ocupación (%)"
                        }

                    },

                    x: {

                        ticks: {

                            autoSkip: false,

                            maxRotation: 45,

                            minRotation: 45

                        }

                    }

                }

            }

        });


    } catch (error) {

        console.error(
            "Error al cargar el gráfico de ocupación:",
            error
        );

    }

}