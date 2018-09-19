var socialWallHelper = {

  init: function() {
      $(window).bind('scroll', loadOnScroll);
      $('#modal-body').on('click', '#btn-post-cancel', function() {
        $('#dialog-form-post').modal('toggle');
      })
      $.ajaxSetup({
        beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'))
          }
        }
      })
      // Init post masonry
      $grid = $('.grid').masonry({
        itemSelector: '.grid-item',
        columWidth: '.grid-sizer',
        percentPosition: true,
      });
      // $posts = $('#widget-grid')
      this.initNewPostBtn();
      this.initPost($grid);
  },


  initNewPostBtn: function() {
    // -------------------- create post start --------------------
    // $posts.find('#btn-newpost').click(function() {
    $('.row').on('click', '#btn-newpost', function() {
      form = $('#form-post');
      url = form.attr('action');

      $.ajax({
        type: 'get',
        url: url,
        success: function (data) {
          // console.log(data);
          $('#modal-body').html(data);
          $('#btn-post-create').show();
          $('#btn-post-update').hide();
          $('#dialog-form-post').modal('show');
          socialWallHelper.initFormNew();
        }
      });
    });

    // -------------------- create post end --------------------

  },


  initFormNew: function() {
    $('form').submit(function (e) {

      e.preventDefault();

      url = $(this).attr('api');

      data = $(this).formcontrol().data();
      hasFile = false;

      try {
        $('#id_file')[0].files[0].name;
        form = new FormData();
        $.each(data, function(key, val) {
          form.append(key, val);
        });
        form.append('file', $('#id_file')[0].files[0])
        hasFile = true;
      } catch (e) {}

      if(hasFile) {
        console.log('has file')
        $.ajax({
          type: 'post',
          url: url,
          data: form,
          contentType: false,
          processData: false,
          success: function(data) {
            $item = $(data);
            $grid.prepend($item).masonry('prepended', $item);
            $('#dialog-form-post').modal('hide');
            socialWallHelper.initPost($item);
          }
        });
      } else {
        console.log('no file')
        $.ajax({
          type: 'post',
          url: url,
          data: data,
          success: function(data) {
            $item = $(data);
            $grid.prepend($item).masonry('prepended', $item);
            $('#dialog-form-post').modal('hide');
            socialWallHelper.initPost($item);
          }
        });
      }
    });
  },


  initEditPostBtn: function() {
    $('form').submit(function (e) {
      e.preventDefault();

      id = $(this).attr('data-id');
      url = $(this).attr('api') + id;
      $div = $('#div-' + id)

      data = $(this).formcontrol().data();
      hasFile = false;

      try {
        $('#id_file')[0].files[0].name;
        form = new FormData();
        $.each(data, function(key, val) {
          form.append(key, val);
        });
        form.append('file', $('#id_file')[0].files[0])
        hasFile = true;
      } catch (e) {}

      if(hasFile) {
        console.log('has file')
        $.ajax({
          type: 'patch',
          url: url,
          data: form,
          contentType: false,
          processData: false,
          success: function(data) {
            $item = $(data);
            socialWallHelper.initPost($item);
            $div.find('.post-edit-area').remove();
            $div.find('ul').prepend($item);
            $grid.masonry('layout');
            $('#dialog-form-post').modal('hide');
          }
        });
      } else {
        console.log('no file')
        $.ajax({
          type: 'patch',
          url: url,
          data: data,
          success: function(data) {
            // $item = $(data);
            // $grid.prepend($item).masonry('prepended', $item);
            // $('#dialog-form-post').modal('hide');
            console.log(data)
            $item = $(data);
            socialWallHelper.initPost($item);
            $div.find('.post-edit-area').remove();
            $div.find('.post-update').prepend($item);
            $grid.masonry('layout');
            $('#dialog-form-post').modal('hide');
          }
        });
      }
    });
  },


  initPost: function($item){

    // -------------------- edit post start --------------------
    $item.find('.post-edit').on('click', function() {
      id = $(this).attr('data-id');
      url = $(this).attr('api') + id;
      $.ajax({
        type: 'get',
        url: url,
        success: function(data){
          $('#modal-body').html(data['html']);
          $('#btn-post-create').hide();
          $('#btn-post-update').show();
          $('#dialog-form-post').modal('show');
          socialWallHelper.initEditPostBtn();
        }
      });
    });
    // -------------------- edit post end --------------------

    // -------------------- delete post start --------------------
    $item.find('.post-delete').on('click', function () {
      id = $(this).attr('data-id');
      url = $(this).attr('api');
      $post = $('#span-' + id).parent();
      $.ajax({
        type: 'DELETE',
        url: url + id,
        success: function() {
          $grid.masonry('remove', $post).masonry('layout');
        }
      })
    })
    // -------------------- delete post end --------------------

    // -------------------- hide post start --------------------
    $item.find('.post-hide').on('click', function () {
      id = $(this).attr('data-id');
      $post = $('#span-' + id).parent();
      $grid.masonry('remove', $post).masonry('layout');
    })
    // -------------------- hide post end --------------------

    // -------------------- reply new start --------------------
    $item.find('.form-control.input-xs.socialwall-reply-text').keyup(function (e) {
      if(e.keyCode == 13) {
        id = $(this).attr('data-id');
        url = $(this).attr('api');
        csrftoken = $(this).attr('data-token');
        text = $(this).val();
        $reply = $(this);
        $.ajax({
          type: 'post',
          url: url,
          async: false,
          data: {
            csrfmiddlewaretoken: csrftoken,
            'object_id': id,
            'content': text,
          },
          success: function(data) {
            $item = $(data);
            socialWallHelper.initPost($item);
            $reply.parents(".socialwall-reply").before($item);
            $reply.val('');
            $grid.masonry();
          }
        });
      }
    });

    $item.find('.btn-reply').on('click', function() {
      id = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text').attr('data-id');
      url = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text').attr('api');
      csrftoken = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text').attr('data-token');
      text = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text').val();
      $reply = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text');
      $.ajax({
        type: 'post',
        url: url,
        async: false,
        data: {
          csrfmiddlewaretoken: csrftoken,
          'object_id': id,
          'content': text,
        },
        success: function(data) {
          $item = $(data);
          socialWallHelper.initPost($item);
          $reply.parents(".socialwall-reply").before($item);
          $reply.val('');
          $grid.masonry();
        }
      });
    });
    // -------------------- reply new end --------------------

    // -------------------- reply delete start --------------------
    $item.find('.reply-delete').on('click', function() {
      id = $(this).attr('data-id');
      url = $(this).attr('api');
      $reply = $(this);
      $.ajax({
        type: 'delete',
        url: url + id,
        async: false,
        success: function() {
          $reply.parents('.socialwall-reply').remove();
          $grid.masonry();
        }
      });
    });
    // -------------------- reply delete end --------------------

    // -------------------- reply edit start --------------------
    $item.find('.reply-edit').on('click', function() {
      id = $(this).attr('data-id');
      url = $(this).attr('api');
      $reply = $(this).parents('.socialwall-reply');
      $reply.find('.comment').hide();
      $reply.find('.comment-edit').show();
      origin = $reply.find('#reply-origin').text();
      $edittext = $reply.find('#reply-edit');
      $edittext.val(origin);
      $edittext.focus();

      $edittext.keyup(function(e) {
        if(e.keyCode == 13) {
          data = $edittext.val();
          $.ajax({
            type: 'patch',
            url: url + id,
            async: false,
            data: {
              'content': data,
            },
            success: function(data) {
              $reply.find('.comment').show();
              $reply.find('.comment-edit').hide();
              $reply.html($reply.html());
              $reply.find('#reply-origin').text(data['content']);
              socialWallHelper.initPost($reply);
              return;
            }
          });
        }
      })

      $edittext.focusout(function(e) {
        data = $edittext.val();
        $.ajax({
          type: 'patch',
          url: url + id,
          async: false,
          data: {
            'content': data,
          },
          success: function(data) {
            $reply.find('.comment').show();
            $reply.find('.comment-edit').hide();
            $reply.html($reply.html());
            $reply.find('#reply-origin').text(data['content']);
            socialWallHelper.initPost($reply);
          }
        });
      });
    });
    // -------------------- reply edit end --------------------


    // -------------------- Read More Start --------------------
    // $('.read-more').readMore()
    //
    // $('#row-post').on('click', 'button', function () {
    //   $grid.masonry('layout')
    //   console.log('read more ok, reloaditems ok')
    // })
    // -------------------- Read More End --------------------

  }
}

