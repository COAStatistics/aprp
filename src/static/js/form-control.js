// https://learn.jquery.com/plugins/basic-plugin-creation/

(function ( $ ) {

  var originalVal = $.fn.val;
  $.fn.val = function(value) {
    $this = $(this);

    if (typeof value != 'undefined') {
      // setter invoked, do processing
      return originalVal.apply(this, value);
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

    this.data = function(data){

      data = typeof(data) === 'object' ? data : {};

      // set data (text only)
      Object.keys(data).forEach(function(key, i){
        $form.find('[name="'+ key +'"]').val(data[key]);
      })

      // get data (text only
      return $form.serializeArray().reduce(function(obj, item){
        obj[item.name] = item.value;
        return obj;
      }, {});
    }

    // reset form
    this.reset = function(){
      $form.trigger('reset');
    }

    return this;
  };
}( jQuery ));
