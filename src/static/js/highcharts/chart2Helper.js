var chart2Helper = {
    container: null,
    manager: {
        monitorProfiles: null,
        watchlistProfiles: null,
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
        subtitle: getBreadCrumb ? getBreadCrumb(' / ') : null,
        colorLevel: {
            marker: {
                danger: '#b94a48',
                warning: '#c09853',
            },
            plotBand: {
                danger: 'rgba(185, 74, 72, 0.1)',
                warning: 'rgba(192, 152, 83, 0.1)',
            }
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
        this.manager.monitorProfiles = this.container[0].monitorProfiles || [];
        // watchlist profiles
        this.manager.watchlistProfiles = this.container[0].watchlistProfiles || [];

    },
    markData: function(typeId, data){

        profiles = $.grep(chart2Helper.manager.monitorProfiles, function(profile){
            return profile.type == typeId;
        })

        data.forEach(function(point, i){

            x = point[0];
            y = point[1];

            profiles.forEach(function(profile, j){
                var priceInRange = (profile.low_price <= y) && (y <= profile.up_price);
                var dateInRange = (profile.start_date <= x) && (x <= profile.end_date); // unix
                if(priceInRange && dateInRange){
                    data[i] = {
                        x: x,
                        y: y,
                        monitorProfile: profile,
                    }
                }
            })
        })

        return function(monthLength){

            if(!chart2Helper.manager.monitorProfiles || thisDevice != 'desktop'){
                return data;
            }
            monthLength = monthLength || 1;
            var radius = (12 - monthLength + 1) > 4 ? (12 - monthLength + 1) : 4;
            data.forEach(function(point, i){
                point.marker = point.monitorProfile ? {
                    symbol: 'triangle',
                    fillColor: '#FFF',
                    radius: radius,
                    lineWidth: radius * 0.5,
                    lineColor: chart2Helper.manager.colorLevel.marker[point.monitorProfile.color],
                } : null;
            })

            return data;
        };

    },
    plotBandUpdate: function(chart){

        var yAxis = chart.yAxis[0];

        var getPlotBands = function(){
            var max = new Date(chart.xAxis[0].getExtremes().max);
            var min = new Date(chart.xAxis[0].getExtremes().min);
            var profiles = $.grep(chart2Helper.manager.monitorProfiles, function(profile, i){
                if(profile.start_date <= min && max <= profile.end_date){
                    return profile;
                }
            })
            var plotBands = profiles.map(function(profile, i){
                return {
                    from: profile.low_price,
                    to: profile.up_price,
                    color: chart2Helper.manager.colorLevel.plotBand[profile.color],
                    label: {
                        text: profile.format_price,
                        style: {
                            color: '#606060',
                            zIndex: 1000,
                        }
                    },
                    zIndex: 1000,
                }
            })
            return plotBands;
        };

        return function(){
            var plotBands = getPlotBands();

            yAxis.update({
                plotBands: plotBands,
                minorGridLineWidth: plotBands ? 0 : 1,
                gridLineWidth: plotBands ? 0 : 1,
                alternateGridColor: plotBands ? null : 'undefined',
            }, true); // redraw
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
                    var markData = chart2Helper.markData(type.id, data['avg_price']);
                    series.push({
                        type: 'line',
                        name: type.name + gettext('Average Price'),
                        yAxis: 0,
                        color: Highcharts.getOptions().colors[1],
                        data: markData(), // invoke to get marked data
                        zIndex: 100,
                        turboThreshold: 0, // check every single data-point more than 1000 points
                        marker: {
                            enabled: true,
                            radius: 3,
                            markData: markData, // function
                        },
                        tooltip: {
                            valueDecimals: 2,
                            split: true,
                            shared: true,
                        },
                        customIndexType: 'avg_price',
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
                        customIndexType: 'sum_volume',
                    });
                }
            }

            if ('avg_weight' in data) {
                if (data['avg_weight'].length > 0) {
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
                        customIndexType: 'avg_weight',
                    });
                }
            }
        })

        /* Plot watchlist flags */
        watchlistFlagData = [];
        chart2Helper.manager.watchlistProfiles.forEach(function(watchlist, i){
            // do not plot watchlist flat if out of date range
            if(watchlist.start_date >= chart2Helper.manager.dateRange.min){
                watchlistFlagData.push({
                    x: watchlist.start_date,
                    title: watchlist.name,
                })
            }
        })
        if(watchlistFlagData.length > 0){
            series.push({
                type: 'flags',
                name: gettext('Watchlists'),
                data: watchlistFlagData,
                shape: 'flag',
                zIndex: 1000,
                showInLegend: false,
                style: {
                    fontSize: chart2Helper.manager.fontSize.label,
                    color: 'white',
                    borderColor: '#000',
                },
                fillColor: '#000',
                states: {
                    hover: {
                        fillColor: '#000',
                        color: 'white',
                        borderColor: '#000',
                    }
                },
            })
        }

        /* Dynamically generate yAxis */
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
                opposite: false,
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
                opposite: true,
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
                opposite: true,
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
        }]

        if(thisDevice != 'desktop'){
            buttons = [buttons[0], buttons[1], buttons[2]];
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

            subtitle: {
                text: getBreadCrumb(' / '),
                style: {
                    fontSize: chart2Helper.manager.fontSize.label,
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

                        var chart = this.chart;

                        if(e.trigger === 'rangeSelectorButton'){

                            /* Add one day to min */
                            min = min.add(1).days();
                            this.setExtremes(min.getTime());

                        }

                        if(e.trigger === 'rangeSelectorInput'
                        || e.trigger === 'navigator'
                        || e.trigger === 'rangeSelectorButton'){


                            /* Update series */
                            chart.series.forEach(function(series, i){
                                var indexType = series.userOptions.customIndexType;
                                var className = series.userOptions.className;
                                var type = series.userOptions.customType;

                                /* Update series data marker size */
                                monthLength = Math.abs(e.max - e.min) / (1000 * 3600 * 24 * 31);

                                if((indexType === 'avg_price') && (className !== 'highcharts-navigator-series')){

                                    series.update({
                                        data: series.userOptions.marker.markData(monthLength),
                                    }, false); // redraw later

                                }

                                series.update({
                                    marker: {
                                        radius: monthLength > 3 ? 0 : 3,
                                    },
                                }, false); // redraw later
                            })

                            chart.plotBandUpdate();

                            /* Update date range */
                            chart2Helper.manager.dateRange.min = min;
                            chart2Helper.manager.dateRange.max = max;

                            var $container = $('#chart-2-widget-integration div[data-load]');
                            var min = chart2Helper.manager.dateRange.min;
                            var max = chart2Helper.manager.dateRange.max;
                            integrationHelper.loadTable($container, min, max);
                        }

                        /* Redraw To Update Range Select Input Value */
                        setTimeout(function(){
                            chart.redraw();
                        }, 0);
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
                },
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

            plotOptions: {
                series: {
                    tooltip: {
                        valueDecimals: 2
                    },
                    dataGrouping: {
                        enabled: false,
                    }
                }
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

            chart.plotBandUpdate = chart2Helper.plotBandUpdate(chart);
            if(thisDevice == 'desktop'){
                chart.plotBandUpdate();
            }

            chart.axisRangeUpdate = chart2Helper.axisRangeUpdate(chart);
            if(thisDevice == 'desktop'){
                chart.axisRangeUpdate();
            }

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