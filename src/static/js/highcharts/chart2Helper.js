var chart2Helper = {
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
        title: gettext('Daily Price/Volume Trend For All Time'),
    },
    init: function(container){
        this.container = $('#' + container);

        if(this.container.length == 0)
            root.console.log('Cannot find container #' + container);

        this.manager.charts = [];

        if(thisDevice == 'desktop'){
            this.manager.fontSize.label = 14;
            this.manager.fontSize.title = 18;
        }

    },
    create: function(container, seriesOptions, unit) {

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
                            radius: 0,
                            states: {
                                hover: {
                                    radius: 2
                                }
                            }
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
                        marker: {
                            radius: 0,
                            states: {
                                hover: {
                                    radius: 2
                                }
                            }
                        },
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
                            radius: 0,
                            states: {
                                hover: {
                                    radius: 2
                                }
                            }
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
                        fontSize: chart2Helper.manager.fontSize.title,
                    },
                },
                labels: {
                    style: {
                        color: Highcharts.getOptions().colors[1],
                        fontSize: chart2Helper.manager.fontSize.label,
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
                    text: gettext('Volume') + '(' + unit.volume_unit + ')',
                    style: {
                        color: Highcharts.getOptions().colors[0],
                        fontSize: chart2Helper.manager.fontSize.title,
                    },
                },
                labels: {
                    style: {
                        color: Highcharts.getOptions().colors[0],
                        fontSize: chart2Helper.manager.fontSize.label,
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
                        fontSize: chart2Helper.manager.fontSize.title,
                    },
                },
                labels: {
                    style: {
                        color: Highcharts.getOptions().colors[2],
                        fontSize: chart2Helper.manager.fontSize.label,
                    },
                    x: 5
                },
                opposite: true
            })
        }

        var buttons = [{
            type: 'month',
            count: 1,
            text: gettext('1m'),
        },  {
            type: 'month',
            count: 3,
            text: gettext('3m'),
        },  {
            type: 'month',
            count: 6,
            text: gettext('6m'),
        },  {
            type: 'year',
            count: 1,
            text: gettext('1y'),
        }, {
            type: 'all',
            text: gettext('all'),
        }]

        if(thisDevice != 'desktop'){
            buttons = [buttons[0], buttons[2], buttons[3]];
        }

        var chart = Highcharts.stockChart(container, {

            chart: {
                zoomType: 'x',
                spacing: [10,0,0,0],
                height: thisDevice == 'desktop' ? 600 : 400,
            },

            title: {
                text: chart2Helper.manager.title,
                style: {
                    fontSize: chart2Helper.manager.fontSize.title,
                    display: thisDevice == 'desktop' ? 'block' : 'none',
                }
            },


            rangeSelector: {
                inputEnabled: true,
                buttons: buttons,
                buttonTheme: {
                    width: 60
                },
                selected: 0,
            },

            xAxis: {
                events: {
                    afterSetExtremes: function(e) {

                        var max = new Date(this.getExtremes().max);
                        var min = new Date(this.getExtremes().min);

                        if(e.trigger == 'rangeSelectorButton'){

                            /* Add one day to min */
                            min = min.add(1).days();
                            this.setExtremes(min.getTime());

                            /* Redraw To Update Range Select Input Value */
                            setTimeout(function(){
                                chart2Helper.container.highcharts().redraw();
                            }, 0);
                        }
                        if(e.trigger == 'rangeSelectorInput'
                        || e.trigger == 'navigator'
                        || e.trigger == 'rangeSelectorButton'){

                            /* Update date range */
                            chart2Helper.manager.dateRange.min = min;
                            chart2Helper.manager.dateRange.max = max;

                            var $container = $('#chart-2-widget-integration div[data-load]');
                            var min = chart2Helper.manager.dateRange.min;
                            var max = chart2Helper.manager.dateRange.max;
                            integrationHelper.loadTable($container, min, max);
                        }
                    },
                },
                type: 'datetime',
                dateTimeLabelFormats: {
                    day: '%m/%e',
                    week: '%m/%e',
                    month: '%Y/%m',
                    year: '%Y/%m',
                },
                labels: {
                    style: {
                        fontSize: chart2Helper.manager.fontSize.label,
                    }
                }
            },

            loading: {
                hideDuration: 1000,
                showDuration: 1000
            },

            yAxis: yAxis,

            series: series,

            exporting: {
                enabled: thisDevice == 'desktop',
                sourceWidth: 1600,
                sourceHeight: this.chartHeight,
                chartOptions: {
                    title: {
                        text: chart2Helper.manager.title,
                        style: {
                            fontSize: chart2Helper.manager.fontSize.title,
                            display: 'block',
                        }
                    }
                },
            },

            tooltip: {
                xDateFormat: '%Y/%m/%d, %a',
            },

            responsive: {
                rules: [{
                    condition: {
                        maxWidth: 500,
                    },
                    chartOptions: {
                        chart: {
                            height: 350,
                        },
                        subtitle: {
                            text: null
                        },
                        navigator: {
                            enabled: false
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
                    }
                }]
            },

        }, function (chart) {


                var max = new Date(chart.xAxis[0].getExtremes().max);
                var min = new Date(chart.xAxis[0].getExtremes().min);

                /* Add 1 day to min for custom purpose */
                min = min.add(1).days();
                chart.xAxis[0].setExtremes(min.getTime());

                /* Init chart2Helper dateRange */
                chart2Helper.manager.dateRange.min = min;
                chart2Helper.manager.dateRange.max = max;

                /* Apply Datepicker */
                setTimeout(function () {
                    $('input.highcharts-range-selector', $(chart.container).parent())
                        .datepicker();
                }, 0);

        });

        chart.seriesOptions = seriesOptions;
        chart.unit = unit;

        this.manager.charts.push(chart);

        return chart;
    },
}

// Set the datepicker's date format
$.datepicker.setDefaults({
    dateFormat: 'yy-mm-dd',
    onSelect: function () {
        this.onchange();
        this.onblur();
    }
});

