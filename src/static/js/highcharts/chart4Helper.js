var chart4Helper = {
    container: null,
    manager: {
        fontSize: {
            label: 11,
            title: 11,
        },
        title: gettext('Monthly Price/Volume Distribution Trend'),
    },
    init: function(container){

        this.container = $('#' + container);

        if(this.container.length == 0)
            root.console.log('Cannot find container #' + container);

        // bind submit function
        this.container.find('.js-panel-toolbar-submit').click(function(){
            $this = $(this);
            var typeId = $this.attr('data-type-id');
            var form = $this.closest('.smart-form');
            var averageYears = form.find('[data-name="average-years"]').val();
            var url = $('#chart-functions-tab').find('a[href="#'+ container +'"]').attr('data-load-url');
            data = {
                average_years: averageYears,
            }
            if(url){
                loadURL(url, chart4Helper.container, data, "POST");
            }else{
                root.console.log('Cannot locate chart4 load url!');
            }

        })

        if(thisDevice == 'desktop'){
            this.manager.fontSize.label = 14;
            this.manager.fontSize.title = 18;
        }

    },
    create: function(container, seriesOption, unit, type, index){

        var series = [];

        var yAxisText = '';

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

        objects = []

        if('perc_0' in seriesOption && 'perc_25' in seriesOption && 'perc_50' in seriesOption && 'perc_75' in seriesOption && 'perc_100' in seriesOption){

            for (var j = 0; j < seriesOption['perc_0'].length; j++) {
                objects.push({
                    x: seriesOption['perc_0'][j][0] - 1, // Month integer to index
                    low: seriesOption['perc_0'][j][1],
                    q1: seriesOption['perc_25'][j][1],
                    median: seriesOption['perc_50'][j][1],
                    q3: seriesOption['perc_75'][j][1],
                    high: seriesOption['perc_100'][j][1],
                    mean: seriesOption['mean'][j][1],
                })
            }
        }

        if (objects.length > 0) {
            series.push({
                data: objects,
                tooltip: {
                    valueDecimals: 1,
                    split: true,
                    shared: true,
                    pointFormat: gettext('Maximum') + ' : {point.high}<br/>' +
                                 gettext('Upper quartile') + ' : {point.q3}<br/>' +
                                 '<span style="color:#0C5DA5;font-weight:bold">' + gettext('Median') +': {point.median}</span><br/>' +
                                 gettext('Lower quartile') +' : {point.q1}<br/>' +
                                 gettext('Minimum') +' : {point.low}<br/>' +
                                 '<span style="color:red;font-weight:bold">{0}'+ gettext('Mean') +': {point.mean}</span><br/>',
                },
            })
        }

        var chart = Highcharts.chart(container, {

            chart: {
                type: 'boxplot',
                inverted: true,
                zoomType: 'xy',
                spacing: [10,0,0,0],
                height: thisDevice == 'desktop' ? 625 : 400,
            },

            title: {
                text: chart4Helper.manager.title,
                style: {
                    fontSize: chart4Helper.manager.fontSize.title,
                    display: thisDevice == 'desktop' ? 'block' : 'none',
                }
            },

            subtitle: {
                text: getBreadCrumb(' / ') !== "" ? getBreadCrumb(' / ') : getShortCutName(),
                style: {
                    fontSize: chart4Helper.manager.fontSize.label,
                    display: thisDevice == 'desktop' ? 'block' : 'none',
                }
            },

            legend: {
                enabled: false,
            },

            xAxis: {
                categories: [gettext("Jan"),
                             gettext("Feb"),
                             gettext("Mar"),
                             gettext("Apr"),
                             gettext("May"),
                             gettext("Jun"),
                             gettext("Jul"),
                             gettext("Aug"),
                             gettext("Sep"),
                             gettext("Oct"),
                             gettext("Nov"),
                             gettext("Dec")],
                labels: {
                    style: {
                        fontSize: chart4Helper.manager.fontSize.label,
                    }
                },
            },

            yAxis: {
                title: {
                    text: yAxisText,
                    style: {
                        fontSize: chart4Helper.manager.fontSize.title,
                    },
                },
                labels: {
                    style: {
                        fontSize: chart4Helper.manager.fontSize.label,
                    }
                }
            },

            plotOptions: {
                boxplot: {
                    fillColor: '#F0F0E0',
                    lineWidth: 2,
                    medianColor: '#0C5DA5',
                    medianWidth: 3
                }
            },

            series: series,

            exporting: {
                enabled: thisDevice == 'desktop',
                sourceWidth: 1600,
                sourceHeight: this.chartHeight,
                chartOptions: {
                    title: {
                        text: chart4Helper.manager.title,
                        style: {
                            fontSize: chart4Helper.manager.fontSize.title,
                            display: 'block',
                        }
                    }
                }
            },

        });

        chart.seriesOption = seriesOption;
        chart.unit = unit;

        return chart;
    },
}



