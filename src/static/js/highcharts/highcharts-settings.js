/* Box Plot Settings */
(function (H) {

    H.seriesTypes.boxplot.prototype.pointArrayMap = ['low', 'q1', 'median', 'q3', 'high', 'mean'];

    H.seriesTypes.boxplot.prototype.toYData = function (point) {
        return [point.low, point.q1, point.median, point.q3, point.high, point.mean];
    };

    H.wrap(H.seriesTypes.boxplot.prototype, 'drawPoints', function (p) {
        p.call(this);
        var chart = this.chart,
            r = chart.renderer,
            xAxis = this.xAxis,
            yAxis = this.yAxis,
            x, y;

        H.each(this.points, function (p, i) {
            x = p.shapeArgs.x;
            y = p.meanPlot;

            if (p.meanPlotX) {
                p.meanPlotX.attr({
                    d: ['M', x, y, 'L', x + p.shapeArgs.width, y]
                });
            } else {
                p.meanPlotX = r.path(['M', x, y, 'L', x + p.shapeArgs.width, y]).attr({
                    stroke: 'red',
                        'stroke-width': 2
                }).add(p.series.group);
            }

        });
    });

})(Highcharts);

/* Theme */
Highcharts.theme = {
    colors: ['#058DC7', '#ED561B', '#DDDF00', '#50B432', '#24CBE5', '#64E572',
        '#FF9655', '#FFF263', '#6AF9C4'],
    chart: {
        backgroundColor: null,
        style: {
            fontFamily: 'Open Sans,Microsoft JhengHei,Arial,Helvetica,Sans-Serif;'
        },
    },
    title: {
        style: {
            fontSize: '1rem',
            fontWeight: 'bold',
            textTransform: 'uppercase'
        }
    },
    tooltip : {
        positioner: function (w, h, point) {
            var position = this.getPosition(w, h, point);
            if (this.chart.flagTooltip) {
                position.y -= 40;
            }
            return position;
        },
        useHTML : true,
        headerFormat: '<b>{point.key}</b>',
        formatter : function (tooltip) {
            if (this.point && this.point.title && this.point.text) {
                var textContainer = thisDevice == 'desktop' ? '<p style="width: 300px;white-space: normal;">' : '<p style="width:120px; white-space: normal;">'
                var text = '<b>' + Highcharts.dateFormat('%Y/%m/%d, %a', this.point.x) + '</b></br></br>' +
                    textContainer + this.point.text + '</p>';
                return '</br></br>' + text + '</span>';
            }
            return tooltip.defaultFormatter.apply(this, [tooltip]);
        }
    },
    legend: {
        itemStyle: {
            fontWeight: 'bold',
            fontSize: '0.8rem'
        }
    },
    xAxis: {
        gridLineWidth: 1,
        title: {
            style: {
                fontSize: '1rem',
            }
        },
        labels: {
            style: {
                fontSize: '0.8rem'
            }
        },
    },
    yAxis: {
        minorTickInterval: 'auto',
        title: {
            style: {
                fontSize: '1rem',
            }
        },
        labels: {
            style: {
                fontSize: '0.8rem',
            }
        }
    },
    plotOptions: {
        candlestick: {
            lineColor: '#404048'
        },
        series: {
            animation: {
                duration: 1000,
            },
        },
    },

    // General
    background2: '#F0F0EA'

};

// Apply the theme
Highcharts.setOptions(Highcharts.theme);

/* i18n */
Highcharts.setOptions({
    global: {
      useUTC: false
    },
    lang: {
        noData: gettext("No data to display or no product been monitoring under current watchlist"),
        loading: gettext("Loading") + '...',
        numericSymbols: [gettext("k"),
                         gettext("M"),
                         gettext("G"),
                         gettext("T"),
                         gettext("P"),
                         gettext("E")],
        months: [gettext("January"),
                 gettext("February"),
                 gettext("March"),
                 gettext("April"),
                 gettext("May"),
                 gettext("June"),
                 gettext("July"),
                 gettext("August"),
                 gettext("September"),
                 gettext("October"),
                 gettext("November"),
                 gettext("December")],
        weekdays: [gettext("Sunday"),
                   gettext("Monday"),
                   gettext("Tuesday"),
                   gettext("Wednesday"),
                   gettext("Thursday"),
                   gettext("Friday"),
                   gettext("Saturday")],
        shortMonths: [gettext("Jan"),
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
        exportButtonTitle: gettext("Export"),
        printButtonTitle: gettext("Print"),
        contextButtonTitle: gettext("Chart context menu"),
        rangeSelectorFrom: gettext("From"),
        rangeSelectorTo: gettext("TO"),
        rangeSelectorZoom: gettext("Zoom"),
        printChart: gettext("Print chart"),
        downloadPNG: gettext("Download") + "PNG",
        downloadJPEG: gettext("Download") + "JPEG",
        downloadPDF: gettext("Download") + "PDF",
        downloadSVG: gettext("Download") + "SVG",
    }
})
