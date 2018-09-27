// https://learn.jquery.com/plugins/basic-plugin-creation/

(function ( $ ) {

  var originalVal = $.fn.val;

  $.fn.val = function(value) {
    $this = $(this);

    if (typeof value != 'undefined') {
      // if is ck editor field
      if($this.hasClass('ckeditorwidget')) {
        var id = $this.attr('id');
        return CKEDITOR.instances[id].setData(value);
      }
      return originalVal.apply(this, [value]);
    }
    else{
      // if is ck editor field
      if($this.hasClass('ckeditorwidget')) {
        var id = $this.attr('id');
        return CKEDITOR.instances[id].getData();
      }
      return originalVal.apply(this);
    }
  };

  $.fn.formcontrol = function() {

    $form = $(this);

    // init dateinput
    if($.ui){
        var dateInputs = $form.find('.dateinput');
        dateInputs.datepicker({
            dateFormat: 'yy-mm-dd',
        });
    }

    // validation
    if(!$form.attr('hasvalidate')){
        $form.find('.form-group').each(function(){
            $(this).append('<div class="help-block" style="display: none;"></div>');
        })
        $form.attr('hasvalidate', 'hasvalidate');
    }else{
        // reset
        $form.find('.help-block').text('').hide();
        $form.find('.form-group').removeClass('has-error');
    }

    this.validate = function(data){
        data = typeof(data) === 'object' ? data : {};
        Object.keys(data).forEach(function(key, i){

            $field = $form.find('#div_id_' + key);

            $field.find('.help-block').html(data[key].join('</br>')).show();

            $field.addClass('has-error');

        })
    }

    this.data = function(data){

      data = typeof(data) === 'object' ? data : {};

      // set data (text only)
      Object.keys(data).forEach(function(key, i){
        $form.find('[name="'+ key +'"]').val(data[key]);
      })

      // get data (text only)
      return $form.serializeArray().reduce(function(obj, item){
        obj[item.name] = item.value;
        return obj;
      }, {});
    }

    // reset form
    this.reset = function(){
      $form.trigger('reset');
      // reset hidden and non-readonly fields
      $form.find('[type="hidden"]').val('');
    }

    return this;
  };

}( jQuery ));
