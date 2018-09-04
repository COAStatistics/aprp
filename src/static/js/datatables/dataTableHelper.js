var integrationHelper = {
    loadTableJobs: [],
    loadTable: function($container, min, max){

        var url = $container.attr('data-load-url');

        data = {
            start_date: min.getTime(),
            end_date: max.getTime(),
            to_init: true,
        }

        // abort previous jobs
        integrationHelper.loadTableJobs.forEach(function(job, i){
            if(job && job.readyState != 4){
                root.console.log('Abort one previous integration ajax job');
                job.abort();
            };
        });

        var job = loadURL(url, $container, data, "POST");

        integrationHelper.loadTableJobs.push(job);

        // assign ajax to container parent data for load more
        $container[0].ajaxData = {
            min: min,
            max: max,
            url: url,
        }
    },
    loadRow: function(node, $container, url, data){

        var $spinner = $('<i class="fa fa-refresh fa-spin" style="margin-right: 5px;">');
        $btn = $(node);

        if($btn.data('load') || $btn.data('load-sending')){
            return;
        }

        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'html',
            async: true,
            data: data,
            beforeSend: function(xhr, settings){
                $spinner.prependTo($btn);
                $btn.data('load-sending', true);
                // CSRF token
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
                }
            },
            complete: function(){
                $btn.find('.fa-spinner').remove();
                $btn.data('load-sending', false);
            },
            error: function(){
                $btn.find('.fa-spinner').remove();
                $btn.data('load-sending', false);
            },
        }).done(function(data){
            var $trs = $(data);

            // INSERT ROWS
            var table = $container.DataTable();
            $trs.each(function(){
                $this = $(this);
                if($this.is('tr')) table.rows.add($this).draw();
            })

            $btn.text(gettext('All Result Successfully Loaded'));
            $btn.addClass('disabled');

            $tds = $trs.find('td[data-sparkline]');
            if($tds.length > 0 && doChunk){
                doChunk($tds);
            }

            dataTableHelper.compareIntegrationRow($container);

            // SET ATTRIBUTE
            $btn.data('load', true);

        }).fail(function(){
            root.console.log('Load Historical Data Failed');

            $btn.text(gettext('Load Failed') + ', ' + gettext('Retry'));
            $btn.find('.fa-spinner').remove();
            $btn.data('load-sending', false);
        })

    }
}