// var initPost = function($posts) {
//
// }

// -------------------- like thumb start --------------------
// $('.toggle-like').on('click', '.reply-like', function() {
//   $(this).children('i').removeClass('fa-thumbs-o-up')
//   $(this).children('i').addClass('fa-thumbs-up')
//   $(this).removeClass('reply-like')
//   $(this).addClass('reply-like-up')
// })
//
// $('.toggle-like').on('click', '.reply-like-up', function() {
//   $(this).children('i').removeClass('fa-thumbs-up')
//   $(this).children('i').addClass('fa-thumbs-o-up')
//   $(this).removeClass('reply-like-up')
//   $(this).addClass('reply-like')
// })
// -------------------- like thumb start --------------------


// ---------- Infinite Scroll Satrt ----------
var pageNum = 1
var hasNextPage = true

var loadOnScroll = function() {
  if( (($(document).height() - $(window).scrollTop()) / 2) <  $(window).height()){
    $(window).unbind('scroll', loadOnScroll)
    loadItem()
  }
}

var loadItem = function() {
  if (hasNextPage == false) {
    return false
  }
  console.log($(window).scrollTop())
  console.log($(document).height())
  console.log($(window).height())

  pageNum = pageNum + 1
  $.ajax({
    url: '/posts/next/' + pageNum,
    success: function(data) {
      hasNextPage = true
      var $item = $(data)

      $grid.append($item);

      $item.find('.read-more').readMore();
      $grid.masonry('appended', $item);

    },
    error: function(data) {
      hasNextPage = false
    },
    complete: function(data) {
      $(window).bind('scroll', loadOnScroll)
    }
  })
}
// ---------- Infinite Scroll end ----------


// solve the problem ckeditor with modal can't focus on ckeditor's modal like insert img
$.fn.modal.Constructor.prototype.enforceFocus = function () {
var $modalElement = this.$element;
$(document).on('focusin.modal',
    function (e) {
        var $parent = $(e.target.parentNode);
        if ($modalElement[0] !== e.target &&
            !$modalElement.has(e.target).length &&
            !$parent.hasClass('cke_dialog_ui_input_select') &&
            !$parent.hasClass('cke_dialog_ui_input_text')) {
            $modalElement.focus();
        }
    });
};
