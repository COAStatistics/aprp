var chart1Helper = {
    container: null,
    manager: {
        getCharts: function(){
            return chart2Helper.manager.charts;
        },
        charts: null,
        dateRange: {
            min: null,
            max: null,
        },
        fontSize: {
            label: 11,
            title: 11,
        },
        title: gettext('Daily Price/Volume Trend For Two Weeks'),
    },
    init: function(container){
        this.container = $('#' + container);

        if(this.container.length == 0)
            root.console.log('Cannot find container #' + container);

        this.manager.charts = [];

        this.manager.dateRange.min = Date.today().add(-6).days();
        this.manager.dateRange.max = Date.today();

        if(thisDevice == 'desktop'){
            this.manager.fontSize.label = 14;
            this.manager.fontSize.title = 18;
        }

    },
    create: function(container, seriesOptions, unit){

        var series = [];
        var yAxis = [];
        var has_avg_price = false;
        var has_sum_volume = false;
        var has_avg_weight = false;


        seriesOptions.forEach(function(option, i) {

            type = option.type;
            data = option.highchart;

            if ('avg_price' in data) {
                if (data['avg_price'].length > 0) {
                    has_avg_price = true;
                    series.push({
                        type: 'line',
                        name: type.name + gettext('Average Price'),
                        yAxis: 0,
                        color: Highcharts.getOptions().colors[1],
                        data: data['avg_price'],
                        zIndex: 100,
                        marker: {
                            enabled: true,
                            radius: 3
                        },
                        tooltip: {
                            valueDecimals: 2,
                            split: true,
                            shared: true,
                        },
                    });
                }
            }
            if ('sum_volume' in data) {
                if (data['sum_volume'].length > 0) {
                    has_sum_volume = true;
                    series.push({
                        type: 'column',
                        name: type.name + gettext('Sum Volume'),
                        color: Highcharts.getOptions().colors[0],
                        yAxis: 1,
                        data: data['sum_volume'],
                        zIndex: 1,
                        tooltip: {
                            valueDecimals: 0,
                            split: true,
                            shared: true,
                        },
                    });
                }
            }


            if ('avg_weight' in data) {
                if (data['sum_volume'].length > 0) {
                    has_avg_weight = true
                    series.push({
                        type: 'line',
                        name: type.name + gettext('Average Weight'),
                        color: Highcharts.getOptions().colors[2],
                        yAxis: 2,
                        data: data['avg_weight'],
                        zIndex: 10,
                        marker: {
                            enabled: true,
                            radius: 3,
                        },
                        tooltip: {
                            valueDecimals: 1,
                            split: true,
                            shared: true,
                        },
                    });
                }
            }
        })

        // dynamic generate yAxis settings
        if (has_avg_price) {
            yAxis.push({
                lineWidth: 1,
                title: {
                    text: gettext('Average Price') + '(' + unit.price_unit + ')',
                    style: {
                        color: Highcharts.getOptions().colors[1],
                        fontSize: chart1Helper.manager.fontSize.title,
                    },

                },
                labels: {
                    style: {
                        color: Highcharts.getOptions().colors[1],
                        fontSize: chart1Helper.manager.fontSize.label,
                    },
                    formatter : function(){
                        return Math.round(this.value * 10) / 10;
                    },
                },
                opposite: false
            })
        }
        if (has_sum_volume) {
            yAxis.push({
                lineWidth: 1,
                title: {
                    text: gettext('Sum Volume') + '(' + unit.volume_unit + ')',
                    style: {
                        color: Highcharts.getOptions().colors[0],
                        fontSize: chart1Helper.manager.fontSize.title,
                    },

                },
                labels: {
                    style: {
                        color: Highcharts.getOptions().colors[0],
                        fontSize: chart1Helper.manager.fontSize.label,
                    },
                },
                opposite: true
            })
        }

        if (has_avg_weight) {
            yAxis.push({
                title: {
                    text: gettext('Average Weight') + '(' + unit.weight_unit + ')',
                    style: {
                        color: Highcharts.getOptions().colors[2],
                        fontSize: chart1Helper.manager.fontSize.title,
                    },
                },
                labels: {
                    style: {
                        color: Highcharts.getOptions().colors[2],
                        fontSize: chart1Helper.manager.fontSize.label,
                    },
                    x: 5
                },
                opposite: true
            })
        }

        var chart = Highcharts.chart(container, {

            chart: {
                zoomType: 'x',
                spacing: [10,0,0,0],
                height: thisDevice == 'desktop' ? 600 : 400,
            },

            title: {
                text: chart1Helper.manager.title,
                style: {
                    display: 'block',
                    fontSize: chart1Helper.manager.fontSize.title,
                }
            },


            loading: {
                hideDuration: 1000,
                showDuration: 1000
            },

            rangeSelector: {
                selected: 0
            },

            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: {
                    day: '%m/%d'
                },
                labels: {
                    style: {
                        fontSize: chart1Helper.manager.fontSize.label,
                    }
                },
            },

            yAxis: yAxis,

            tooltip: {
                valueDecimals: 2,
                split: true,
                shared: true,
                xDateFormat: '%Y/%m/%d, %a',
            },

            series: series,

            legend: {
                itemStyle: {
                    fontSize: chart1Helper.manager.fontSize.label,
                },
            },

            exporting: {
                enabled: thisDevice == 'desktop',
                sourceWidth: 1600,
                sourceHeight: this.chartHeight,
                chartOptions: {
                    title: {
                        text: chart1Helper.manager.title,
                        style: {
                            fontSize: chart1Helper.manager.fontSize.title,
                            display: 'block',
                        }
                    }
                }
            },

            responsive: {
                rules: [{
                    condition: {
                        maxWidth: 500
                    },
                    chartOptions: {
                        legend: {
                            align: 'center',
                            verticalAlign: 'bottom',
                            layout: 'horizontal'
                        },

                        yAxis: [
                            {
                                title: null,
                            },
                            {
                                title: null,
                            },
                            {
                                title: null,
                            },
                        ],
                        subtitle: {
                            text: null
                        },
                        credits: {
                            enabled: false
                        }
                    }
                }]
            },
        });

        chart.seriesOptions = seriesOptions;
        chart.unit = unit;

        this.manager.charts.push(chart);

        return chart;

    },
}


