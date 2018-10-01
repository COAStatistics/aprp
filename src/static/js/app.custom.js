/*
 * ShortCut click event
 */
$('#shortcut').on('click', 'a', function(){
    var $a = $(this);
    var name = $a.find('.shortcut-name').text();
    $('#shortcut > li > a').removeClass('selected');
    $a.addClass('selected');
});

function getShortCutName() {
    var $a = $('#shortcut a.selected');
    if($a.length === 1) return $a.find('.shortcut-name').text();
}

/*
 * Custom load multiple script in order by loadScript()
 */
function scriptLoader (scriptArray, callback) {
    var arr = scriptArray.reverse();
    var f = function (s, c) {
        return function (){
            loadScript(s, c);
        }
    }
    var stack = [];
    arr.forEach(function(script, i){
        stack.push(f(script, i === 0 ? callback : stack[i-1]));
    })
    stack[stack.length - 1]();
}

/*
 * GET BREADCRUMB
 */
function getBreadCrumb(sep) {
    if(bread_crumb){
        arr = bread_crumb.find('li').map(function(){
            return $(this).text();
        }).toArray();
        uniqueArr = arr.filter(function(item, pos) {
            return arr.indexOf(item) == pos;
        })
        return uniqueArr.join(sep);
    }
}
/*
 * CUSTOM UPDATE BREADCRUMB TO REMOVE "HOME/"
 */
function drawBreadCrumb(opt_breadCrumbs) {
    var a = $("nav li.active > a"),
        b = a.length;

    bread_crumb.empty(),
    a.each(function() {
        bread_crumb.append($("<li></li>").html($.trim($(this).clone().children(".badge").remove().end().text()))), --b || (document.title = bread_crumb.find("li:last-child").text())
    });

    // Push breadcrumb manually -> drawBreadCrumb(["Users", "John Doe"]);
    // Credits: Philip Whitt | philip.whitt@sbcglobal.net
    if (opt_breadCrumbs != undefined) {
        $.each(opt_breadCrumbs, function(index, value) {
            bread_crumb.append($("<li></li>").html(value));
            document.title = bread_crumb.find("li:last-child").text();
        });
    }
}

/*
 * Return true if method need Django csrf token
 */
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/*
 * Use in pagefunction() to initial and destroy custom widget grid
 * Call dynamic_setup_widgets_desktop in pagefunction() if you want to dynamically render content with widget
 */
function dynamic_setup_widgets(container){

    // destroy all widget instances

    if ( $.navAsAjax && enableJarvisWidgets && $("#" + container)[0] ) {

        $("#widget-grid").jarvisWidgets('destroy');
        // debugState
        if (debugState){
            root.console.log("✔ dynamic JarvisWidgets #" + container + " destroyed");
        }

    }
    // end destroy all widgets

    if (thisDevice === "desktop"){

        dynamic_setup_widgets_desktop(container);

    } else {

        // is mobile
        dynamic_setup_widgets_mobile(container);

    }
}
function dynamic_setup_widgets_desktop(container) {

    if ($.fn.jarvisWidgets && enableJarvisWidgets) {

        $('#' + container).jarvisWidgets({

            grid : 'article',
            widgets : '.jarviswidget',
            localStorage : localStorageJarvisWidgets,
            deleteSettingsKey : '#deletesettingskey-options',
            settingsKeyLabel : 'Reset settings?',
            deletePositionKey : '#deletepositionkey-options',
            positionKeyLabel : 'Reset position?',
            sortable : sortableJarvisWidgets,
            buttonsHidden : false,
            // toggle button
            toggleButton : true,
            toggleClass : 'fa fa-minus | fa fa-plus',
            toggleSpeed : 200,
            onToggle : function() {
            },
            // delete btn
            deleteButton : true,
            deleteMsg:'Warning: This action cannot be undone!',
            deleteClass : 'fa fa-times',
            deleteSpeed : 200,
            onDelete : function() {
            },
            // edit btn
            editButton : true,
            editPlaceholder : '.jarviswidget-editbox',
            editClass : 'fa fa-cog | fa fa-save',
            editSpeed : 200,
            onEdit : function() {
            },
            // color button
            colorButton : true,
            // full screen
            fullscreenButton : true,
            fullscreenClass : 'fa fa-expand | fa fa-compress',
            fullscreenDiff : 3,
            onFullscreen : function() {
            },
            // custom btn
            customButton : false,
            customClass : 'folder-10 | next-10',
            customStart : function() {
                alert('Hello you, this is a custom button...');
            },
            customEnd : function() {
                alert('bye, till next time...');
            },
            // order
            buttonOrder : '%refresh% %custom% %edit% %toggle% %fullscreen% %delete%',
            opacity : 1.0,
            dragHandle : '> header',
            placeholderClass : 'jarviswidget-placeholder',
            indicator : true,
            indicatorTime : 600,
            ajax : true,
            timestampPlaceholder : '.jarviswidget-timestamp',
            timestampFormat : 'Last update: %m%/%d%/%y% %h%:%i%:%s%',
            refreshButton : true,
            refreshButtonClass : 'fa fa-refresh',
            labelError : 'Sorry but there was a error:',
            labelUpdated : 'Last Update:',
            labelRefresh : 'Refresh',
            labelDelete : 'Delete widget:',
            afterLoad : function() {
            },
            rtl : false, // best not to toggle this!
            onChange : function() {

            },
            onSave : function() {

            },
            ajaxnav : $.navAsAjax // declears how the localstorage should be saved (HTML or AJAX Version)

        });

    }

}
function dynamic_setup_widgets_mobile(container) {

    if (enableMobileWidgets && enableJarvisWidgets) {
        setup_widgets_desktop();
    }

}