var dataTableHelper = {
    init: function(){
        if(thisDevice == 'desktop'){
            $.fn.DataTable.ext.pager.numbers_length = 7;
        }
        else{
            $.fn.DataTable.ext.pager.numbers_length = 4;
        }
    },
    responsiveHelpers: [],
    language: {
        sEmptyTable:     gettext("No data available in table"),
        sInfo:           gettext("Showing _START_ to _END_ of _TOTAL_ entries"),
        sInfoEmpty:      gettext("Showing 0 to 0 of 0 entries"),
        sInfoFiltered:   gettext("(filtered from _MAX_ total entries)"),
        sInfoPostFix:    "",
        sInfoThousands:  ",",
        sLengthMenu:     gettext("Show _MENU_ entries"),
        sLoadingRecords: gettext("Loading") + '...',
        sProcessing:     gettext("Processing") + '...',
        sSearch:         gettext("Search"),
        sZeroRecords:    gettext("No matching results found"),
        oPaginate: {
            sFirst:    gettext("First"),
            sLast:     gettext("Last"),
            sNext:     gettext("Next"),
            sPrevious: gettext("Previous"),
        },
        oAria: {
            sSortAscending:  gettext(": activate to sort column ascending"),
            sSortDescending: gettext(": activate to sort column descending"),
        },
        buttons: {
            copyTitle: gettext('Copy To Clipboard'),
            copySuccess: {
                _: gettext('Copy %d rows'),
                1: gettext('Copy 1 row'),
            },
        },
    },
    buttons: {
        copy: function(){
            return {extend: 'copy', text: gettext('Copy')}
        },
        csv: function(){
            return {extend: 'csv', charset: 'UTF-16LE', bom: true, text: gettext('Download') + 'CSV'}
        },
        excel: function(){
            return {extend: 'excel', text: gettext('Download') + 'Excel'}
        },
        pdf: function(){
            return {extend: 'pdf', text: gettext('Download') + 'Pdf'}
        },
        print: function(){
            return {extend: 'print', text: gettext('Print')}
        },
        UI: '\
            <div class="row">\
                <div class="col-sm-12 col-md-12" style="padding-bottom:0.3rem;"></div>\
            </div>\
        ',
        create: function(table){
            var div = $(this.UI);
            var container = $(table.buttons().container());
            div.find('.col-md-12:eq(0)').html(container);
            div.appendTo($(table.table().container()));
        },
    },
    breakpointDefinition : {
        tablet : 1024,
        phone : 480
    },
    createRaw: function(container){
        var responsiveHelper = null;
        this.responsiveHelpers.push(responsiveHelper);

        var $container = $('#'+ container);

        /* Trans Table To DataTable */
        var $table = $container.DataTable({
			dom: "<'dt-toolbar padding-10 padding-left-0'<'col-xs-12 col-sm-12 hidden-xs'B><'col-xs-12 col-sm-12 hidden-sm hidden-md hidden-lg'f>>"+
				 "t"+
				 "<'dt-toolbar-footer'<'col-sm-6 col-xs-12 hidden-xs'i><'col-xs-12 col-sm-6'p>>",
            buttons: [
                dataTableHelper.buttons.csv(),
                dataTableHelper.buttons.excel(),
                dataTableHelper.buttons.print(),
                dataTableHelper.buttons.copy(),
            ],
            number: 3,
			autoWidth : true,
			preDrawCallback : function() {
				// Initialize the responsive datatables helper once.
				if (!responsiveHelper) {
					responsiveHelper = new ResponsiveDatatablesHelper($container, dataTableHelper.breakpointDefinition);
				}
			},
			rowCallback : function(nRow) {
				responsiveHelper.createExpandIcon(nRow);
			},
			drawCallback : function(oSettings) {
				responsiveHelper.respond();
			},
            order: [
                [0, 'asc']
            ],
            language: dataTableHelper.language,
        });

	    // Apply the filter
	    $("#" + container + " thead th input[type=text]").on( 'keyup change', function () {

	        $table
	            .column( $(this).parent().index()+':visible' )
	            .search( this.value )
	            .draw();

	    } );

        return $table;

    },
    createIntegration: function(container){

        function getAjaxDataFromContainer($container){
            // Access ajax data from parent div
            $parent = $container.closest('div[data-load]');
            var ajaxData = $parent[0].ajaxData;
            return ajaxData;
        }

        $container =$('#' + container);

        var responsiveHelper = null;
        this.responsiveHelpers.push(responsiveHelper);

        // exporting column options
        var csv = dataTableHelper.buttons.csv();
        var excel = dataTableHelper.buttons.excel();
        var print = dataTableHelper.buttons.print();

        var columnLength = $container.find('tbody > tr:first td').length;
        switch(columnLength){
            case 3:
                columns = [0, 1];
                break;
            case 5:
                columns = [0, 1, 3];
                break;
            case 7:
                columns = [0, 1, 3, 5];
                break;
            default:
                columns = null;
                break;
        }

        if(columns){
            exportOptions = {
                columns: columns,
            }
            csv['exportOptions'] = exportOptions;
            excel['exportOptions'] = exportOptions;
            print['exportOptions'] = exportOptions;
        }

        buttons = [
            csv,
        ]

        if(thisDevice == 'desktop'){
            buttons.push(excel),
            buttons.push(print),
            buttons.push(dataTableHelper.buttons.copy())
        }

        var ajaxData = getAjaxDataFromContainer($container);

        // Add btnLoad if start date and end date in same year
        sameYear = ajaxData.min.getYear() == ajaxData.max.getYear();
        btnLoadRow = sameYear ? {
            text: gettext('Load Historical Data'),
            action: function(e, dt, node){
                var typeId = $container.attr('data-type-id');
                var ajaxData = getAjaxDataFromContainer($container);
                var data = {
                    start_date: ajaxData.min.getTime(),
                    end_date: ajaxData.max.getTime(),
                    to_init: false,
                    type_id: typeId,
                }
                integrationHelper.loadRow(node, $container, ajaxData.url, data);
            },
        } : null
        if(sameYear) buttons.push(btnLoadRow);

        // adjust column width
        var columnLength = $container.find("tr:first th").length;
        var columnWidth = 100 / columnLength + '%';

        console.log(columnLength, columnWidth)

        var columns = [];
        for(var i = 0; i < columnLength; i++){
            columns.push({ width: columnWidth });
        }

        var $table = $container.DataTable({
			dom: "<'dt-toolbar padding-10 padding-left-0'<'col-xs-12 col-sm-12'B>>"+
				 "t"+
				 "<'dt-toolbar-footer'>",
            buttons: buttons,
            paging: false,
			autoWidth : false,
			preDrawCallback : function() {
				// Initialize the responsive datatables helper once.
				if (!responsiveHelper) {
					responsiveHelper = new ResponsiveDatatablesHelper($container, dataTableHelper.breakpointDefinition);
				}
			},
			rowCallback : function(nRow) {
				responsiveHelper.createExpandIcon(nRow);
			},
			drawCallback : function(oSettings) {
				responsiveHelper.respond();
			},
			columns: columns,
            order: [
                [0, 'desc']
            ],
            language: dataTableHelper.language,
        });

        // sparkle line chunk
        $td = $container.find('td[data-sparkline]');
        if(doChunk && $td){
            doChunk($td);
        }

        dataTableHelper.compareIntegrationRow($container);

        return $table;
    },
    compareIntegrationRow: function(){
        $container.find('td[data-base="false"]').each(function(){
            $this = $(this);

            if($this.attr('data-compared')){
                return;
            }

            var columnNo = $this.index();
            $base = $this.closest("table").find("tr td:nth-child(" + (columnNo+1) + ")").filter('[data-base="true"]');
            if($base.length == 1){
                var thisValue = parseFloat($this.data('value'));
                var baseValue = parseFloat($base.data('value'));
                var diff = ((baseValue - thisValue) / thisValue) * 100;
                diff = Math.round(diff * 10) / 10;
                if(diff > 0){
                    var $ui = $('<span class="label bg-color-redLight pull-right hidden-xs hidden-sm"><i class="fa fa-caret-up"></i> '+ diff +'%</span>');
                }else{
                    var $ui = $('<span class="label bg-color-greenLight pull-right hidden-xs hidden-sm"><i class="fa fa-caret-down"></i> '+ diff * -1 +'%</span>');
                }
                $ui.appendTo($this);
            }

            $this.attr('data-compared', true);
        })
    },
}

dataTableHelper.init();