// https://learn.jquery.com/plugins/basic-plugin-creation/
(function($) {

    var originalVal = $.fn.val;

    // Plugin support: django-ckeditor
    $.fn.val = function(value) {
        $this = $(this);

        if (typeof value != 'undefined') {
            // ckeditor field setter
            if (window.CKEDITOR && $this.hasClass('ckeditorwidget')) {
                var id = $this.attr('id');
                return CKEDITOR.instances[id].setData(value);
            }
            return originalVal.apply(this, [value]);
        } else {
            // ckeditor field getter
            if (window.CKEDITOR && $this.hasClass('ckeditorwidget')) {
                var id = $this.attr('id');
                return CKEDITOR.instances[id].getData();
            }
            return originalVal.apply(this);
        }
    };

    $.fn.formcontrol = function() {

        $form = $(this);

        // Plugin support: django-tagulous
        function initAfterSetData() {

            // init tagulous
            var $tagulouses = $form.find('input[data-tagulous]');
            if (window.Tagulous && $tagulouses.length > 0) {
                Tagulous.select2($tagulouses, false);
            }
        }

        // init datepicker
        if ($.ui) {
            var dateInputs = $form.find('[data-datepicker]').not('.hasDatepicker');
            dateInputs.datepicker({
                dateFormat: 'yy/mm/dd',
            });
        }

        // validation
        if (!$form.attr('hasvalidate')) {
            $form.find('.form-group').each(function() {
                $(this).append('<div class="help-block" style="display: none;"></div>');
            })
            $form.attr('hasvalidate', 'hasvalidate');
        } else {
            // reset
            $form.find('.help-block').text('').hide();
            $form.find('.form-group').removeClass('has-error');
        }

        this.validate = function(data) {
            data = typeof(data) === 'object' ? data : {};
            Object.keys(data).forEach(function(key, i) {

                $field = $form.find('#div_id_' + key);
                $field.find('.help-block').html(data[key].join('</br>')).show();
                $field.addClass('has-error');

            })
        }

        this.data = function(data, callback) {

            data = typeof(data) === 'object' ? data : {};

            // setter
            Object.keys(data).forEach(function(key, i) {
                $field = $form.find('[name="' + key + '"]');
                $field.val(data[key]);
                // checkbox
                if($field.attr('type') === 'checkbox'){
                    $field.prop('checked', data[key]);
                }

            })

            initAfterSetData();
            if(typeof callback === 'function') callback();

            // getter
            return $form.serializeArray().reduce(function(obj, item) {
                obj[item.name] = item.value;
                return obj;
            }, {});
        }

        // reset form
        this.reset = function() {
            $form.trigger('reset');
            // reset hidden fields
            $form.find('[type="hidden"]').val('');
        }

        return this;
    };

}(jQuery));