/*
 * OVERRIDE loadURL
 * Modify 1: add data parameter to use "POST" method and add type parameter to use more methods
 * Modify 2: ajax.error => if return 403, redirect to login page
 * Modify 3: add csrf token for django backend
 * Modify 4: Loading gettext
 */
function loadURL(url, container, data, type) {

    data = data || null;
    type = type || "GET";

    // debugState
    if (debugState){
        root.root.console.log("Loading URL: %c" + url, debugStyle);
    }

    return $.ajax({
        type : type,
        url : url,
        dataType : 'html',
        data: data,
        cache : true, // (warning: setting it to false will cause a timestamp and will call the request twice)
        beforeSend : function(xhr, settings) {

            // CSRF token
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }

            // Google Analytics click event
            if(window.ga){
                ga('send', 'pageview', url);
            }

            //IE11 bug fix for googlemaps (delete all google map instances)
            //check if the page is ajax = true, has google map class and the container is #content
            if ($.navAsAjax && $(".google_maps")[0] && (container[0] == $("#content")[0]) ) {

                // target gmaps if any on page
                var collection = $(".google_maps"),
                    i = 0;
                // run for each	map
                collection.each(function() {
                    i ++;
                    // get map id from class elements
                    var divDealerMap = document.getElementById(this.id);

                    if(i == collection.length + 1) {
                        // "callback"
                    } else {
                        // destroy every map found
                        if (divDealerMap) divDealerMap.parentNode.removeChild(divDealerMap);

                        // debugState
                        if (debugState){
                            root.console.log("Destroying maps.........%c" + this.id, debugStyle_warning);
                        }
                    }
                });

                // debugState
                if (debugState){
                    root.console.log("✔ Google map instances nuked!!!");
                }

            } //end fix

            // destroy all datatable instances
            if ( $.navAsAjax && $('.dataTables_wrapper')[0] && (container[0] == $("#content")[0]) ) {

                var tables = $.fn.dataTable.fnTables(true);
                $(tables).each(function () {

                    if($(this).find('.details-control').length != 0) {
                        $(this).find('*').addBack().off().remove();
                        $(this).dataTable().fnDestroy();
                    } else {
                        $(this).dataTable().fnDestroy();
                    }

                });

                // debugState
                if (debugState){
                    root.console.log("✔ Datatable instances nuked!!!");
                }
            }
            // end destroy

            // pop intervals (destroys jarviswidget related intervals)
            if ( $.navAsAjax && $.intervalArr.length > 0 && (container[0] == $("#content")[0]) && enableJarvisWidgets ) {

                while($.intervalArr.length > 0)
                    clearInterval($.intervalArr.pop());
                    // debugState
                    if (debugState){
                        root.console.log("✔ All JarvisWidget intervals cleared");
                    }

            }
            // end pop intervals

            // destroy all widget instances

            if ( $.navAsAjax && (container[0] == $("#content")[0]) && enableJarvisWidgets && $("#widget-grid")[0] ) {

                $("#widget-grid").jarvisWidgets('destroy');
                // debugState
                if (debugState){
                    root.console.log("✔ JarvisWidgets destroyed");
                }

            }
            // end destroy all widgets

            // cluster destroy: destroy other instances that could be on the page
            // this runs a script in the current loaded page before fetching the new page
            if ( $.navAsAjax && (container[0] == $("#content")[0]) ) {

                /*
                 * The following elements should be removed, if they have been created:
                 *
                 *	colorList
                 *	icon
                 *	picker
                 *	inline
                 *	And unbind events from elements:
                 *
                 *	icon
                 *	picker
                 *	inline
                 *	especially $(document).on('mousedown')
                 *	It will be much easier to add namespace to plugin events and then unbind using selected namespace.
                 *
                 *	See also:
                 *
                 *	http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
                 *	http://keith-wood.name/pluginFramework.html
                 */

                // this function is below the pagefunction for all pages that has instances

                if (typeof pagedestroy == 'function') {

                  try {
                        pagedestroy();

                        if (debugState){
                            root.console.log("✔ Pagedestroy()");
                       }
                    }
                    catch(err) {
                       pagedestroy = undefined;

                       if (debugState){
                            root.console.log("! Pagedestroy() Catch Error");
                       }
                  }

                }

                // destroy all inline charts

                if ( $.fn.sparkline && $("#content .sparkline")[0] ) {
                    $("#content .sparkline").sparkline( 'destroy' );

                    if (debugState){
                        root.console.log("✔ Sparkline Charts destroyed!");
                    }
                }

                if ( $.fn.easyPieChart && $("#content .easy-pie-chart")[0] ) {
                    $("#content .easy-pie-chart").easyPieChart( 'destroy' );

                    if (debugState){
                        root.console.log("✔ EasyPieChart Charts destroyed!");
                    }
                }



                // end destory all inline charts

                // destroy form controls: Datepicker, select2, autocomplete, mask, bootstrap slider

                if ( $.fn.select2 && $("#content select.select2")[0] ) {
                    $("#content select.select2").select2('destroy');

                    if (debugState){
                        root.console.log("✔ Select2 destroyed!");
                    }
                }

                if ( $.fn.mask && $('#content [data-mask]')[0] ) {
                    $('#content [data-mask]').unmask();

                    if (debugState){
                        root.console.log("✔ Input Mask destroyed!");
                    }
                }

                if ( $.fn.datepicker && $('#content .datepicker')[0] ) {
                    $('#content .datepicker').off();
                    $('#content .datepicker').remove();

                    if (debugState){
                        root.console.log("✔ Datepicker destroyed!");
                    }
                }

                if ( $.fn.slider && $('#content .slider')[0] ) {
                    $('#content .slider').off();
                    $('#content .slider').remove();

                    if (debugState){
                        root.console.log("✔ Bootstrap Slider destroyed!");
                    }
                }

                // end destroy form controls


            }
            // end cluster destroy

            // empty container and var to start garbage collection (frees memory)
            pagefunction = null;
            container.removeData().html("");

            // place cog
            container.html('<h1 class="ajax-loading-animation"><i class="fa fa-cog fa-spin"></i> ' + gettext('Loading') + '...</h1>');

            // Only draw breadcrumb if it is main content material
            if (container[0] == $("#content")[0]) {

                // clear everything else except these key DOM elements
                // we do this because sometime plugins will leave dynamic elements behind
                $('body').find('> *').filter(':not(' + ignore_key_elms + ')').empty().remove();

                // draw breadcrumb
                drawBreadCrumb();

                // scroll up
                $("html").animate({
                    scrollTop : 0
                }, "fast");
            }
            // end if
        },
        success : function(data) {

            // dump data to container
            container.css({
                opacity : '0.0'
            }).html(data).delay(50).animate({
                opacity : '1.0'
            }, 300);

            // clear data var
            data = null;
            container = null;

            // Google Analytics click event
            if(window.ga){
                ga('send', 'event', 'ajax', 'success', url);
            }
        },
        error : function(xhr, status, thrownError, error) {
            if(xhr.status == 403){
                var res = JSON.parse(xhr.responseText);
                if('login_url' in res){
                    window.location.href = res.login_url;
                }
            }
            container.html('<h4 class="ajax-loading-error"><i class="fa fa-warning txt-color-orangeDark"></i> '+ gettext('Error requesting') + '<span class="txt-color-red">' + url + '</span>: ' + xhr.status + ' <span style="text-transform: capitalize;">'  + thrownError + '</span></h4>');

            // Google Analytics click event
            if(window.ga){
                ga('send', 'event', 'ajax', 'error', url);
            }
        },
        async : true
    });

}

