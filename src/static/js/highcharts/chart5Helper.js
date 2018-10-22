var chart5Helper = {
    manager: {
        chartContainers: [],
        getCharts: function(){
            return this.chartContainers.map(function(container, i){
                return $('#' + container).highcharts();
            })
        },
        fontSize: {
            label: 11,
            title: 11,
        },
        title: gettext('Important Transition Events'),
        url: null,
        contentType: null,
        objectId: null,
        locationImage: null,
    },
    init: function(url, contentType, objectId){

        this.manager.charts = [];

        if(thisDevice == 'desktop'){
            this.manager.fontSize.label = 14;
            this.manager.fontSize.title = 18;
        }

        this.manager.url = url;
        this.manager.contentType = contentType;
        this.manager.objectId = objectId;

        image = thisDevice === 'desktop' ? 'dot-32.png' : 'dot-24.png';
        this.manager.locationImage = 'url('+ window.location.href + 'static/img/chart/' + image + ')';

    },
    create: function(container, seriesOptions, unit){

        this.manager.chartContainers.push(container);

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
                        type: 'spline',
                        name: type.name + gettext('Average Price'),
                        yAxis: 0,
                        zIndex: 1,
                        lineWidth: 0.7,
                        color: Highcharts.getOptions().colors[0],
                        marker: {
                            enabled: false,
                        },
                        data: data['avg_price'],
                        tooltip: {
                            valueDecimals: 2,
                            split: true,
                            shared: true,
                        },
                        id: 'avg_price_' + type.name,
                        customIndexType: 'avg_price',
                    });

                }
            }

        })

        /* Dynamically generate yAxis */
        if (has_avg_price) {
            yAxis.push({
                title: {
                    text: gettext('Average Price') + '(' + unit.price_unit + ')',
                    style: {
                        color: Highcharts.getOptions().colors[1],
                        fontSize: chart5Helper.manager.fontSize.title,
                    },

                },
                labels: {
                    style: {
                        color: Highcharts.getOptions().colors[1],
                        fontSize: chart5Helper.manager.fontSize.label,
                    },
                    formatter : function(){
                        return Math.round(this.value * 10) / 10;
                    },
                },
                opposite: false,
            })
        }

        var chart = Highcharts.chart(container, {

            chart: {
                zoomType: 'x',
                spacing: [10,0,0,0],
                height: thisDevice == 'desktop' ? 625 : 400,
            },

            title: {
                text: chart5Helper.manager.title,
                style: {
                    fontSize: chart5Helper.manager.fontSize.title,
                    display: thisDevice == 'desktop' ? 'block' : 'none',
                }
            },

            subtitle: {
                text: getBreadCrumb(' / ') !== "" ? getBreadCrumb(' / ') : getShortCutName(),
                style: {
                    fontSize: chart5Helper.manager.fontSize.label,
                    display: thisDevice == 'desktop' ? 'block' : 'none',
                }
            },

            rangeSelector: {
                selected: 0
            },

            plotOptions: {
                series: {
                    connectNulls: true,
                },
//                area: {
//                    lineWidth: 0.3,
//                    threshold: null, // Y axis value to serve as the base for the area
//                    tooltip: {
//                        xDateFormat: '%Y/%m/%d, %a',
//                        valueDecimals: 2,
//                    }
//                },
                flags: {
                    tooltip: {
                        xDateFormat: '%Y/%m/%d, %a',
                    }
                },
            },

            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: {
                    day: '%m/%e',
                    week: '%m/%e',
                    month: '%Y/%m',
                    year: '%Y',
                },
                labels: {
                    style: {
                        fontSize: chart5Helper.manager.fontSize.label,
                    }
                },
            },

            yAxis: yAxis,

            series: series,

            legend: {
                itemStyle: {
                    fontSize: chart5Helper.manager.fontSize.label,
                },
            },


            exporting: {
                enabled: thisDevice == 'desktop',
                sourceWidth: 1600,
                sourceHeight: this.chartHeight,
                chartOptions: {
                    title: {
                        text: chart5Helper.manager.title,
                        style: {
                            fontSize: chart5Helper.manager.fontSize.title,
                            display: 'block',
                        }
                    }
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
            $.ajax({
                url: chart5Helper.manager.url,
                data: {
                    content_type: chart5Helper.manager.contentType,
                    object_id: chart5Helper.manager.objectId,
                    datatable: false,
                    order_by: 'date',
                },
                async: false,
                success: function(data) {
                    // set event flag series data
                    if(data.length > 0){
                        var points = [];
                        var range = chart.xAxis[0].getExtremes();
                        data.forEach(function(point, i){
                            var date = new Date(point.date).getTime();

                            if(range.dataMin < date < range.dataMax){

                                var typeLabels = '';
                                point.types.forEach(function(type, i){
                                    var labelColor = type.level === 1 ? 'danger' : 'info';
                                    typeLabels += '<span style="margin-right:3px;" class="label label-' + labelColor +'">' + type.label + '</span>';
                                })
                                var text = typeLabels + '</br></br><b>' + point.name + '</b>';
                                if(thisDevice == 'desktop') text = text + '</br>' + point.context;
                                points.push({
                                    x: date,
                                    text: text,
                                    title: ' ',
                                })
                            }
                        })
                        chart.series.forEach(function(series, i){
                            if(series.type === 'flags'){
                                series.remove();
                            }
                            else if(series.userOptions.customIndexType === 'avg_price'){
                                chart.addSeries({
                                    type: 'flags',
                                    shape: chart5Helper.manager.locationImage,
                                    name: 'Events',
                                    color: series.userOptions.color, // same as onSeries
                                    fillColor: series.userOptions.color,
                                    data: points,
                                    onSeries: series.userOptions.id,
                                    showInLegend: false,
                                    style: { // text style
                                        color: 'white',
                                        fontSize: chart5Helper.manager.fontSize.label,
                                    },
                                    zIndex: 5,
                                    states: {
                                        hover: {
                                            color: 'black', // same as onSeries
                                            fillColor: series.userOptions.color,
                                        }
                                    },
                                }, true);
                            }
                        })
                    }else{
                        root.console.log('No related events data.')
                    }
                },
                cache: false,
            });
        });

        chart.seriesOptions = seriesOptions;
        chart.unit = unit;

        return chart;

    },
}

