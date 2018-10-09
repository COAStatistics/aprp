var chart3Helper = {
    container: null,
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
        title: gettext('Daily Price/Volume Trend Year By Year'),
    },
    init: function(container){

        this.container = $('#' + container);

        if(this.container.length == 0)
            root.console.log('Cannot find container #' + container);

        if(thisDevice == 'desktop'){
            this.manager.fontSize.label = 14;
            this.manager.fontSize.title = 18;
        }

        this.manager.$form = this.container.find('.smart-form');

        // bind submit function
        this.container.on('click', '.js-panel-toolbar-submit', function(){
            chart3Helper.updateChartSeries();
        })
    },
    updateChartSeries: function() {
        var averageYears = this.manager.$form.find('[data-name="average-years"]').val();
        var displayYears = this.manager.$form.find('[data-name="display-years"]').val();
        var charts = this.manager.getCharts();
        charts.forEach(function(chart, i){
            chart3Helper.replaceAvgSeries(chart, averageYears);
            chart3Helper.displaySeries(chart, displayYears);
        })
    },
    create: function(container, seriesOption, unit, type, index) {

        var series = []

        var yAxisText = ''

        switch(index){
            case 'price':
                yAxisText = gettext('Average Price') + '(' + unit.price_unit + ')';
                break;
            case 'volume':
                yAxisText = gettext('Sum Volume') + '(' + unit.volume_unit + ')';
                break;
            case 'weight':
                yAxisText = gettext('Average Weight') + '(' + unit.weight_unit + ')';
                break;
        }

        for (var key in seriesOption) {

            if (seriesOption.hasOwnProperty(key)) {

                var j = Object.keys(seriesOption).length - Object.keys(seriesOption).indexOf(key)

                series.push({
                    customIsAverage: false, // Custom Attribute To Determinate '2018' And 'All'
                    name: key,
                    data: seriesOption[key],
                    color: Highcharts.getOptions().colors[j],
                    zIndex: 10,
                    showInLegend: true,
                })
            }
        }

        var averageYears = this.manager.$form.find('[data-name="average-years"]').val();
        avgSeries = chart3Helper.createAvgSeries(seriesOption, averageYears);

        if(avgSeries != null)
            series.push(avgSeries);

        var chart = Highcharts.chart(container, {

            chart: {
                zoomType: 'x',
                spacing: [10,0,0,0],
                height: thisDevice == 'desktop' ? 750 : 400,
            },

            title: {
                text: chart3Helper.manager.title,
                style: {
                    fontSize: chart3Helper.manager.fontSize.title,
                    display: thisDevice == 'desktop' ? 'block' : 'none',
                }
            },

            subtitle: {
                text: getBreadCrumb(' / ') !== "" ? getBreadCrumb(' / ') : getShortCutName(),
                style: {
                    fontSize: chart3Helper.manager.fontSize.label,
                    display: thisDevice == 'desktop' ? 'block' : 'none',
                }
            },

            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: {
                    day: '%m/%d',
                    week: '%m/%d',
                    month: '%b',
                },
                crosshair: {
                    width: 2,
                    color: 'black',
                    dashStyle: 'Solid',
                    label: {
                        enable: true,
                    },
                },
                labels: {
                    style: {
                        fontSize: chart3Helper.manager.fontSize.label,
                    }
                }
            },
            yAxis: {
                title: {
                    text: yAxisText,
                    style: {
                        fontSize: chart3Helper.manager.fontSize.title,
                    }
                },
                labels: {
                    style: {
                        fontSize: chart3Helper.manager.fontSize.label,
                    }
                }
            },
            legend: {
                itemStyle: {
                    fontSize: chart3Helper.manager.fontSize.label,
                },
            },
            tooltip: {
                valueDecimals: 1,
                split: true,
                shared: true,
                xDateFormat: '%m/%d',
            },

            series: series,

            exporting: {
                enabled: thisDevice == 'desktop',
                sourceWidth: 1600,
                sourceHeight: this.chartHeight,
                chartOptions: {
                    title: {
                        text: chart3Helper.manager.title,
                        style: {
                            fontSize: chart3Helper.manager.fontSize.title,
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
        })

        chart.seriesOption = seriesOption;
        chart.unit = unit;

        this.manager.chartContainers.push(container);

        return chart;
    },
    createAvgSeries: function(seriesOption, years){

        data = [];

        years = years || Object.keys(seriesOption);

        /* Return NaN If seriesOption IS {} */
        if(Object.keys(seriesOption).length == 0) return null;

        for(var i = 0; i < 366; i++){
            var sum = 0;
            var count = 0;
            var time = null;
            var time = seriesOption[Object.keys(seriesOption)[0]][i][0];
            years.forEach(function(year, j){
                var value = seriesOption[year][i][1];
                if(value != null){
                    count ++;
                    sum += value;
                }
            })
            var avg = sum/count == 0 ? null : sum/count;
            data[i] = [time, avg];
        }

        var avgSeries = {
            customIsAverage: true,
            visible: true,
            showInLegend: true,
            name: gettext('Average Year By Year'),
            type: 'area',
            data: data,
            gapSize: 5,
            color: Highcharts.getOptions().colors[0],
            lineWidth: 0,
            fillColor: {
                linearGradient: {
                    x1: 0,
                    y1: 0,
                    x2: 0,
                    y2: 1
                },
                stops: [
                    [0, Highcharts.getOptions().colors[0]],
                    [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                ]
            },
            threshold: null,
            zIndex: 1
        }

        return avgSeries;
    },
    replaceAvgSeries: function(chart, years){
        /* Replace Avg Series To Chart */
        var indexAvgYearObj = $.grep(chart.series, function(series, i){
            return series.options.customIsAverage == true;
        })[0];

        if(!indexAvgYearObj){
            root.console.log("Cannot find average series in chart:" + chart);
            return;
        }

        avgSeries = chart3Helper.createAvgSeries(chart.seriesOption, years);
        indexAvgYearObj.setData(avgSeries.data, true);
    },
    displaySeries: function(chart, years){

        chart.series.forEach(function(series, i){
            if(series.userOptions.customIsAverage === true)
                return;
            var showInLegend = years.indexOf(series.name) > -1;
            series.update({
                showInLegend: showInLegend,
                visible: showInLegend,
            })
        })
    },
}