// CUSTOM SHORTCUT

var shortcut_dropdown_watchlist = $('#shortcutWatchlist');

initApp.SmartActionsCustom = function(){

    var smartActions = {
        // WATCHLIST TOGGLE SHORTCUT
        toggleShortcut: function(){

            if (shortcut_dropdown_watchlist.is(":visible")) {
                shortcut_buttons_hide();
            } else {
                shortcut_buttons_show();
            }

            // SHORT CUT (buttons that appear when clicked on user name)
            shortcut_dropdown_watchlist.find('a').click(function(e) {
                e.preventDefault();
                window.location = $(this).attr('href');
                setTimeout(shortcut_buttons_hide, 300);

            });

            // SHORTCUT buttons goes away if mouse is clicked outside of the area
            $(document).mouseup(function(e) {
                if (!shortcut_dropdown_watchlist.is(e.target) && shortcut_dropdown_watchlist.has(e.target).length === 0) {
                    shortcut_buttons_hide();
                }
            });

            // SHORTCUT ANIMATE HIDE
            function shortcut_buttons_hide() {
                shortcut_dropdown_watchlist.animate({
                    height : "hide"
                }, 300, "easeOutCirc");
                $.root_.removeClass('shortcut-on');

            }

            // SHORTCUT ANIMATE SHOW
            function shortcut_buttons_show() {
                shortcut_dropdown_watchlist.animate({
                    height : "show"
                }, 200, "easeOutCirc");
                $.root_.addClass('shortcut-on');
            }

        }
    }

    $.root_.on('click', '[data-action="toggleShortcutWatchlist"]', function(e) {
        smartActions.toggleShortcut();
        e.preventDefault();
    });
}

