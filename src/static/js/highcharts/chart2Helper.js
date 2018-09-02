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
        monitorProfiles: null,
        colorLevel: {
            danger: '#b94a48',
            warning: '#c09853'
        },
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

        // monitor profiles
        this.manager.monitorProfiles = this.container[0].monitorProfiles;

    },
    mark: function(typeId, data){
        if(!this.manager.monitorProfiles){
            return data;
        }
        profiles = $.grep(this.manager.monitorProfiles, function(profile){
            return profile.type == typeId;
        })
        data.forEach(function(point, i){
            x = point[0];
            y = point[1];
            profiles.forEach(function(profile, j){
                if((profile.low_price <= y) && (y <= profile.up_price)){
                    data[i] = {
                        x: x,
                        y: y,
                        marker: {
                            symbol: 'triangle',
                            fillColor: '#FFF',
                            radius: 8,
                            lineColor: chart2Helper.manager.colorLevel[profile.color],
                            lineWidth: 5,
                        },
                        monitorProfile: profile,
                    }
                }
            })
        })
        return data;
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
                        data: chart2Helper.mark(type.id, data['avg_price']),
                        zIndex: 100,
                        marker: {
                            enabled: true,
                            radius: 1,
                            states: {
                                hover: {
                                    radius: 5,
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
                            radius: 1,
                            states: {
                                hover: {
                                    radius: 5,
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
                                chart2Helper.manager.charts.forEach(function(chart, i){
                                    chart.redraw();
                                })
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

            legend: {
                enabled: true,
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
                        text: chart2Helper.manager.title,
                        style: {
                            fontSize: chart2Helper.manager.fontSize.title,
                            display: 'block',
                        }
                    }
                },
            },

            tooltip: {
                formatter: function () {
                    var s = '<b>' + Highcharts.dateFormat('%Y/%m/%d, %a', new Date(this.x)) + '</b>';

                    $.each(this.points, function () {
                        s += '<br/><br/>' + this.series.name + ': ' + Highcharts.numberFormat(this.y, this.series.tooltipOptions.valueDecimals);
                        if(this.point.monitorProfile){
                            s += ' (' + this.point.monitorProfile.watchlist + '-' + this.point.monitorProfile.format_price +  ')'
                        }
                    });

                    return s;
                },
                shared: true,
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

                // init integration datatable
                integrationHelper.loadTable($('#chart-2-widget-integration div[data-load]'), min, max);

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

