var chart1Helper = {
    container: null,
    manager: {
        monitorProfiles: null,
        watchlistProfiles: null,
        dateRange: {
            min: null,
            max: null,
        },
        fontSize: {
            label: 11,
            title: 11,
        },
        title: gettext('Daily Price/Volume Trend For Two Weeks'),
        colorLevel: {
            marker: {
                danger: '#b94a48',
                warning: '#c09853',
            },
            plotBand: {
                danger: 'rgba(185, 74, 72, 0.15)',
                warning: 'rgba(221, 223, 0, 0.15)',
            },
            plotBandBorder: {
                danger: 'rgba(185, 74, 72, 0.3)',
                warning: 'rgba(221, 223, 0, 0.3)',
            },
        },
        radiusSize: {
            line: 2,
        },
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
            this.manager.radiusSize.line = 5;
        }

        // monitor profiles
        this.manager.monitorProfiles = this.container[0].monitorProfiles || [];
        // watchlist profiles
        this.manager.watchlistProfiles = this.container[0].watchlistProfiles || [];

    },
    markData: function(typeId, data){

        profiles = $.grep(chart1Helper.manager.monitorProfiles, function(profile){
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
                        monitorProfile: profile,
                    }
                }
            })
        })

        return function(radius){

            if(!chart1Helper.manager.monitorProfiles || thisDevice != 'desktop'){
                return data;
            }
            radius = radius || 10;

            data.forEach(function(point, i){
                point.marker = point.monitorProfile ? {
                    symbol: 'triangle',
                    fillColor: '#FFF',
                    radius: radius,
                    lineWidth: radius * 0.5,
                    lineColor: chart1Helper.manager.colorLevel.marker[point.monitorProfile.color],
                } : null;
            })
            return data;
        };
    },
    plotBandUpdate: function(chart){

        var yAxis = chart.yAxis[0];

        var getPlotBands = function(){
            var max = new Date(chart.xAxis[0].getExtremes().max);
            var profiles = $.grep(chart1Helper.manager.monitorProfiles, function(profile, i){
                if(profile.start_date <= max && max <= profile.end_date){
                    return profile;
                }
            })
            var plotBands = profiles.map(function(profile, i){
                return {
                    from: profile.low_price,
                    to: profile.up_price,
                    borderColor: chart1Helper.manager.colorLevel.plotBandBorder[profile.color],
                    borderWidth: 0.5,
                    color: chart1Helper.manager.colorLevel.plotBand[profile.color],
                    label: {
                        text: profile.format_price + '(' + profile.watchlist + ')',
                        style: {
                            color: '#606060',
                        },
                    },
                    zIndex: 3,
                }
            })
            return plotBands;
        };

        return function(redraw){
            if(thisDevice == 'desktop'){
                redraw = redraw || true;
                var plotBands = getPlotBands();

                yAxis.update({
                    plotBands: plotBands,
                    minorGridLineWidth: plotBands ? 0 : 1,
                    gridLineWidth: plotBands ? 0 : 1,
                    alternateGridColor: plotBands ? null : 'undefined',
                }, redraw); // redraw
            }
        }
    },
    setMinToZero: function() {
        // only call chart.events
        if(this.constructor == Highcharts.Chart){
            var chart = this;
            // Sets the min value for the chart
            if (chart.yAxis[0].getExtremes().min < 0) {
                //set the min and return the values
                chart.yAxis[0].setExtremes(0, null, true, false); // redraw
            }
            console.log('Set yAxis[0] min to zero');
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
                    var markData = chart1Helper.markData(type.id, data['avg_price']);
                    has_avg_price = true;
                    series.push({
                        type: 'line',
                        name: type.name + gettext('Average Price'),
                        yAxis: 0,
                        color: Highcharts.getOptions().colors[1],
                        zIndex: 2,
                        data: markData(), // invoke to get marked data
                        marker: {
                            enabled: true,
                            radius: chart1Helper.manager.radiusSize.line,
                            markData: markData, // function
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
                        zIndex: 3,
                        marker: {
                            enabled: true,
                            radius: chart1Helper.manager.radiusSize.line,
                        },
                        data: data['avg_weight'],
                        tooltip: {
                            valueDecimals: 1,
                            split: true,
                            shared: true,
                        },
                    });
                }
            }
        })

        /* Dynamically generate yAxis */
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
                height: thisDevice == 'desktop' ? 625 : 400,
                events: {
                    load: chart1Helper.setMinToZero,
                    render: chart1Helper.setMinToZero,
                },
            },

            title: {
                text: chart1Helper.manager.title,
                style: {
                    fontSize: chart1Helper.manager.fontSize.title,
                    display: thisDevice == 'desktop' ? 'block' : 'none',
                }
            },

            subtitle: {
                text: getBreadCrumb(' / ') !== "" ? getBreadCrumb(' / ') : getShortCutName(),
                style: {
                    fontSize: chart1Helper.manager.fontSize.label,
                    display: thisDevice == 'desktop' ? 'block' : 'none',
                }
            },

            rangeSelector: {
                selected: 0
            },

            plotOptions: {
                series: {
                    connectNulls: true
                }
            },

            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: {
                    day: '%m/%e',
                    week: '%m/%e',
                    month: '%Y/%m',
                    year: '%Y/%m',
                },
                labels: {
                    style: {
                        fontSize: chart1Helper.manager.fontSize.label,
                    }
                },
            },

            yAxis: yAxis,

            tooltip: {
                formatter: function () {
                    var s = '<b>' + Highcharts.dateFormat('%Y/%m/%d, %a', new Date(this.x)) + '</b>';

                    $.each(this.points, function () {
                        s += '<br/><br/>' + this.series.name + ': ' + Highcharts.numberFormat(this.y, this.series.tooltipOptions.valueDecimals);
                        if(this.point.monitorProfile){
                            s += ' (' + this.point.monitorProfile.watchlist + '-' + this.point.monitorProfile.format_price + ')'
                        }
                    });

                    return s;
                },
                shared: true,
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
                },
                buttons: {
                    plotBands: {
                        enabled: thisDevice == 'desktop' && chart1Helper.manager.monitorProfiles.length > 0 ? true : false,
                        text: gettext('PlotBands'),
                        onclick: function () {
                            this.yAxis.forEach(function(yAxis, i){
                                var plotBands = yAxis.plotLinesAndBands;
                                plotBands.forEach(function(plotBand, i){
                                    if (plotBand.hidden) {
                                        plotBand.hidden = false;
                                        plotBand.svgElem.show();
                                        if('label' in plotBand) plotBand.label.show();
                                    } else {
                                        plotBand.hidden = true;
                                        plotBand.svgElem.hide();
                                        if('label' in plotBand) plotBand.label.hide();
                                    }
                                })
                            })
                        },
                        theme: {
                            'stroke-width': 1,
                            stroke: 'silver',
                            r: 5,
                        },
                    },
                },
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
        }, function(chart){

            chart.plotBandUpdate = chart1Helper.plotBandUpdate(chart);
            chart.plotBandUpdate(false); // redraw later

            /* Add extra range to price yAxis */
            var min = chart.yAxis[0].min;
            var max = chart.yAxis[0].max;
            var extra = (max - min) / 20;
            extra = extra > 3 ? extra : 3;
            chart.yAxis[0].update({
                min: min - extra,
                max: max + extra,
            }, false); // redraw later

            /* Plot watchlist flag */
            watchlistFlagData = [];
            chart1Helper.manager.watchlistProfiles.forEach(function(watchlist, i){
                // add watchlist flag if in series date range
                if(watchlist.start_date >= chart.xAxis[0].getExtremes().dataMin){
                    watchlistFlagData.push({
                        x: watchlist.start_date,
                        title: watchlist.name,
                    });
                };
            });
            chart.addSeries({
                type: 'flags',
                name: gettext('Watchlists'),
                data: watchlistFlagData,
                shape: 'flag',
                zIndex: 5,
                showInLegend: false,
                style: {
                    fontSize: chart1Helper.manager.fontSize.label,
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
            }, true); // redraw

        });

        chart.seriesOptions = seriesOptions;
        chart.unit = unit;

        return chart;

    },
}