jQuery(document).ready(function() {
    initApp.SmartActionsCustom();
})

// CUSTOM LEFT NAV JARVISMENU
// ADD ATTRIBUTE "data-load" AND "data-loaded-url" TO REQUEST UL UI FROM BACKEND

$('nav').on('click.jarvismenu-load-element', 'a[data-load]', function(e){
    e.preventDefault();

    var $this = $(this);
    if($this.attr('data-load') || $this.attr('data-load-sending')){
        $this.unbind('click.jarvismenu-load-element');
        return;
    }
    var url = $this.data('load-url');
    $.ajax({
        url: url,
        type: 'get',
        dataType: 'html',
        beforeSend: function(){
            var $spinner = $('<i class="fa fa-refresh fa-spin" style="margin-right: 5px;">');
            $spinner.appendTo($this);
            $this.attr('data-load-sending', true);
        },
        complete: function(){
            $this.parent().find('.fa-spin').remove();
            $this.attr('data-load-sending', false);
        },
    }).done(function(data){
        var $ul = $(data);
        if(!$ul.find('li').length > 0)
            return;
        $ul.insertAfter($this);

        // UNBIND
        $this.closest('ul').find('li a').unbind('click');
        $this.closest('ul').find('b').remove();

        // RE-INITIALIZE UL
        $this.closest('ul').jarvismenu({
          accordion : true,
          speed : $.menu_speed,
          closedSign : '<em class="fa fa-plus-square-o"></em>',
          openedSign : '<em class="fa fa-minus-square-o"></em>'
        });
        // SET ATTRIBUTE
        $this.attr('data-load', true);

        $this.trigger('click');

    }).fail(function(xhr, status, thrownError, error){
        if(xhr.status == 403){
            var res = JSON.parse(xhr.responseText);
            if('login_url' in res){
                window.location.href = res.login_url;
            }
        }
        root.console.log('load jarvis menu element fail');
    })

})

// Replace url on hash change
$(window).on('hashchange', function() {
    history.replaceState(null, '', '/');
});

// Panel Collapse Button
$('#content').on('click', '.js-panel-collapse-close', function(){
    $this = $(this);
    $this.closest('.panel-collapse').collapse('hide');
})
$('#content').on('click', '.js-panel-collapse-show', function(){
    $this = $(this);
    $this.closest('.panel-collapse').collapse('show');
})


// CUSTOM LEFT NAV JARVISMENU
// ADD COLOR ALERT ICON TO ANCHOR

$('nav a[color-alert]').each(function(){
    $this = $(this);

    $dangers = $this.parent().find('[data-name="profile-active-alert"][data-color="danger"]');
    $warnings = $this.parent().find('[data-name="profile-active-alert"][data-color="warning"]');

    if($dangers.length > 0){
        $dangers.first().clone().prependTo($this);
    }else if($warnings.length > 0){
        $warnings.first().clone().prependTo($this);
    }
})






